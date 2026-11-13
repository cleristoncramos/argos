"""Campo "Período disponível" em destaque quando o histórico é menor que o pedido (DL2-B)."""

from app.ui.data_info import SHORTER_HISTORY_ICON, available_period_markdown

RESUMO = {"available": "13/07/2020 a 12/11/2026"}


def test_periodo_menor_em_vermelho_com_icone():
    texto = available_period_markdown(RESUMO, True)
    assert SHORTER_HISTORY_ICON in texto and ":red[" in texto and "menor que o solicitado" in texto


def test_periodo_completo_sem_destaque():
    texto = available_period_markdown(RESUMO, False)
    assert ":red[" not in texto and SHORTER_HISTORY_ICON not in texto and RESUMO["available"] in texto
