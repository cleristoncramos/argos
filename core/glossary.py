"""
Glossário educativo do Argos. Os exemplos usam valores HIPOTÉTICOS,
apenas para ilustrar o conceito. Sem dependência de UI.
"""

from dataclasses import dataclass

from core.disclaimers import METRIC_EXPLANATIONS, contains_forbidden_phrase


@dataclass(frozen=True)
class GlossaryEntry:
    key: str
    term: str
    definition: str
    example: str
    limitation: str


def _from_metric(key: str, metric_key: str, term: str, example: str) -> GlossaryEntry:
    metric = METRIC_EXPLANATIONS[metric_key]
    return GlossaryEntry(key, term, metric.description, example, metric.limitation)


GLOSSARY: dict[str, GlossaryEntry] = {
    entry.key: entry
    for entry in [
        _from_metric(
            "retorno", "retorno_total", "Retorno",
            "um ativo que foi de 100 para 120 no período teve retorno total de 20%.",
        ),
        _from_metric(
            "volatilidade", "volatilidade", "Volatilidade",
            "dois ativos com o mesmo retorno podem ter volatilidades diferentes; o mais volátil oscilou mais ao longo do caminho.",
        ),
        _from_metric(
            "drawdown", "drawdown_maximo", "Drawdown",
            "se o preço subiu até 200 e caiu para 150 antes de voltar a subir, o drawdown foi de -25%.",
        ),
        _from_metric(
            "sharpe", "sharpe", "Índice de Sharpe",
            "com a mesma taxa livre de risco, um ativo com Sharpe 1,0 teve melhor relação histórica entre retorno e volatilidade do que outro com Sharpe 0,5.",
        ),
        GlossaryEntry(
            "correlacao", "Correlação",
            "Mede o quanto dois ativos variam juntos, em uma escala de -1 a +1.",
            "perto de +1, tendem a variar na mesma direção; perto de -1, em direções opostas; perto de 0, sem relação linear clara.",
            "Correlação não implica causalidade e pode mudar ao longo do tempo e entre períodos.",
        ),
        GlossaryEntry(
            "media_movel", "Média móvel",
            "Preço médio dos últimos N períodos, calculado a cada data para suavizar oscilações de curto prazo.",
            "uma média móvel de 3 períodos sobre os preços 10, 12 e 14 vale 12.",
            "Reage com atraso às mudanças de preço e depende da janela escolhida.",
        ),
        GlossaryEntry(
            "rsi", "RSI",
            "Índice de Força Relativa: compara a intensidade das altas e das baixas recentes, em escala de 0 a 100.",
            "um RSI de 75 indica que, nos últimos períodos, as altas pesaram bem mais que as baixas.",
            "Os níveis de referência (30 e 70) são convenções; o indicador descreve o passado e não indica compra ou venda.",
        ),
        GlossaryEntry(
            "macd", "MACD",
            "Diferença entre duas médias móveis exponenciais (uma curta e uma longa), usada para descrever mudanças no ritmo da tendência.",
            "quando a média curta fica acima da longa, o MACD é positivo, o que descreve preços recentes acima dos mais antigos.",
            "Herda o atraso das médias móveis; cruzamentos não indicam resultado futuro.",
        ),
        GlossaryEntry(
            "base_100", "Base 100",
            "Normalização que faz todos os ativos partirem do valor 100 na data inicial, permitindo comparar trajetórias de ativos com preços diferentes.",
            "um ativo que termina o período em 150 acumulou +50% desde o início.",
            "Compara apenas a trajetória dentro do período escolhido; mudar a data inicial muda a comparação.",
        ),
        GlossaryEntry(
            "sazonalidade", "Sazonalidade",
            "Padrão de comportamento associado a épocas do calendário, como os meses do ano.",
            "a média dos retornos de todos os meses de janeiro do histórico mostra como janeiro se comportou, em média.",
            "Padrões passados não garantem repetição; amostras curtas geram médias instáveis.",
        ),
    ]
}


def get_glossary_entry(key: str) -> GlossaryEntry | None:
    return GLOSSARY.get(key)


def glossary_terms() -> list[str]:
    return list(GLOSSARY)


def find_forbidden_language() -> list[tuple[str, str]]:
    """Textos do glossário que contenham expressões de recomendação."""
    found = []
    for entry in GLOSSARY.values():
        for text in (entry.definition, entry.example, entry.limitation):
            phrase = contains_forbidden_phrase(text)
            if phrase:
                found.append((text, phrase))
    return found