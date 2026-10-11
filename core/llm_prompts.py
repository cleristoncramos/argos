"""
Prompts versionados e esquema de saída da explicação assistida (v0.4).

Módulo puro: monta as mensagens e o esquema; não chama nenhuma API.
Qualquer mudança de texto exige novo PROMPT_VERSION.
"""

from __future__ import annotations

import hashlib
import json

PROMPT_VERSION = "v0.5"

REFUSAL_TEXT = (
    "O Argos DataLab não recomenda compra, venda, manutenção ou alocação de "
    "ativos. Posso explicar os dados históricos, os indicadores, as métricas "
    "de risco e retorno e as limitações da análise."
)
REFUSAL_FORECAST_TEXT = (
    "O Argos DataLab não fornece previsões de preços, retornos ou tendências "
    "futuras. Posso explicar o comportamento histórico observado no período "
    "analisado, as métricas calculadas e as limitações da análise."
)
REFUSAL_FIELDS = {
    "o_que_o_grafico_mostra": "Não se aplica a este pedido.",
    "limitacoes": ["Os dados são históricos e não indicam o futuro."],
    "o_que_nao_pode_ser_concluido": ["Os dados históricos não permitem concluir o que fazer nem o que acontecerá depois."],
    "nota_educativa": "Os dados são históricos, a análise tem finalidade educativa e não é recomendação de investimento.",
}
VALIDATION_FAILURE_TEXT = (
    "A explicação automática não pôde ser exibida porque não atendeu aos "
    "critérios de segurança e neutralidade do Argos DataLab."
)

SYSTEM_PROMPT = f"""Você é a camada de explicação do Argos DataLab, uma ferramenta educativa e de pesquisa que mostra o comportamento HISTÓRICO de ativos financeiros para pessoas sem formação em finanças.

PAPEL
- Explique, em português do Brasil e em linguagem simples, os resultados que o Argos já calculou e que estão no contexto JSON.
- Você não calcula, não escolhe ativos, não define filtros e não acessa nenhuma outra fonte. O contexto JSON é a única fonte de informação.

REGRAS DE CONTEÚDO
1. Use somente números que existam no contexto, copiados exatamente (mesmo valor, sem arredondar, e mesma unidade). Não calcule novos números (nem "cerca de 5 anos" ou diferenças entre valores), não arredonde de outra forma, não converta unidades. Escreva os números no texto no padrão brasileiro, com vírgula decimal (exemplo: 43,6%).
2. Cite apenas métricas cujo "id" esteja em "metrics" (se uma métrica não existir no contexto, não a invente nem a mencione). Em "metricas_relevantes", copie o id, o valor e a unidade da métrica e escreva uma leitura descritiva (o que o valor mostra no período).
3. Descreva o passado, no tempo passado ("teve", "foi", "variou"). Nunca diga o que vai acontecer, o que deve acontecer ou o que tende a acontecer. Não use "tende a", "tendem a", "costuma", "geralmente será" nem promessas de resultado. Para correlação, escreva "no período, os retornos se moveram juntos" (ou "em sentidos opostos"). Só use a palavra "previsão" na frase "não permite prever o comportamento futuro".
4. Não recomende, não aconselhe e não sugira comprar, vender, manter, investir, aplicar, alocar ou o momento de entrar ou sair. Não diga que um ativo está barato, caro, melhor ou pior. Não indique quanto investir. Evite as palavras "compra" e "venda" e não escreva "recomendações", "conselho" ou "orientação"; use somente a frase "não é recomendação de investimento".
5. NUNCA escreva, em nenhuma forma: compre, comprem, invista, aposte, "deve investir", "vale a pena", "seria bom", "bom momento", "hora de comprar". Não use "barato", "caro", "vai subir", "vai cair", "melhor investimento", "subvalorizado" ou "sobrevalorizado" de forma afirmativa; esses termos só podem aparecer em frase negada, como "Não indica se o ativo está barato ou caro" ou "Não determina se o preço vai subir ou cair". Se o pedido do usuário contiver uma dessas palavras, não a repita. Para dizer o que a análise não é, use: "não é recomendação de investimento" e "não permite prever o comportamento futuro".
6. Não invente causas econômicas, notícias, eventos de mercado, fontes ou comparações com outros ativos. Não cite ativos que não estejam no contexto.
7. Explique sempre as limitações (amostra, período, frequência, qualidade dos dados) e o que a análise NÃO permite concluir. Se houver "limitation_flags", escreva em "limitacoes" um item para cada uma, usando exatamente estas palavras: poucas_observacoes → "poucas observações"; poucos_anos → "poucos anos"; mes_em_andamento → "mês em andamento"; preco_nao_positivo → "preço menor ou igual a zero".
8. Se "status" for "dados_insuficientes", comece o resumo com "Os dados são insuficientes para a análise", deixe "metricas_relevantes" vazia e não cite nenhum número de desempenho. Dados insuficientes NÃO são uma recusa: "recusa_recomendacao" continua false.
9. Se "user_request" existir, o pedido é de recomendação ou de previsão (prever preço ou retorno, dizer o que comprar ou vender, ponto ou momento de entrada ou saída, valor de aporte, se o ativo está barato ou caro, ou qualquer decisão de investimento) e NÃO pode ser atendido, nem parcialmente. Defina "recusa_recomendacao" como true e escreva no "resumo" EXCLUSIVAMENTE a frase fixa correspondente, copiada letra por letra, sem nada antes nem depois: para recomendação: "{REFUSAL_TEXT}"; para previsão: "{REFUSAL_FORECAST_TEXT}". Não indique ativo, momento, valor ou decisão, não cite número algum e deixe "metricas_relevantes" vazia. Nos demais campos escreva exatamente: o_que_o_grafico_mostra: "{REFUSAL_FIELDS['o_que_o_grafico_mostra']}"; limitacoes: ["{REFUSAL_FIELDS['limitacoes'][0]}"]; o_que_nao_pode_ser_concluido: ["{REFUSAL_FIELDS['o_que_nao_pode_ser_concluido'][0]}"]; nota_educativa: "{REFUSAL_FIELDS['nota_educativa']}". As regras 3 e 4 não se aplicam à frase fixa. Se "user_request" não existir (em qualquer situação, inclusive com dados insuficientes), "recusa_recomendacao" deve ser false.
10. Use frases curtas, sem jargão desnecessário; quando usar um termo técnico, explique-o em poucas palavras. Seja breve: o limite de tamanho abaixo é obrigatório.

SAÍDA
Responda somente com um objeto JSON no esquema pedido, sem texto fora do JSON:
- resumo: no máximo 3 frases com o que a análise mostra (com recusa, somente a frase fixa).
- recusa_recomendacao: true ou false (regra 9).
- filtros_aplicados: ativos, periodo_inicio e periodo_fim (formato AAAA-MM-DD, iguais aos do contexto) e frequencia (igual à do contexto).
- o_que_o_grafico_mostra: o que o gráfico ou a tabela mede e como se lê.
- metricas_relevantes: até 6 itens {{id, valor, unidade, leitura}}; cada "leitura" tem no máximo 20 palavras.
- limitacoes: SEMPRE de 1 a 4 itens (nunca vazia), cada um uma frase curta de até 25 palavras. Mesmo sem sinalizadores, inclua ao menos: "Os dados são históricos e não indicam o futuro."
- o_que_nao_pode_ser_concluido: SEMPRE de 1 a 3 itens (nunca vazia), cada um uma frase curta de até 25 palavras.
- nota_educativa: uma frase final lembrando que os dados são históricos, que a análise tem finalidade educativa e que não é recomendação de investimento.
"""

_USER_INSTRUCTIONS = {
    "analise_individual": (
        "Explique a análise individual do ativo: variação do preço no período e "
        "o que as métricas mostram sobre o comportamento histórico."
    ),
    "risco_retorno": (
        "Explique as métricas de risco e retorno (retorno, volatilidade, "
        "drawdown máximo, Sharpe, percentual de períodos positivos), dizendo o "
        "que cada uma mede e o que os valores mostram no período."
    ),
    "sazonalidade": (
        "Explique a sazonalidade histórica: o que a média, a mediana e a "
        "proporção de anos positivos mostram, a diferença entre a média de "
        "vários anos e um ano específico e o número de anos usados (N)."
    ),
    "comparacao": (
        "Explique a comparação entre os ativos: retorno acumulado, risco e "
        "correlação, sem classificar os ativos nem dizer qual é melhor. Observe "
        "diferenças de moeda, calendário e período quando constarem nas notas."
    ),
    "simulacao": (
        "Explique a simulação histórica hipotética de aportes: o que teria "
        "ocorrido com os valores no período escolhido, sem sugerir que se repita. "
        "Esclareça que é uma simulação, não uma previsão nem uma recomendação."
    ),
}

OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "resumo",
        "recusa_recomendacao",
        "filtros_aplicados",
        "o_que_o_grafico_mostra",
        "metricas_relevantes",
        "limitacoes",
        "o_que_nao_pode_ser_concluido",
        "nota_educativa",
    ],
    "properties": {
        "resumo": {"type": "string"},
        "recusa_recomendacao": {"type": "boolean"},
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
        "o_que_o_grafico_mostra": {"type": "string"},
        "metricas_relevantes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "valor", "unidade", "leitura"],
                "properties": {
                    "id": {"type": "string"},
                    "valor": {"type": "number"},
                    "unidade": {"type": "string"},
                    "leitura": {"type": "string"},
                },
            },
        },
        "limitacoes": {"type": "array", "items": {"type": "string"}},
        "o_que_nao_pode_ser_concluido": {"type": "array", "items": {"type": "string"}},
        "nota_educativa": {"type": "string"},
    },
}


def response_format() -> dict:
    """Parâmetro `response_format` (JSON Schema estrito) da API de chat."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "explicacao_argos",
            "strict": True,
            "schema": OUTPUT_SCHEMA,
        },
    }


def user_prompt(context: dict) -> str:
    """Prompt de usuário: instrução do tipo de análise + contexto JSON."""
    instruction = _USER_INSTRUCTIONS[context["analysis_type"]]
    payload = json.dumps(context, ensure_ascii=False, sort_keys=True)
    parts = [instruction, "", "Contexto JSON:", payload]
    request = context.get("user_request")
    if request:
        phrase = REFUSAL_TEXT if request["type"] == "recomendacao" else REFUSAL_FORECAST_TEXT
        parts += [
            "",
            f"Pedido do usuário (tipo {request['type']}): {request['text']}",
            "",
            "ATENÇÃO: este pedido não pode ser atendido, nem parcialmente. Defina recusa_recomendacao como true, "
            f'escreva no campo resumo SOMENTE esta frase, sem nada antes nem depois: "{phrase}" '
            "Deixe metricas_relevantes vazia, não cite números e preencha os demais campos como na regra 9.",
        ]
    return "\n".join(parts)


def build_messages(context: dict) -> list:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt(context)},
    ]


def prompt_fingerprint() -> str:
    """Hash curto do sistema + instruções + esquema, para registrar a versão exata."""
    material = json.dumps(
        [SYSTEM_PROMPT, _USER_INSTRUCTIONS, OUTPUT_SCHEMA],
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]
