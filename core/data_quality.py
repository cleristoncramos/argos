"""
Alertas de qualidade e de comportamento atípico dos dados (A4).

Funções puras, sem Streamlit. Avaliam a série DIÁRIA baixada (antes de
agregar pela frequência) e apontam situações que merecem atenção antes da
interpretação. Os alertas não concluem que há erro, fraude ou manipulação:
um mesmo sinal pode vir de um evento real, de um ajuste não aplicado pela
fonte ou de falha no registro.

Os limiares são heurísticas iniciais, calibradas em 24/10/2026 com os 120
ativos do catálogo em 5 anos de dados diários do Yahoo Finance (metodologia
em docs/metodologia_de_calculo.md, seção "Alertas de qualidade dos dados").
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

import numpy as np
import pandas as pd

# Variação diária (em módulo) a partir da qual o dia é sinalizado, por tipo
# de série. Taxas de juros ficam de fora: perto de zero, variações
# percentuais enormes são normais. O VIX é volátil por natureza.
JUMP_THRESHOLDS = {
    "crypto": 0.50,
    "commodity": 0.30,
    "index": 0.15,
    "volatility_index": 1.00,
    "forex": 0.10,
    "stock": 0.25,
}

# Para o salto contar, ele também precisa ser atípico para o próprio ativo:
# pelo menos este múltiplo do desvio típico (MAD robusto) das variações.
ROBUST_Z_MIN = 8.0

# Descontinuidade temporária: em até REVERSAL_WINDOW observações depois do
# salto, o preço desfaz pelo menos 75% do movimento (a distância para o nível
# anterior fica abaixo de 25% do tamanho do salto). Uma correção parcial,
# comum depois de altas fortes, não conta.
REVERSAL_WINDOW = 5
REVERSAL_MAX_REMAINING = 0.25

# Sequência de fechamentos idênticos que merece atenção (criptomoedas são
# negociadas todos os dias, por isso o limite menor).
FLAT_RUN_MIN = {"crypto": 5, "default": 10}

# Proporção de dias sem volume registrado (zero ou ausente) que merece atenção.
ZERO_VOLUME_SHARE = 0.20

# Maior intervalo, em dias corridos, entre duas observações diárias. Feriados
# longos (como o Ano-Novo chinês) chegam a cerca de 11 dias.
MAX_GAP_DAYS = 15

# Histórico total abaixo disto é sinalizado quando a série começa depois do
# início pedido (ou seja, o ativo não tem mais dados na fonte).
SHORT_HISTORY_YEARS = 3

VOLATILITY_INDEXES = {"^VIX"}
RATE_TICKERS = {"^IRX", "^FVX", "^TNX", "^TYX"}
MAX_LISTED_EVENTS = 3


@dataclass(frozen=True)
class QualityAlert:
    level: str      # "warning" ou "info"
    code: str       # identificador estável (usado em testes e registros)
    title: str
    text: str


def series_kind(ticker: str) -> str:
    """Tipo de série pelo ticker (vale também para o modo "Digitar ticker")."""
    t = str(ticker or "").strip().upper()
    if t in RATE_TICKERS:
        return "rate"
    if t in VOLATILITY_INDEXES:
        return "volatility_index"
    if t.endswith("-USD"):
        return "crypto"
    if t.endswith("=X"):
        return "forex"
    if t.endswith("=F"):
        return "commodity"
    if t.startswith("^") or t.endswith(".SS"):
        return "index"
    return "stock"


def volume_is_relevant(ticker: str) -> bool:
    """Índices, taxas e câmbio não têm volume próprio na fonte."""
    return series_kind(ticker) not in {"rate", "volatility_index", "forex", "index"}


def _fmt_date(value) -> str:
    return pd.Timestamp(value).strftime("%d/%m/%Y")


def _fmt_pct(value: float) -> str:
    return f"{value * 100:+,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    data = df[[c for c in ("Date", "Close", "Volume") if c in df.columns]].copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data["Close"] = pd.to_numeric(data["Close"], errors="coerce")
    return data.dropna(subset=["Date", "Close"]).sort_values("Date").reset_index(drop=True)


def find_jumps(data: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """
    Dias com variação atípica: acima do limiar do tipo de série e acima de
    ROBUST_Z_MIN desvios típicos do próprio ativo. Coluna `Reversal` indica
    se o preço desfez o movimento em até REVERSAL_WINDOW observações.
    """
    columns = ["Date", "Change", "Reversal", "Reversal_Date"]
    kind = series_kind(ticker)
    if kind == "rate" or len(data) < 3:
        return pd.DataFrame(columns=columns)

    close = data["Close"].to_numpy(dtype=float)
    previous = close[:-1]
    valid = previous > 0
    changes = np.full(len(close), np.nan)
    changes[1:][valid] = close[1:][valid] / previous[valid] - 1

    finite = changes[np.isfinite(changes)]
    median = np.median(finite)
    mad = np.median(np.abs(finite - median)) * 1.4826
    threshold = JUMP_THRESHOLDS[kind]

    rows = []
    for i in np.flatnonzero(np.isfinite(changes)):
        change = changes[i]
        robust_z = abs(change - median) / mad if mad > 0 else np.inf
        if abs(change) < threshold or robust_z < ROBUST_Z_MIN:
            continue
        before = close[i - 1]
        reversal_date = None
        for j in range(i + 1, min(i + 1 + REVERSAL_WINDOW, len(close))):
            if abs(close[j] / before - 1) <= REVERSAL_MAX_REMAINING * abs(change):
                reversal_date = data["Date"].iloc[j]
                break
        rows.append({
            "Date": data["Date"].iloc[i],
            "Change": float(change),
            "Reversal": reversal_date is not None,
            "Reversal_Date": reversal_date,
        })

    result = pd.DataFrame(rows, columns=columns)
    # O movimento de volta de uma descontinuidade faz parte dela: não conta
    # de novo como salto isolado.
    closing = set(result.loc[result["Reversal"], "Reversal_Date"])
    return result[~result["Date"].isin(closing)].reset_index(drop=True)


def longest_flat_run(data: pd.DataFrame) -> tuple[int, Optional[pd.Timestamp], Optional[pd.Timestamp]]:
    """Maior sequência de fechamentos idênticos: (tamanho, início, fim)."""
    if data.empty:
        return 0, None, None
    same = data["Close"].diff().eq(0).to_numpy()
    best, best_end, current = 1, 0, 1
    for i in range(1, len(same)):
        current = current + 1 if same[i] else 1
        if current > best:
            best, best_end = current, i
    start = best_end - best + 1
    return best, data["Date"].iloc[start], data["Date"].iloc[best_end]


def assess_data_quality(
    df: pd.DataFrame,
    ticker: str,
    requested_start: Optional[date] = None,
) -> list[QualityAlert]:
    """
    Alertas da série diária `df` (colunas Date, Close e, se houver, Volume).
    `requested_start`: início pedido na interface; com ele, o histórico curto
    só é sinalizado quando a fonte não tem dados desde essa data.
    """
    if df is None or df.empty or "Close" not in df.columns:
        return []

    data = _clean(df)
    if len(data) < 2:
        return []

    alerts: list[QualityAlert] = []
    kind = series_kind(ticker)

    def caution(count: int) -> str:
        period = "esse período" if count == 1 else "esses períodos"
        return f"Verifique antes de interpretar os resultados que incluem {period}."

    def more(count: int) -> str:
        return f" e mais {count - MAX_LISTED_EVENTS}" if count > MAX_LISTED_EVENTS else ""

    jumps = find_jumps(data, ticker)
    reversals = jumps[jumps["Reversal"]]
    if not reversals.empty:
        listed = "; ".join(
            f"{_fmt_date(row.Date)} ({_fmt_pct(row.Change)}), de volta ao nível anterior em "
            f"{_fmt_date(row.Reversal_Date)}"
            for row in reversals.head(MAX_LISTED_EVENTS).itertuples()
        )
        alerts.append(QualityAlert(
            "warning",
            "temporary_discontinuity",
            "Mudança de patamar que se desfaz em poucos dias",
            f"O preço mudou bruscamente de nível e voltou ao patamar anterior em até "
            f"{REVERSAL_WINDOW} observações: {listed}{more(len(reversals))}. Esse "
            f"comportamento pode vir de um ajuste não aplicado pela fonte (como um "
            f"desdobramento), de um registro incorreto ou de um evento real. "
            f"{caution(len(reversals))}",
        ))

    others = jumps[~jumps["Reversal"]]
    if not others.empty:
        listed = "; ".join(
            f"{_fmt_date(row.Date)} ({_fmt_pct(row.Change)})"
            for row in others.reindex(others["Change"].abs().sort_values(ascending=False).index)
            .head(MAX_LISTED_EVENTS).itertuples()
        )
        alerts.append(QualityAlert(
            "info",
            "atypical_jump",
            "Variações diárias muito acima do habitual",
            f"{len(others)} dia(s) com variação acima de "
            f"{JUMP_THRESHOLDS[kind] * 100:.0f}% e muito fora do comportamento típico do "
            f"ativo: {listed}{more(len(others))}. Pode refletir um evento real (resultado, notícia, "
            f"mudança relevante no projeto ou na empresa), baixa negociação ou falha da "
            f"fonte; os dados de preço, sozinhos, não indicam qual. Esses dias pesam muito "
            f"em médias, volatilidade e quedas máximas.",
        ))

    run, run_start, run_end = longest_flat_run(data)
    if run >= FLAT_RUN_MIN.get(kind, FLAT_RUN_MIN["default"]):
        alerts.append(QualityAlert(
            "info",
            "flat_prices",
            "Preço sem variação por vários dias seguidos",
            f"O fechamento se repetiu em {run} observações seguidas, de "
            f"{_fmt_date(run_start)} a {_fmt_date(run_end)}. Pode indicar baixa "
            f"negociação, câmbio administrado ou dado não atualizado pela fonte.",
        ))

    if "Volume" in data.columns and volume_is_relevant(ticker):
        volume = pd.to_numeric(data["Volume"], errors="coerce").fillna(0)
        share = float((volume <= 0).mean())
        if share > ZERO_VOLUME_SHARE:
            alerts.append(QualityAlert(
                "info",
                "missing_volume",
                "Muitos dias sem volume registrado",
                f"{share * 100:.0f}% dos dias não têm volume negociado registrado na fonte. "
                f"Pode indicar pouca negociação ou ausência do dado (comum em alguns "
                f"contratos futuros); preços desses dias podem não refletir negócios efetivos.",
            ))

    gaps = data["Date"].diff().dt.days
    if gaps.max() > MAX_GAP_DAYS:
        position = int(gaps.idxmax())
        alerts.append(QualityAlert(
            "info",
            "long_gap",
            "Intervalo longo sem dados",
            f"Não há observações entre {_fmt_date(data['Date'].iloc[position - 1])} e "
            f"{_fmt_date(data['Date'].iloc[position])} ({int(gaps.max())} dias corridos). "
            f"Pode ser suspensão de negociação ou falha da fonte; a variação desse "
            f"intervalo aparece concentrada em um único período.",
        ))

    first = data["Date"].iloc[0]
    years = (data["Date"].iloc[-1] - first).days / 365.25
    starts_late = requested_start is None or first.date() > requested_start
    if starts_late and years < SHORT_HISTORY_YEARS:
        alerts.append(QualityAlert(
            "info",
            "short_history",
            "Histórico curto na fonte",
            f"Há cerca de {f'{years:.1f}'.replace('.', ',')} ano(s) de dados (desde "
            f"{_fmt_date(first)}). Análises que dependem de vários anos, como padrões "
            f"sazonais e janelas longas, ficam com amostra reduzida.",
        ))

    return alerts


def quality_summary(alerts: list[QualityAlert]) -> str:
    """Texto curto para os detalhes do processamento."""
    if not alerts:
        return "Nenhum alerta nas verificações automáticas"
    return f"{len(alerts)} alerta(s): " + "; ".join(alert.title.lower() for alert in alerts)
