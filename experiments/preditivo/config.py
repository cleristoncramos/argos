"""
Parâmetros do piloto, copiados do protocolo consolidado (v1) e da nota
metodológica aprovados em 08/11/2026. Mudar qualquer valor aqui é mudança
substantiva do experimento (protocolo, seção 11).
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PROJETO = RAIZ.parents[1]
DADOS = RAIZ / "dados"                # um subdiretório por snapshot (snap-AAAAMMDD-NN), fora do Git
SNAPSHOT = RAIZ / "snapshot.json"     # ponteiro versionado: snapshot vigente e tentativas anteriores
POLITICA_QUALIDADE = RAIZ / "politica_qualidade.json"   # tratamento documentado das ocorrências de integridade
REGISTRO = RAIZ / "registro.jsonl"
CONDICOES = RAIZ / "condicoes_abertura.json"
MARCA_FINAL_USADO = RAIZ / "avaliacao_final_usada.json"
PROTOCOLO = PROJETO / "docs" / "preditivo" / "protocolo_piloto_v1.md"
NOTA = PROJETO / "docs" / "preditivo" / "nota_teste_estatistico.md"

# R6: ativos, horizonte e períodos
ATIVOS = ("PETR4.SA", "VALE3.SA")
HORIZONTE = 20            # intervalos entre observações (pregões)
INICIO_COLETA = "2008-01-02"
FIM_DESENVOLVIMENTO = "2021-12-30"
DATA_CORTE = "2026-10-30"
EMBARGO = 20              # pregões excluídos no início de cada validação
ANOS_DESENVOLVIMENTO = tuple(range(2014, 2022))   # validações das 8 dobras
ANOS_FINAIS = tuple(range(2022, 2027))            # ajuste inicial em 2022 e reestimações anuais
# Confirmado pelo orientador em 08/11/2026: o embargo vale nas fronteiras dos
# blocos de avaliação (cada dobra e o início do período final, em 2022); nas
# reestimações de 2023 a 2026, dentro do bloco já iniciado, aplica-se só o expurgo.
EMBARGO_NAS_REESTIMACOES_FINAIS = False

# Modelo candidato
ALPHAS = (0.1, 1.0, 10.0, 100.0, 1000.0)
VALIDACOES_INTERNAS = 3   # últimos anos completos do treino

# R7: estratégia, custos e caixa
CUSTO_LADO_BASE = 0.001   # 0,05% negociação + 0,05% slippage
CUSTOS_SENSIBILIDADE = (0.0, 0.001, 0.002, 0.003)
CUSTO_LADO_DOBRO = 0.002
LIMIAR = 0.002            # c: custo aproximado de ida e volta
PREGOES_ANO = 252

# Nota metodológica (N1 a N5)
NW_DEFASAGENS = 19
P_LIMIAR = 0.10
T_MINIMO = 200
DOBRAS_MINIMAS = 5

DESCRICAO_RESULTADO = (
    "Retorno aproximado com ajustes da fonte para proventos e desdobramentos, "
    "antes de impostos e de custos não modelados."
)
