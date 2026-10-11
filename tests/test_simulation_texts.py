import ast
import re
from pathlib import Path

from core.simulation import SIMULATION_DISCLAIMER, non_simulable_reason
from core import simulation_texts as texts

PAGE = Path(__file__).resolve().parent.parent / "app" / "views" / "simulacao_aportes.py"

MANDATORY = (
    "Esta é uma simulação histórica hipotética. Ela mostra como um valor teria "
    "evoluído no período selecionado, sem representar previsão, recomendação "
    "ou garantia de resultado futuro."
)

FORBIDDEN_PATTERNS = [
    r"\bmelhor\b", r"\bpior\b", r"\bvai ocorrer\b", r"\bvai subir\b",
    r"\bvai cair\b", r"\bquanto investir\b", r"\binvista\b", r"\bcompre\b",
    r"\bvenda\b", r"\brecomendamos\b", r"\bgarante\b", r"\boportunidade\b",
]


def page_strings():
    """Textos literais da página, sem as chaves internas do resumo do core
    (ex.: "Pior janela"), que nunca aparecem para o usuário."""
    internal_keys = set(texts.SIMULATION_WINDOW_LABELS)
    tree = ast.parse(PAGE.read_text(encoding="utf-8"))
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value not in internal_keys
    ]


def assert_neutral(text):
    lowered = text.lower()
    for pattern in FORBIDDEN_PATTERNS:
        assert not re.search(pattern, lowered), (pattern, text)


# 4.1 texto obrigatório, palavra por palavra, e presente na página
def test_mandatory_text_is_exact_and_used_by_the_page():
    assert texts.SIMULATION_MANDATORY_TEXT == MANDATORY
    source = PAGE.read_text(encoding="utf-8")
    assert "SIMULATION_MANDATORY_TEXT" in source
    assert "from core.simulation_texts import" in source


# 4.2 e 4.6 linguagem neutra no módulo de textos, no aviso e na página
def test_page_and_texts_use_neutral_language():
    for text in page_strings():
        assert_neutral(text)
    for text in (
        texts.SIMULATION_MANDATORY_TEXT,
        texts.SIMULATION_ASSUMPTIONS,
        texts.SIMULATION_STRATEGY_CAPTION,
        SIMULATION_DISCLAIMER,
        *texts.SIMULATION_WINDOW_LABELS.values(),
    ):
        assert_neutral(text)


def test_page_keeps_past_conditional_wording():
    joined = " ".join(page_strings()).lower()
    assert "teria ocorrido" in joined
    assert "quanto investir" not in joined
    assert "vai ocorrer" not in joined


# 4.3 rótulos descritivos
def test_window_labels_are_descriptive():
    labels = texts.SIMULATION_WINDOW_LABELS
    assert labels["Pior janela"] == "Menor retorno histórico"
    assert labels["Melhor janela"] == "Maior retorno histórico"
    assert labels["Mediana"] == "Mediana"
    # a tabela usa os rótulos descritivos, não as chaves internas
    source = PAGE.read_text(encoding="utf-8")
    assert source.count("SIMULATION_WINDOW_LABELS[") >= 6
    for label in labels.values():
        assert_neutral(label)
    assert "SIMULATION_WINDOW_LABELS" in PAGE.read_text(encoding="utf-8")


# 4.4 premissas: fechamento sem dividendos, custos e impostos, moeda do ativo
def test_assumptions_state_price_costs_taxes_and_currency():
    text = texts.SIMULATION_ASSUMPTIONS.lower()
    for fragment in ("preço de fechamento", "dividendos", "corretagem",
                     "impostos", "moeda do ativo"):
        assert fragment in text
    assert "SIMULATION_ASSUMPTIONS" in PAGE.read_text(encoding="utf-8")


# 4.5 taxas de juros continuam fora
def test_interest_rate_tickers_stay_excluded():
    for ticker in ("^IRX", "^FVX", "^TNX", "^TYX"):
        assert non_simulable_reason(ticker) is not None
        assert "taxa de juros" in non_simulable_reason(ticker)