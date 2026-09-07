import numpy as np
import pandas as pd

def annual_to_periodic_rate(
    annual_rate: float,
    annualization_factor: float,
) -> float:
    """
    Converte uma taxa anual efetiva em taxa equivalente por período.

    Exemplos:
    - 10% ao ano, com 12 períodos: taxa mensal equivalente;
    - 10% ao ano, com 252 períodos: taxa diária equivalente.

    Fórmula:
        (1 + taxa_anual) ** (1 / períodos_ano) - 1
    """
    if annualization_factor <= 0:
        raise ValueError(
            "O fator de anualização deve ser maior que zero."
        )

    if annual_rate <= -1:
        raise ValueError(
            "A taxa anual deve ser maior que -100%."
        )

    return float(
        (1 + annual_rate) ** (1 / annualization_factor) - 1
    )

def calculate_sharpe_ratio(
    returns: pd.Series,
    annual_risk_free_rate: float = 0.0,
    annualization_factor: float = 252.0,
) -> float:
    """
    Calcula o Índice de Sharpe anualizado.

    Parâmetros:
    - returns: série de retornos simples por período, em decimal;
    - annual_risk_free_rate: taxa livre de risco anual, em decimal;
      exemplo: 0.10 representa 10% ao ano;
    - annualization_factor: número de períodos no ano.

    Retorna:
    - Sharpe anualizado; ou np.nan quando não houver dados suficientes
      ou não houver variabilidade nos retornos.

    Metodologia:
    1. Converte a taxa livre de risco anual para a frequência da série.
    2. Calcula retorno excedente por período.
    3. Divide retorno excedente médio pelo desvio-padrão amostral.
    4. Multiplica por raiz quadrada do fator de anualização.
    """
    valid_returns = pd.to_numeric(
        returns,
        errors="coerce",
    ).dropna()

    if len(valid_returns) < 2:
        return np.nan

    periodic_risk_free_rate = annual_to_periodic_rate(
        annual_risk_free_rate,
        annualization_factor,
    )

    excess_returns = valid_returns - periodic_risk_free_rate

    excess_std = excess_returns.std(ddof=1)

    if pd.isna(excess_std) or excess_std == 0:
        return np.nan

    periodic_sharpe = excess_returns.mean() / excess_std

    return float(
        periodic_sharpe * np.sqrt(annualization_factor)
    )

def calculate_volatility(
    returns: pd.Series,
    annualization_factor: float = 252.0,
) -> float:
    """
    Calcula a volatilidade anualizada da série de retornos.

    Para mercados de ações, 252 é uma aproximação comum para dias úteis.
    Para criptoativos, esse valor pode ser ajustado para 365, pois o mercado
    opera todos os dias. O fator deve ser configurável e não usado como regra
    universal para todos os mercados.
    """
    if returns.empty:
        return 0.0

    std = returns.std(ddof=1)
    if pd.isna(std) or std == 0:
        return 0.0

    return float(std * np.sqrt(annualization_factor))


def calculate_positive_percentage(
    returns: pd.Series,
) -> float:
    """
    Retorna a proporção de retornos positivos em formato decimal.

    Exemplos:
    - 0.4545 representa 45,45% de períodos positivos;
    - 0.0 representa ausência de períodos positivos;
    - 1.0 representa todos os períodos positivos.

    A conversão para texto percentual deve ocorrer somente na interface,
    por meio de format_return_pct().
    """
    if returns.empty:
        return 0.0

    return float((returns > 0).mean())


def build_risk_summary(
    df: pd.DataFrame,
    value_col: str = "Value",
    annualization_factor: float = 252.0,
    annual_risk_free_rate: float = 0.0,
) -> dict:
    """
    Monta um resumo de risco e retorno para uma série de preços.

    Convenções:
    - Retornos, volatilidade, drawdown e percentual positivo são
      armazenados internamente em formato decimal.
    - Sharpe é uma razão adimensional anualizada.
    - annual_risk_free_rate deve ser informada como taxa anual decimal:
      0.10 representa 10% ao ano.
    """
    if df.empty or value_col not in df.columns:
        raise ValueError(
            f"A coluna '{value_col}' não existe no DataFrame."
        )

    values = pd.to_numeric(
        df[value_col],
        errors="coerce",
    )

    valid_values = values.dropna()

    if valid_values.empty:
        raise ValueError(
            f"A coluna '{value_col}' não contém valores válidos."
        )

    if (valid_values <= 0).any():
        raise ValueError(
            f"A coluna '{value_col}' deve conter valores maiores que zero."
        )

    returns = valid_values.pct_change().dropna()

    first_value = valid_values.iloc[0]
    last_value = valid_values.iloc[-1]

    total_return = float(
        (last_value / first_value) - 1
    )

    mean_return = (
        float(returns.mean())
        if not returns.empty
        else 0.0
    )

    volatility = calculate_volatility(
        returns,
        annualization_factor,
    )

    drawdown_df = calculate_drawdown(
        pd.DataFrame(
            {
                value_col: valid_values,
            }
        ),
        value_col=value_col,
    )

    max_drawdown = get_max_drawdown(drawdown_df)

    positive_percentage = calculate_positive_percentage(
        returns
    )

    sharpe = calculate_sharpe_ratio(
        returns=returns,
        annual_risk_free_rate=annual_risk_free_rate,
        annualization_factor=annualization_factor,
    )

    return {
        "Retorno total": total_return,
        "Retorno médio": mean_return,
        "Volatilidade": volatility,
        "Drawdown máximo": max_drawdown,
        "Percentual positivo": positive_percentage,
        "Sharpe": sharpe,
    }


def calculate_drawdown(
    df: pd.DataFrame,
    value_col: str = "Value",
) -> pd.DataFrame:
    """
    Calcula o pico acumulado e o drawdown de uma série de preços.

    Running_Peak:
        Maior valor observado até cada data.

    Drawdown:
        Queda percentual do valor atual em relação ao maior pico
        observado anteriormente ou na própria data.

    Exemplo:
        Preços: 100, 120, 90
        Pico:   100, 120, 120
        DD:     0%,  0%, -25%
    """
    if value_col not in df.columns:
        raise ValueError(
            f"A coluna '{value_col}' não existe no DataFrame."
        )

    if df.empty:
        result = df.copy()
        result["Running_Peak"] = pd.Series(dtype="float64")
        result["Drawdown"] = pd.Series(dtype="float64")
        return result

    result = df.copy()

    # Garante que preços inválidos não gerem divisão por zero
    values = pd.to_numeric(
        result[value_col],
        errors="coerce",
    )

    if values.isna().any():
        raise ValueError(
            f"A coluna '{value_col}' possui valores não numéricos ou ausentes."
        )

    if (values <= 0).any():
        raise ValueError(
            f"A coluna '{value_col}' deve conter valores maiores que zero."
        )

    # Maior preço alcançado até cada observação
    result["Running_Peak"] = values.cummax()

    # Queda percentual em relação ao maior pico anterior
    result["Drawdown"] = (
        values / result["Running_Peak"] - 1
    )

    return result


def get_max_drawdown(
    df: pd.DataFrame,
    drawdown_col: str = "Drawdown",
) -> float | None:
    """
    Retorna o maior drawdown da série.

    O resultado é negativo ou zero:
    - 0.0: não houve queda em relação a pico anterior;
    - -0.25: queda máxima de 25%.
    """
    if drawdown_col not in df.columns:
        raise ValueError(
            f"A coluna '{drawdown_col}' não existe no DataFrame."
        )

    if df.empty or df[drawdown_col].dropna().empty:
        return None

    return float(df[drawdown_col].min())