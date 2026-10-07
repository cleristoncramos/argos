"""
Simulação histórica de aportes.

Responde apenas à pergunta
"o que teria acontecido historicamente com um valor hipotético?".

Não é previsão nem recomendação. Premissas simplificadoras:
- usa o preço de fechamento da série informada (retorno de preço);
- não considera dividendos, taxas, impostos, spread, câmbio ou inflação;
- permite frações de unidade;
- o aporte é executado ao preço da observação em que ocorre.
"""

from typing import Dict, List

import numpy as np
import pandas as pd


SIMULATION_DISCLAIMER = (
    "Simulação histórica com valor hipotético. Mostra o que teria ocorrido "
    "com os preços do período selecionado; não é previsão, não é "
    "recomendação de investimento e não considera dividendos, taxas, "
    "impostos, câmbio, inflação nem o perfil, a renda ou os objetivos de "
    "quem usa a ferramenta."
)

# Séries que representam taxas ou indicadores não negociáveis como ativo.
NON_SIMULABLE_TICKERS = {
    "^IRX": "é uma taxa de juros (yield), não um preço de ativo",
    "^FVX": "é uma taxa de juros (yield), não um preço de ativo",
    "^TNX": "é uma taxa de juros (yield), não um preço de ativo",
    "^TYX": "é uma taxa de juros (yield), não um preço de ativo",
    "^VIX": "é um índice de volatilidade esperada, não um preço de ativo",
}


def non_simulable_reason(symbol: str) -> str | None:
    """Retorna o motivo pelo qual o ticker não pode ser simulado, ou None."""
    return NON_SIMULABLE_TICKERS.get(str(symbol).strip().upper())


def simulation_notes(symbol: str) -> List[str]:
    """Avisos específicos do tipo de ativo, em linguagem neutra."""
    ticker = str(symbol).strip().upper()
    notes: List[str] = []

    if ticker.startswith("^"):
        notes.append(
            "Índices não são negociáveis diretamente; a simulação supõe "
            "uma carteira hipotética que acompanhe o índice, sem custos "
            "nem dividendos."
        )
    if ticker.endswith("=F"):
        notes.append(
            "Contratos futuros têm vencimento e rolagem; a série contínua "
            "usada aqui não representa o resultado de manter um contrato."
        )
    if ticker.endswith("=X"):
        notes.append(
            "Pares de moedas não consideram diferencial de juros entre as "
            "moedas nem custos de conversão."
        )

    return notes


def _prepare_prices(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Valida e padroniza a série: colunas Date e Price, ordenada e > 0."""
    if df is None or df.empty:
        raise ValueError("Não há dados para simular.")

    missing = [c for c in ("Date", value_col) if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    data = df[["Date", value_col]].copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")
    data = data.dropna().sort_values("Date").reset_index(drop=True)

    if len(data) < 2:
        raise ValueError("São necessárias ao menos 2 observações válidas.")

    if (data[value_col] <= 0).any():
        raise ValueError(
            f"A coluna '{value_col}' deve conter valores maiores que zero."
        )

    return data.rename(columns={value_col: "Price"})


def _validate_amount(amount: float) -> None:
    if not np.isfinite(amount) or amount <= 0:
        raise ValueError("O valor do aporte deve ser maior que zero.")


def _validate_every(every: int) -> None:
    if int(every) != every or every < 1:
        raise ValueError("O intervalo entre aportes deve ser inteiro e >= 1.")


def _build_path(data: pd.DataFrame, contribution: np.ndarray) -> pd.DataFrame:
    """Monta a trajetória a partir dos aportes por observação."""
    result = data.copy()
    result["Contribution"] = contribution
    result["Invested"] = result["Contribution"].cumsum()
    result["Units"] = (result["Contribution"] / result["Price"]).cumsum()
    result["Portfolio_Value"] = result["Units"] * result["Price"]
    result["Result"] = result["Portfolio_Value"] - result["Invested"]
    result["Return"] = result["Portfolio_Value"] / result["Invested"] - 1
    return result


def simulate_lump_sum(
    df: pd.DataFrame,
    amount: float,
    value_col: str = "Value",
) -> pd.DataFrame:
    """Aporte único no primeiro preço da série."""
    _validate_amount(amount)
    data = _prepare_prices(df, value_col)

    contribution = np.zeros(len(data))
    contribution[0] = float(amount)

    return _build_path(data, contribution)


def simulate_periodic(
    df: pd.DataFrame,
    amount: float,
    every: int = 1,
    value_col: str = "Value",
) -> pd.DataFrame:
    """
    Aportes iguais a cada `every` observações, começando na primeira.

    Com frequência mensal e every=1, equivale a um aporte por mês.
    """
    _validate_amount(amount)
    _validate_every(every)
    data = _prepare_prices(df, value_col)

    contribution = np.zeros(len(data))
    contribution[::int(every)] = float(amount)

    return _build_path(data, contribution)


def compare_strategies(
    df: pd.DataFrame,
    periodic_amount: float,
    every: int = 1,
    value_col: str = "Value",
) -> Dict[str, pd.DataFrame]:
    """
    Compara aportes periódicos com um aporte único de MESMO total investido,
    feito no início da série.
    """
    periodic = simulate_periodic(df, periodic_amount, every, value_col)
    total_invested = float(periodic["Invested"].iloc[-1])
    lump = simulate_lump_sum(df, total_invested, value_col)

    return {"periodic": periodic, "lump_sum": lump}


def summarize_simulation(path: pd.DataFrame) -> Dict[str, float]:
    """Resume uma trajetória. Retornos em decimal (0.10 = 10%)."""
    last = path.iloc[-1]

    return {
        "Total investido": float(last["Invested"]),
        "Valor final": float(last["Portfolio_Value"]),
        "Resultado": float(last["Result"]),
        "Retorno sobre o investido": float(last["Return"]),
        "Menor retorno no caminho": float(path["Return"].min()),
        "Número de aportes": int((path["Contribution"] > 0).sum()),
    }


def rolling_window_outcomes(
    df: pd.DataFrame,
    horizon: int,
    every: int = 1,
    value_col: str = "Value",
) -> pd.DataFrame:
    """
    Resultado de cada janela histórica de `horizon` períodos.

    Para cada data inicial possível, calcula o retorno do aporte único e o
    do aporte periódico (mesma regra de `simulate_periodic`) até
    `horizon` observações depois. Os retornos são sobre o total investido.
    """
    _validate_every(every)
    data = _prepare_prices(df, value_col)

    if int(horizon) != horizon or horizon < 1:
        raise ValueError("O horizonte deve ser inteiro e >= 1.")

    n = len(data)
    if horizon >= n:
        raise ValueError(
            "O horizonte deve ser menor que o número de observações."
        )

    prices = data["Price"].to_numpy(dtype=float)
    dates = data["Date"].to_numpy()
    rows = []

    for start in range(n - horizon):
        end = start + horizon
        idx = np.arange(start, end + 1, int(every))
        units = float(np.sum(1.0 / prices[idx]))
        invested = float(len(idx))
        periodic_return = units * prices[end] / invested - 1

        rows.append(
            {
                "Start_Date": dates[start],
                "End_Date": dates[end],
                "Lump_Return": prices[end] / prices[start] - 1,
                "Periodic_Return": periodic_return,
                "Contributions": int(len(idx)),
            }
        )

    return pd.DataFrame(rows)


def summarize_windows(
    outcomes: pd.DataFrame,
    column: str = "Lump_Return",
) -> Dict[str, object]:
    """
    Resume a distribuição das janelas: pior, mediana, melhor e % positivas.

    Não rotula nenhuma janela como "boa" ou "ruim" para investir; apenas
    descreve o que ocorreu no histórico.
    """
    if outcomes is None or outcomes.empty or column not in outcomes.columns:
        raise ValueError("Não há janelas para resumir.")

    values = outcomes[column]
    worst_pos = values.idxmin()
    best_pos = values.idxmax()

    return {
        "Janelas analisadas": int(len(values)),
        "Pior janela": float(values.min()),
        "Início da pior janela": outcomes.loc[worst_pos, "Start_Date"],
        "Mediana": float(values.median()),
        "Melhor janela": float(values.max()),
        "Início da melhor janela": outcomes.loc[best_pos, "Start_Date"],
        "Janelas com retorno positivo": float((values > 0).mean()),
    }