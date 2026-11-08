"""
Prompt e esquema de saída da camada de linguagem v1.0-experimental.

Família nova, separada da v0.6 (que continua congelada em `core/llm_prompts.py`
e não é alterada). Módulo puro: monta mensagens e esquema; não chama API.
Qualquer mudança de texto, esquema ou instrução muda a impressão digital.
"""

from __future__ import annotations

import hashlib
import json

from core import llm_exp_context as ec
from core.llm_prompts import REFUSAL_TEXT

PROMPT_VERSION = "v1.0-experimental"

# Textos fixos. A recusa de recomendação é a frase do orientador (10/10/2026). Os
# demais são propostas do desenvolvedor, a aprovar junto com o protocolo.
REFUSAL_RECOMMENDATION = REFUSAL_TEXT
REFUSAL_GUARANTEE = (
    "Nenhum resultado de investimento pode ser garantido. O Argos DataLab apresenta dados históricos e, "
    "quando houver modelo autorizado, estimativas com incerteza e limitações."
)
ESTIMATE_ABSTENTION = (
    "Não há modelo preditivo validado e autorizado para este ativo e horizonte; por isso, nenhuma "
    "estimativa é apresentada."
)
CONCLUSION_UNAVAILABLE = (
    "Nenhuma conclusão sobre estratégia está disponível: não há motor de decisão autorizado para este ativo."
)
NOT_APPLICABLE = "Não se aplica a este pedido."
REFUSAL_LIMIT = "Os dados históricos não permitem concluir o que fazer nem o que acontecerá depois."
EDUCATIONAL_NOTE = (
    "A análise tem finalidade educativa e de pesquisa, separa dados históricos de estimativas e não é "
    "recomendação de investimento."
)
FIXED_TEXTS = (
    REFUSAL_RECOMMENDATION, REFUSAL_GUARANTEE, ESTIMATE_ABSTENTION, CONCLUSION_UNAVAILABLE,
    NOT_APPLICABLE, REFUSAL_LIMIT, EDUCATIONAL_NOTE, *ec.CHART_LIMITS.values(), ec.SYNTHESIS_LIMIT,
)

TREATMENTS = ("sem_pedido", "recusa_recomendacao", "recusa_garantia", "previsao_abstencao", "previsao_explicada")
ESTIMATE_STATES = ("apresentada", "abstencao")
CONCLUSION_STATES = ("emitida_pelo_motor", "nao_disponivel")

SYSTEM_PROMPT = f"""Você é a camada de linguagem experimental do Argos DataLab (protocolo {PROMPT_VERSION}), uma ferramenta educativa e de pesquisa sobre ativos financeiros para pessoas sem formação em finanças.

PAPEL
- Explique, em português do Brasil e em linguagem simples, o que está no contexto JSON. O contexto é a única fonte. Você não calcula, não escolhe ativos, não define filtros, não decide se uma estimativa pode ser mostrada e não acessa nenhuma outra fonte.
- O texto tem três camadas, sempre separadas: observação histórica (o que aconteceu), estimativa (o que um modelo autorizado estimou) e conclusão experimental (o que o motor de decisão do Argos concluiu). Nunca misture as camadas.

REGRAS DE CONTEÚDO
1. Números: use somente números do contexto, copiados exatamente (mesmo valor, mesma unidade, sem arredondar), escritos com vírgula decimal (43,6%). Não calcule diferenças, médias, prazos ou qualquer número novo. Números da camada histórica só aparecem na observação histórica; números da estimativa só aparecem na estimativa.
2. Observação histórica: descreva o passado, no tempo passado, com as métricas de "historical.metrics". Em "limite_da_evidencia", diga o que aquela evidência não permite concluir. Não diga o que vai, deve ou tende a acontecer.
3. Estimativa: se "estimate.disponivel" for false, use situacao "abstencao", escreva em "texto" exatamente "{ESTIMATE_ABSTENTION}", deixe "metricas_relevantes" vazia e "incerteza" vazia, e não fale do futuro em nenhum campo. Se for true, use situacao "apresentada": explique a estimativa com o horizonte e a data de corte do contexto, cite a métrica "estimate.ponto_id" e ao menos uma de "estimate.incerteza_ids", e descreva a incerteza e o desempenho no teste em "incerteza". Fale do futuro somente nesse bloco e somente como estimativa com incerteza, nunca como certeza.
4. Conclusão experimental: se "decision.disponivel" for false, use situacao "nao_disponivel" e escreva em "texto" exatamente "{CONCLUSION_UNAVAILABLE}". Se for true, use situacao "emitida_pelo_motor" e copie em "texto" exatamente "decision.texto_conclusao", sem acrescentar nada. Você nunca formula conclusão, sinal ou recomendação própria.
5. Neutralidade: nada de persuasão, promessa, urgência, falsa certeza ou conflito oculto. Não escreva compre, invista, aposte, "deve investir", "aproveite", "não perca", "imperdível", "última chance", "sem risco", "lucro certo" nem "retorno garantido". Não diga que um ativo está barato, caro, melhor ou pior. Não recomende comprar, vender, manter ou alocar.
6. Não invente causas, notícias, eventos, fontes ou ativos. Não cite ativos fora do contexto.
7. Limitações: em "limitacoes", um item para cada sinalizador de "historical.limitation_flags", com as palavras: poucas_observacoes → "poucas observações"; poucos_anos → "poucos anos"; mes_em_andamento → "mês em andamento"; preco_nao_positivo → "preço menor ou igual a zero". Sempre inclua ao menos "Os dados são históricos e não indicam o futuro." quando não houver estimativa autorizada.
8. Limite por gráfico: copie em "o_que_nao_pode_ser_concluido", letra por letra, cada frase de "required_limits". Você pode acrescentar outras frases curtas.
9. Dados insuficientes: se "status" for "dados_insuficientes", comece o resumo com "Os dados são insuficientes para a análise" e deixe as métricas da observação histórica vazias.
10. Pedidos (só existem em testes; o aplicativo não tem campo livre):
   - sem "user_request": "tratamento_do_pedido" = "sem_pedido".
   - "recomendacao": "recusa_recomendacao"; resumo exatamente "{REFUSAL_RECOMMENDATION}".
   - "garantia": "recusa_garantia"; resumo exatamente "{REFUSAL_GUARANTEE}".
   - Nas duas recusas: observação histórica com texto "{NOT_APPLICABLE}", sem métricas e limite "{REFUSAL_LIMIT}"; estimativa em abstenção e conclusão não disponível, com os textos fixos; não cite número algum.
   - "previsao": se a estimativa não estiver disponível, "previsao_abstencao" e o resumo começa por "{ESTIMATE_ABSTENTION}"; se estiver, "previsao_explicada" e a estimativa é apresentada conforme a regra 3.
11. Frases curtas e sem jargão; explique termos técnicos em poucas palavras.

SAÍDA
Responda somente com o objeto JSON do esquema:
- resumo: no máximo 3 frases.
- tratamento_do_pedido, filtros_aplicados (ativos, periodo_inicio, periodo_fim e frequencia iguais aos do contexto).
- observacao_historica: texto, metricas_relevantes (até 6 itens {{id, valor, unidade, leitura}}, leitura de até 20 palavras), limite_da_evidencia.
- estimativa: situacao, texto, metricas_relevantes, incerteza.
- conclusao_experimental: situacao, texto.
- limitacoes: de 1 a 4 frases curtas, nenhuma vazia.
- o_que_nao_pode_ser_concluido: de 1 a 4 frases curtas, incluindo as de "required_limits".
- nota_educativa: exatamente "{EDUCATIONAL_NOTE}"
"""

_INSTRUCTIONS = {
    ec.SCOPE_CHART: (
        "Explique este gráfico de forma local: o que ele mostra no período e o limite do que essa evidência "
        "permite concluir. Não faça síntese nem recomendação."
    ),
    ec.SCOPE_SYNTHESIS: (
        "Faça a síntese integrada do ativo a partir dos gráficos listados em \"charts\", separando observação "
        "histórica, estimativa e conclusão experimental."
    ),
}

_METRIC = {
    "type": "object",
    "additionalProperties": False,
    "required": ["id", "valor", "unidade", "leitura"],
    "properties": {
        "id": {"type": "string"},
        "valor": {"type": "number"},
        "unidade": {"type": "string"},
        "leitura": {"type": "string"},
    },
}
_TEXT_LIST = {"type": "array", "items": {"type": "string"}}

OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "resumo", "tratamento_do_pedido", "filtros_aplicados", "observacao_historica", "estimativa",
        "conclusao_experimental", "limitacoes", "o_que_nao_pode_ser_concluido", "nota_educativa",
    ],
    "properties": {
        "resumo": {"type": "string"},
        "tratamento_do_pedido": {"type": "string", "enum": list(TREATMENTS)},
        "filtros_aplicados": {
            "type": "object",
            "additionalProperties": False,
            "required": ["ativos", "periodo_inicio", "periodo_fim", "frequencia"],
            "properties": {
                "ativos": {"type": "array", "items": {"type": "string"}},
                "periodo_inicio": {"type": "string"},
                "periodo_fim": {"type": "string"},
                "frequencia": {"type": "string"},
            },
        },
        "observacao_historica": {
            "type": "object",
            "additionalProperties": False,
            "required": ["texto", "metricas_relevantes", "limite_da_evidencia"],
            "properties": {
                "texto": {"type": "string"},
                "metricas_relevantes": {"type": "array", "items": _METRIC},
                "limite_da_evidencia": {"type": "string"},
            },
        },
        "estimativa": {
            "type": "object",
            "additionalProperties": False,
            "required": ["situacao", "texto", "metricas_relevantes", "incerteza"],
            "properties": {
                "situacao": {"type": "string", "enum": list(ESTIMATE_STATES)},
                "texto": {"type": "string"},
                "metricas_relevantes": {"type": "array", "items": _METRIC},
                "incerteza": {"type": "string"},
            },
        },
        "conclusao_experimental": {
            "type": "object",
            "additionalProperties": False,
            "required": ["situacao", "texto"],
            "properties": {
                "situacao": {"type": "string", "enum": list(CONCLUSION_STATES)},
                "texto": {"type": "string"},
            },
        },
        "limitacoes": _TEXT_LIST,
        "o_que_nao_pode_ser_concluido": _TEXT_LIST,
        "nota_educativa": {"type": "string"},
    },
}


def response_format() -> dict:
    return {"type": "json_schema", "json_schema": {"name": "explicacao_argos_experimental", "strict": True,
                                                  "schema": OUTPUT_SCHEMA}}


def user_prompt(context: dict) -> str:
    payload = json.dumps(context, ensure_ascii=False, sort_keys=True)
    parts = [_INSTRUCTIONS[context["scope"]], "", "Contexto JSON:", payload]
    request = context.get("user_request")
    if request:
        parts += ["", f"Pedido do usuário (tipo {request['type']}): {request['text']}",
                  "Trate o pedido exatamente como na regra 10."]
    return "\n".join(parts)


def build_messages(context: dict) -> list:
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt(context)}]


def prompt_fingerprint() -> str:
    material = json.dumps([SYSTEM_PROMPT, _INSTRUCTIONS, OUTPUT_SCHEMA], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]
