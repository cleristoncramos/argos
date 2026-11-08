"""
Critérios de elegibilidade por ativo (protocolo, seção 9.3), todos obrigatórios.

1. R² fora da amostra estritamente maior que zero (None = não calculável);
2. Diebold-Mariano com p < 0,10 (estrito); não calculável não atende;
3. R² > 0 em pelo menos 5 das 8 dobras do desenvolvimento;
4. resultado econômico (A ∧ B) ∨ C com o custo-base;
5. o critério 4 mantido com o dobro do custo-base.
"""

from __future__ import annotations

from experiments.preditivo.config import DOBRAS_MINIMAS
from experiments.preditivo.estatistica import OK

MENSAGEM_SEM_EVIDENCIA = "Não houve evidência suficiente para habilitar o sinal."


def condicao_economica(resultados: dict) -> dict:
    estrategia, caixa, manter = resultados["estrategia"], resultados["caixa"], resultados["comprar_manter"]
    a = estrategia.retorno > caixa.retorno
    b = estrategia.drawdown_maximo < manter.drawdown_maximo
    c = estrategia.retorno > manter.retorno
    atende = (a and b) or c
    return {
        "A_retorno_acima_do_caixa": a,
        "B_queda_menor_que_comprar_e_manter": b,
        "C_retorno_acima_de_comprar_e_manter": c,
        "atende": atende,
        # Ramo C não comprova menor risco: destacar quando entra por ele com queda maior.
        "destaque_queda_maior_no_ramo_C": bool(atende and not (a and b) and c
                                               and estrategia.drawdown_maximo > manter.drawdown_maximo),
    }


def avaliar(r2_final, teste_dm, r2_dobras, resultados_base, resultados_dobro) -> dict:
    positivas = sum(1 for r in r2_dobras if r is not None and r > 0)
    economica_base = condicao_economica(resultados_base)
    economica_dobro = condicao_economica(resultados_dobro)
    criterios = {
        "1_ganho_preditivo": r2_final is not None and r2_final > 0,
        "2_comparacao_estatistica": teste_dm.status == OK and teste_dm.atende,
        "3_estabilidade": positivas >= DOBRAS_MINIMAS,
        "4_resultado_economico": economica_base["atende"],
        "5_robustez_ao_custo": economica_dobro["atende"],
    }
    elegivel = all(criterios.values())
    return {
        "criterios": criterios,
        "dobras_positivas": positivas,
        "dobras_avaliadas": len(r2_dobras),
        "economica_base": economica_base,
        "economica_dobro": economica_dobro,
        "elegivel": elegivel,
        "mensagem": "Elegível para integração experimental restrita, após conferência do relatório e dos testes."
        if elegivel else MENSAGEM_SEM_EVIDENCIA,
    }
