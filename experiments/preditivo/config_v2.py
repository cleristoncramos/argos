"""
Parâmetros próprios do piloto v2 (docs/preditivo/protocolo_piloto_v2.md), confirmados
pelo orientador em 08/11/2026 (V2-1 a V2-7). Todos os demais parâmetros vêm de
config.py (v1), que não muda. Mudar qualquer valor aqui é mudança substantiva da v2.
"""

from __future__ import annotations

from experiments.preditivo import config

VERSAO = "v2"

# V2-1 e V2-2: única mudança de modelagem, com limite fixo (sem nova ampliação na v2)
ALPHAS = (0.1, 1.0, 10.0, 100.0, 1000.0, 1e4, 1e5, 1e6)
ALPHAS_V1 = config.ALPHAS
LIMITE_SUPERIOR = max(ALPHAS)

# Protocolo v2, seção 11: reprodução da v1 nos valores comuns das grades
TOLERANCIA_RELATIVA = 1e-10
TOLERANCIA_ABSOLUTA = 1e-12

# Arquivos próprios da v2 (os da v1 não são tocados)
PROTOCOLO = config.PROJETO / "docs" / "preditivo" / "protocolo_piloto_v2.md"
REGISTRO = config.RAIZ / "registro_v2.jsonl"
CONDICOES = config.RAIZ / "condicoes_abertura_v2.json"
MARCA_FINAL_USADO = config.RAIZ / "avaliacao_final_usada_v2.json"
DATAS_ELEGIVEIS = config.RAIZ / "datas_elegiveis_v2.json"
ENCERRAMENTO = config.RAIZ / "encerramento_v2.json"
RESULTADOS = config.RAIZ / "resultados" / "v2"
RESULTADOS_V1 = config.RAIZ / "resultados"
ENCERRAMENTO_V1 = config.RAIZ / "encerramento_v1.json"

# Protocolo v2, seção 9: condições de abertura do período final, todas obrigatórias
CONDICOES_ABERTURA = (
    "1_protocolo_v2_confirmado",
    "2_configuracao_e_dados_identificados_por_hashes",
    "3_implementacao_e_testes_concluidos",
    "4_desenvolvimento_oficial_concluido",
    "5_criterios_3_e_6_atendidos_no_desenvolvimento",
    "6_relatorio_de_desenvolvimento_emitido",
    "7_nova_decisao_escrita_de_abertura",
)

# Alterações locais aceitas no congelamento: o documento sem relação com o piloto
# (desvio já registrado na v1) e o próprio registro de execuções da v2.
ALTERACOES_ACEITAS = ("docs/versao_congelada.md", "experiments/preditivo/registro_v2.jsonl")

DECLARACAO_NAO_INDEPENDENCIA = (
    "A configuração da v2 foi proposta a partir dos resultados de desenvolvimento da v1. "
    "As mesmas dobras foram reutilizadas para seleção e avaliação de desenvolvimento. "
    "Seus resultados não constituem evidência independente de generalização."
)
PERIODO_RESERVADO = "Período ainda não utilizado para avaliação preditiva ou seleção de modelos."
