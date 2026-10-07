"""
Documentação central dos indicadores técnicos da primeira versão do Argos.
Define O QUE cada indicador mede, como é calculado e suas limitações.
Sem dependência de UI.
"""

from dataclasses import dataclass, field

from core.disclaimers import contains_forbidden_phrase


@dataclass(frozen=True)
class IndicatorDoc:
    key: str
    name: str
    category: str  # Tendência | Momentum | Volatilidade | Volume
    measures: str
    formula: str
    parameters: dict = field(default_factory=dict)
    limitations: str = ""
    feature_candidate: bool = True  # pode virar variável de modelos futuros


INDICATOR_DOCS: dict[str, IndicatorDoc] = {
    "sma": IndicatorDoc(
        key="sma",
        name="Média Móvel Simples (SMA)",
        category="Tendência",
        measures="O preço médio de fechamento nos últimos N períodos, suavizando oscilações de curto prazo.",
        formula="SMA_t = (C_t + C_{t-1} + ... + C_{t-N+1}) / N",
        parameters={"janela curta": "20 (padrão)", "janela longa": "50 (padrão)"},
        limitations="Reage com atraso às mudanças de preço e dá o mesmo peso a todos os períodos da janela.",
    ),
    "ema": IndicatorDoc(
        key="ema",
        name="Média Móvel Exponencial (EMA)",
        category="Tendência",
        measures="Uma média que dá mais peso aos preços recentes do que aos antigos.",
        formula="EMA_t = α·C_t + (1-α)·EMA_{t-1}, com α = 2/(N+1)",
        parameters={"janela curta": "12 (padrão)", "janela longa": "26 (padrão)"},
        limitations=(
            "Reage mais rápido que a SMA, mas é mais sensível a ruídos de curto prazo. "
            "Os primeiros valores da série dependem do ponto inicial e são menos "
            "confiáveis (período de aquecimento)."
        ),
    ),
    "bollinger": IndicatorDoc(
        key="bollinger",
        name="Bandas de Bollinger",
        category="Volatilidade",
        measures="A dispersão dos preços em torno de uma média móvel, em faixas de desvios-padrão.",
        formula="Banda central = SMA_N; bandas = SMA_N ± k·desvio-padrão amostral_N (ddof = 1)",
        parameters={"janela": "20 (padrão)", "k (desvios-padrão)": "2,0 (padrão)"},
        limitations="Preços fora das bandas descrevem afastamento estatístico recente, não preveem reversão ou continuidade.",
    ),
    "rsi": IndicatorDoc(
        key="rsi",
        name="Índice de Força Relativa (RSI)",
        category="Momentum",
        measures="A intensidade relativa das altas frente às baixas recentes, em escala de 0 a 100.",
        formula=(
            "RSI = 100 - 100/(1 + RS), RS = média de ganhos / média de perdas em N períodos, "
            "ambas com suavização de Wilder (α = 1/N)"
        ),
        parameters={"janela": "14 (padrão)", "níveis de referência": "30 e 70 (padrão)"},
        limitations=(
            "Os níveis de referência são convenções; em tendências fortes o RSI pode "
            "permanecer extremo por longos períodos. Em séries sem nenhuma variação o "
            "RSI é indefinido. A média é inicializada no primeiro valor, então os "
            "primeiros pontos podem diferir levemente de outras plataformas."
        ),
    ),
    "macd": IndicatorDoc(
        key="macd",
        name="MACD",
        category="Momentum",
        measures="A diferença entre duas médias exponenciais, indicando mudanças de ritmo da tendência.",
        formula="MACD = EMA_curta - EMA_longa; Sinal = EMA_9(MACD); Histograma = MACD - Sinal",
        parameters={"EMA curta": "12", "EMA longa": "26", "sinal": "9"},
        limitations="É derivado de médias móveis, portanto herda o atraso delas; cruzamentos não indicam resultado futuro.",
    ),
    "atr": IndicatorDoc(
        key="atr",
        name="Amplitude Média Verdadeira (ATR)",
        category="Volatilidade",
        measures="A amplitude média de variação do preço por período, incluindo lacunas entre fechamento e abertura seguinte.",
        formula="TR_t = max(H-L, |H-C_{t-1}|, |L-C_{t-1}|); ATR_t = suavização de Wilder (α = 1/N) de TR",
        parameters={"janela": "14 (padrão)"},
        limitations="Mede magnitude, não direção; é expresso na unidade do ativo, então não compara ativos de preços diferentes.",
    ),
    "volatilidade_movel": IndicatorDoc(
        key="volatilidade_movel",
        name="Volatilidade Móvel",
        category="Volatilidade",
        measures="O desvio-padrão dos retornos simples nos últimos N períodos, anualizado pela frequência escolhida.",
        formula="Vol_t = desvio-padrão(r_{t-N+1..t}) × √(fator de anualização), r_t = C_t/C_{t-1} - 1",
        parameters={"janela": "20 (padrão)", "fator de anualização": "depende da frequência"},
        limitations="Depende da janela escolhida e assume que retornos passados descrevem a dispersão atual; não projeta o futuro.",
    ),
    "volume": IndicatorDoc(
        key="volume",
        name="Volume",
        category="Volume",
        measures="A quantidade negociada do ativo em cada período, uma aproximação da liquidez.",
        formula="Soma das quantidades negociadas no período (agregada na frequência escolhida)",
        parameters={},
        limitations="Nem todos os ativos têm volume confiável (ex.: índices e câmbio); as fontes podem diferir entre mercados.",
        feature_candidate=False,
    ),
}


def get_indicator_doc(key: str) -> IndicatorDoc | None:
    return INDICATOR_DOCS.get(key)


def all_doc_texts() -> list[str]:
    """Todos os textos exibíveis, para teste automático de linguagem neutra."""
    texts = []
    for doc in INDICATOR_DOCS.values():
        texts += [doc.name, doc.measures, doc.formula, doc.limitations, *doc.parameters.values()]
    return texts


def find_forbidden_language() -> list[tuple[str, str]]:
    return [
        (text, phrase)
        for text in all_doc_texts()
        if (phrase := contains_forbidden_phrase(text))
    ]