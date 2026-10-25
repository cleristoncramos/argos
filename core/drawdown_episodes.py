"""
Episódios de queda e tempo de recuperação (A7).

Funções puras, sem Streamlit. Um episódio começa em um pico (o maior valor
até então, seguido de queda), passa pelo fundo (o menor valor antes de
voltar ao pico) e termina na recuperação: a primeira observação em que o
valor volta a ser igual ou maior que o do pico. Se isso não acontece até a
última observação, o episódio fica "não recuperado até a última observação
disponível", sem nenhuma estimativa de quando ocorreria.

Unidade das durações: dias corridos entre as datas das observações da
série recebida. Na página Risco e Retorno, a série está na frequência
escolhida (por exemplo, fechamentos mensais), então as datas e durações
têm a resolução dessa frequência (detalhes em
docs/metodologia_de_calculo.md, seção 4.1).
"""

import pandas as pd

DEFAULT_TOP = 3

COLUMNS = [
    "Pico", "Valor no pico", "Fundo", "Valor no fundo", "Queda",
    "Recuperação", "Recuperada", "Dias até o fundo", "Dias do fundo à recuperação",
    "Dias em queda", "Períodos em queda",
]


def drawdown_episodes(
    df: pd.DataFrame,
    value_col: str = "Value",
    date_col: str = "Date",
) -> pd.DataFrame:
    """
    Todos os episódios de queda, em ordem cronológica, com as colunas de
    `COLUMNS`. `Queda` em fração negativa (-0,25 = -25%). Em episódios não
    recuperados, `Recuperação` e `Dias do fundo à recuperação` ficam vazios e
    `Dias em queda` / `Períodos em queda` contam até a última observação.
    """
    if df is None or df.empty or value_col not in df.columns or date_col not in df.columns:
        return pd.DataFrame(columns=COLUMNS)

    data = pd.DataFrame({
        "Date": pd.to_datetime(df[date_col], errors="coerce"),
        "Value": pd.to_numeric(df[value_col], errors="coerce"),
    }).dropna()
    data = data[data["Value"] > 0].sort_values("Date").reset_index(drop=True)
    if len(data) < 2:
        return pd.DataFrame(columns=COLUMNS)

    values = data["Value"].to_numpy(dtype=float)
    dates = data["Date"]
    last = len(values) - 1
    rows = []
    peak = 0

    i = 1
    while i <= last:
        if values[i] >= values[peak]:
            peak = i
            i += 1
            continue

        # Abaixo do pico: procura a recuperação e o fundo do episódio.
        recovery = None
        trough = i
        j = i
        while j <= last:
            if values[j] >= values[peak]:
                recovery = j
                break
            if values[j] < values[trough]:
                trough = j
            j += 1

        end = recovery if recovery is not None else last
        rows.append({
            "Pico": dates.iloc[peak],
            "Valor no pico": values[peak],
            "Fundo": dates.iloc[trough],
            "Valor no fundo": values[trough],
            "Queda": values[trough] / values[peak] - 1,
            "Recuperação": dates.iloc[recovery] if recovery is not None else pd.NaT,
            "Recuperada": recovery is not None,
            "Dias até o fundo": (dates.iloc[trough] - dates.iloc[peak]).days,
            "Dias do fundo à recuperação": (
                (dates.iloc[recovery] - dates.iloc[trough]).days if recovery is not None else None
            ),
            "Dias em queda": (dates.iloc[end] - dates.iloc[peak]).days,
            "Períodos em queda": end - peak,
        })

        if recovery is None:
            break
        peak = recovery
        i = recovery + 1

    return pd.DataFrame(rows, columns=COLUMNS)


def largest_drawdowns(
    df: pd.DataFrame,
    top: int = DEFAULT_TOP,
    value_col: str = "Value",
    date_col: str = "Date",
) -> pd.DataFrame:
    """Os `top` episódios mais profundos, do maior para o menor."""
    episodes = drawdown_episodes(df, value_col, date_col)
    if episodes.empty:
        return episodes
    return episodes.sort_values("Queda", kind="stable").head(top).reset_index(drop=True)
