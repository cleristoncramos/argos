"""
Conteúdo e blocos HTML da página "Sobre o Projeto".

Funções puras (sem Streamlit), testadas em tests/test_about.py. Os números do
catálogo e a ordem dos módulos vêm do próprio sistema (core/assets.py e
app/ui/pages.py), para que a página não fique desatualizada.
"""

from __future__ import annotations

from collections import Counter
from html import escape
from typing import Iterable, Mapping

from app.ui.landing import ACADEMIC_INFO
from app.ui.pages import ANALYSIS_PAGES

SUBTITLE = "Plataforma de Análise Histórica de Ativos Financeiros"

RESEARCH_QUESTION = (
    "Em que medida indicadores técnicos clássicos (tendência, momentum, volatilidade e "
    "volume), calculados sobre dados históricos de múltiplas classes de ativos, podem ser "
    "organizados em uma ferramenta de apoio à interpretação de dados financeiros que seja "
    "compreensível para usuários sem formação em finanças, preservando rigor metodológico e "
    "sem configurar recomendação de investimento?"
)

GENERAL_OBJECTIVE = (
    "Desenvolver e avaliar uma ferramenta de apoio à interpretação de dados históricos do "
    "mercado financeiro que organize indicadores técnicos clássicos de forma compreensível "
    "para pessoas sem formação em finanças, com rigor metodológico e sem configurar "
    "recomendação de investimento."
)

# (código, objetivo, situação, concluído?)
SPECIFIC_OBJECTIVES = (
    ("O1", "Selecionar e documentar indicadores com fórmula, parâmetros e limitações",
     "Concluído", True),
    ("O2", "Implementar os cálculos de forma reprodutível e verificada, sem informação futura",
     "Concluído; testes contra valores de referência independentes em andamento", True),
    ("O3", "Construir uma camada educativa para usuários sem formação em finanças",
     "Concluído", True),
    ("O4", "Garantir linguagem neutra e separar informação histórica, interpretação, "
           "simulação e recomendação", "Concluído", True),
    ("O5", "Documentar fontes, tratamento dos dados e limitações", "Concluído", True),
    ("O6", "Avaliar a compreensão da ferramenta por usuários sem formação em finanças",
     "Aguarda parecer do Comitê de Ética em Pesquisa", False),
)

# Pergunta que cada módulo responde e o que oferece, por caminho da página.
MODULE_DETAILS = {
    "views/analise_individual.py": (
        "Como um ativo se comportou ao longo do tempo?",
        ("Preço de fechamento, retorno do período e estatísticas descritivas",
         "Volatilidade anualizada mês a mês",
         "Mapa de calor de retornos mensais, recorte por anos e janela sazonal",
         "Exportação dos dados tratados em CSV"),
    ),
    "views/comparacao_ativos.py": (
        "Qual ativo foi mais longe no mesmo período e eles se movem juntos?",
        ("De 2 a 5 ativos em base 100, inclusive de grupos diferentes",
         "Filtros por grupo, subclasse e mercado; período comum opcional",
         "Correlação dos retornos e resumo de risco e retorno",
         "Retorno móvel e razão de desempenho"),
    ),
    "views/indicadores_tecnicos.py": (
        "O que dizem os indicadores clássicos de tendência, momento e volatilidade?",
        ("Linha de fechamento ou candles",
         "Médias móveis simples e exponenciais, Bandas de Bollinger",
         "RSI, MACD, ATR, volatilidade móvel e volume",
         "Guia de leitura de cada indicador, sem sinais de compra ou venda"),
    ),
    "views/risco_retorno.py": (
        "Quanto o ativo oscilou e qual foi a maior queda desde um pico?",
        ("Retorno acumulado e médio, volatilidade anualizada",
         "Índice de Sharpe com taxa livre de risco configurável",
         "Drawdown máximo e a data do fundo da queda",
         "Melhor e pior período e distribuição dos retornos"),
    ),
    "views/simulacao_aportes.py": (
        "E se eu tivesse investido um valor fixo no passado?",
        ("Aporte único e aportes periódicos com o mesmo total investido",
         "Janelas históricas com menor, mediano e maior resultado",
         "Premissas explícitas: sem dividendos, custos, impostos ou inflação",
         "Valor hipotético; não considera perfil, renda ou objetivos"),
    ),
    "views/panorama_catalogo.py": (
        "Como os ativos de um mesmo grupo se comportaram no mesmo período?",
        ("Todos os ativos de um grupo, consultados um grupo por vez",
         "Variação no período e em 12 meses ao lado da volatilidade e da queda máxima",
         "Ordem inicial por nome; a ordenação não é recomendação",
         "Dados indisponíveis aparecem vazios, nunca como zero"),
    ),
}

METHODOLOGY = (
    ("Variável principal", "Preço de fechamento da frequência escolhida (diária, semanal, mensal, semestral ou anual)"),
    ("Retorno", "Retorno simples entre períodos consecutivos; lacunas ficam vazias e não são preenchidas"),
    ("Anualização", "Fator 252 (diário), 52 (semanal), 12 (mensal), 2 (semestral) e 1 (anual), igual para todas as classes"),
    ("Risco", "Volatilidade com desvio-padrão amostral; Sharpe com a taxa livre de risco convertida para a frequência; drawdown em relação ao maior pico anterior"),
    ("Comparação", "Base 100 a partir do primeiro valor válido de cada série; correlação de Pearson entre retornos coincidentes"),
    ("Indicadores", "SMA, EMA, Bollinger (desvio amostral), RSI de Wilder e MACD 12/26/9, com parâmetros ajustáveis"),
    ("Sem informação futura", "Cada indicador, em cada data, usa apenas dados até aquela data (verificado por testes)"),
)

QUALITY = (
    ("Testes automatizados", "Todo cálculo do núcleo (core/) é coberto por testes, com 100% de cobertura de código."),
    ("Linguagem neutra", "Os textos exibidos são verificados automaticamente contra expressões de recomendação."),
    ("Reprodutibilidade", "Modo de demonstração com dados congelados, data de coleta e hash SHA-256 de cada arquivo."),
    ("Explicação assistida", "Recurso opcional e desligado por padrão, com prompt versionado e respostas validadas antes da exibição."),
    ("Documentação", "Arquitetura, metodologia, fontes de dados e decisões registradas no repositório."),
)

OUT_OF_SCOPE = (
    "Previsão de preços ou modelos preditivos",
    "Recomendação de compra, venda ou adequação ao perfil do investidor",
    "Dividendos, câmbio, inflação, custos e impostos nos retornos",
    "Dados em tempo real: as séries são históricas, consultadas sob demanda",
)


def group_counts(assets: Iterable[Mapping[str, str]], groups: Iterable[Mapping[str, str]]) -> list[tuple[str, str, int]]:
    """(rótulo do grupo, classe, quantidade de ativos) na ordem do menu de grupos."""
    counts = Counter(asset["group"] for asset in assets)
    return [(group["label"], group["class"], counts[group["key"]]) for group in groups]


def _section(kicker: str, title: str, body: str, lead: str = "") -> str:
    lead_html = f'<p class="ab-lead">{escape(lead)}</p>' if lead else ""
    return (
        f'<section class="ab-section"><div class="ab-kicker">{escape(kicker)}</div>'
        f'<h2 class="ab-title">{escape(title)}</h2>{lead_html}{body}</section>'
    )


def build_hero_html(stats: Mapping[str, int]) -> str:
    facts = (
        (stats["assets"], "ativos"),
        (stats["groups"], "grupos"),
        (stats["classes"], "classes"),
        (len(ANALYSIS_PAGES), "módulos de análise"),
        (5, "frequências"),
    )
    cells = "".join(f'<div><b>{value}</b><span>{escape(label)}</span></div>' for value, label in facts)
    return f"""
<div class="ab-hero">
  <div class="ab-eyebrow">Sobre o projeto · PIBITI UFPI 2026–2027</div>
  <h1 class="ab-name">Argos</h1>
  <div class="ab-subtitle">{escape(SUBTITLE)}</div>
  <p class="ab-intro">Ferramenta acadêmica para estudar o comportamento histórico de ativos financeiros.
  Reúne dados de mercado, métricas de risco e retorno e indicadores técnicos em um só lugar, com
  fórmulas documentadas e explicações em linguagem simples, para quem não tem formação em finanças.</p>
  <div class="ab-facts">{cells}</div>
</div>"""


def build_context_html() -> str:
    cards = (
        ("O problema",
         "Dados de mercado estão amplamente disponíveis, mas interpretá-los exige conhecimento técnico. "
         "Gráficos e indicadores costumam aparecer sem a fórmula, sem as premissas e misturados a "
         "sugestões de compra e venda, o que dificulta o estudo crítico."),
        ("A proposta",
         "Organizar o histórico de diferentes classes de ativos com cálculos verificáveis e uma camada "
         "educativa que explica o que cada número significa e o que ele não permite concluir, sempre "
         "separando a descrição do passado de qualquer recomendação."),
        ("Para quem",
         "Estudantes, pesquisadores e pessoas interessadas em mercado financeiro que desejam examinar "
         "dados históricos com rigor, inclusive sem formação prévia na área."),
    )
    body = '<div class="ab-cards ab-cards-3">' + "".join(
        f'<div class="ab-card"><h3>{escape(title)}</h3><p>{escape(text)}</p></div>' for title, text in cards
    ) + "</div>"
    return _section("01 · Contexto", "Por que o projeto existe", body)


def build_research_html() -> str:
    rows = "".join(
        f'<tr><td class="ab-code">{escape(code)}</td><td>{escape(goal)}</td>'
        f'<td><span class="ab-status {"ok" if done else "pending"}">{escape(status)}</span></td></tr>'
        for code, goal, status, done in SPECIFIC_OBJECTIVES
    )
    body = (
        f'<blockquote class="ab-question">{escape(RESEARCH_QUESTION)}</blockquote>'
        f'<div class="ab-card ab-objective"><h3>Objetivo geral</h3><p>{escape(GENERAL_OBJECTIVE)}</p></div>'
        '<table class="ab-table"><thead><tr><th>#</th><th>Objetivo específico</th><th>Situação</th></tr></thead>'
        f"<tbody>{rows}</tbody></table>"
    )
    return _section("02 · Pesquisa", "Pergunta de pesquisa e objetivos", body)


def build_modules_html() -> str:
    cards = []
    # Só os módulos de análise; esta própria página não tem cartão.
    for number, spec in enumerate(ANALYSIS_PAGES, 1):
        question, items = MODULE_DETAILS[spec.path]
        bullets = "".join(f"<li>{escape(item)}</li>" for item in items)
        cards.append(
            f'<div class="ab-card ab-module"><div class="ab-module-top"><span>{spec.icon}</span>'
            f'<span class="ab-n">{number:02d}</span></div><h3>{escape(spec.title)}</h3>'
            f'<p class="ab-q">{escape(question)}</p><ul>{bullets}</ul></div>'
        )
    body = '<div class="ab-cards ab-cards-3">' + "".join(cards) + "</div>"
    return _section("03 · Módulos", "O que cada página responde", body,
                    "A ordem segue o fluxo de estudo e é a mesma do menu principal.")


def build_methodology_html() -> str:
    rows = "".join(f"<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>" for k, v in METHODOLOGY)
    body = (
        f'<table class="ab-table ab-kv"><tbody>{rows}</tbody></table>'
        '<p class="ab-note">Fórmulas, unidades e casos-limite estão em docs/metodologia_de_calculo.md, no repositório do projeto.</p>'
    )
    return _section("04 · Metodologia", "Como os números são calculados", body)


def build_data_html(stats: Mapping[str, int], groups: list[tuple[str, str, int]]) -> str:
    cells = "".join(
        f'<div class="ab-group"><span>{escape(label)}</span><small>{escape(asset_class)}</small><b>{count}</b></div>'
        for label, asset_class, count in groups
    )
    sources = (
        ("Yahoo Finance (via yfinance)", "Séries diárias de abertura, máxima, mínima, fechamento e volume, consultadas sob demanda e guardadas em cache por 1 hora"),
        ("Catálogo interno", f'{stats["assets"]} ativos selecionados de forma intencional, organizados em {stats["groups"]} grupos e {stats["classes"]} classes'),
        ("Pacote de demonstração", "Arquivos salvos para apresentações e avaliação sem depender da internet"),
    )
    source_rows = "".join(f"<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>" for k, v in sources)
    body = (
        f'<table class="ab-table ab-kv"><tbody>{source_rows}</tbody></table>'
        f'<h3 class="ab-sub">Grupos do catálogo</h3><div class="ab-groups">{cells}</div>'
        '<p class="ab-note">Os retornos são de preço: dividendos e proventos não são incorporados. '
        "A fonte pode ter atrasos, ajustes históricos e indisponibilidade temporária.</p>"
    )
    return _section("05 · Dados", "Fontes e catálogo de ativos", body)


def build_quality_html() -> str:
    quality = "".join(f'<div class="ab-card"><h3>{escape(t)}</h3><p>{escape(d)}</p></div>' for t, d in QUALITY)
    scope = "".join(f"<li>{escape(item)}</li>" for item in OUT_OF_SCOPE)
    body = (
        f'<div class="ab-cards ab-cards-3">{quality}'
        f'<div class="ab-card ab-scope"><h3>Fora do escopo</h3><ul>{scope}</ul></div></div>'
    )
    return _section("06 · Qualidade", "Rigor, reprodutibilidade e limites", body)


def build_team_html() -> str:
    info = ACADEMIC_INFO
    rows = (
        ("Instituição", info["institution"]),
        ("Centro", info["center"]),
        ("Curso", info["course"]),
        ("Programa", info["program"]),
        ("Plano de trabalho", info["work_plan"]),
        ("Pesquisador discente", info["author"]),
        ("Orientador", info["advisor"]),
    )
    table = "".join(f"<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>" for k, v in rows)
    body = (
        f'<table class="ab-table ab-kv"><tbody>{table}</tbody></table>'
        '<p class="ab-note">Tecnologias, bases de dados e logotipos institucionais estão no botão '
        "Informações acadêmicas, na página inicial.</p>"
    )
    return _section("07 · Equipe", "Contexto acadêmico", body)


def build_disclaimer_html() -> str:
    return (
        '<div class="ab-disclaimer"><b>Aviso legal e metodológico.</b> O Argos tem finalidade '
        "exclusivamente acadêmica, educacional e de desenvolvimento tecnológico. As análises "
        "descrevem dados históricos; resultados passados não garantem resultados futuros, e "
        "nenhuma informação exibida constitui recomendação, indicação ou aconselhamento de "
        "investimento.</div>"
    )


ABOUT_CSS = """
<style>
/* Largura total, como nas demais páginas (sem limite lateral) */
.block-container { max-width: none !important; }
@keyframes ab-rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
.ab-hero { padding: 26px 30px 22px; border: 1px solid #2a2a2a; animation: ab-rise .5s ease both;
  background: radial-gradient(700px 260px at 100% 0%, rgba(200,16,46,.10), transparent 65%), #fff;
  box-shadow: 0 14px 34px rgba(17,17,17,.08); }
.ab-eyebrow { color: #c8102e; font-size: .74rem; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; }
.ab-name { margin: 6px 0 0 !important; padding: 0 !important; font-size: 3.2rem !important; font-weight: 800 !important;
  letter-spacing: -.04em; line-height: 1 !important; color: #111; }
.ab-subtitle { margin-top: 10px; padding-left: 12px; border-left: 3px solid #c8102e; font-size: 1.3rem; font-weight: 650; color: #111; }
.ab-intro { margin: 14px 0 0; max-width: 820px; color: #3f3f3f; font-size: 1rem; line-height: 1.7; }
.ab-facts { display: grid; grid-template-columns: repeat(5, 1fr); margin-top: 20px; border: 1px solid #2a2a2a; background: #fff; }
.ab-facts div { padding: 10px 14px; border-right: 1px solid #e4e1da; }
.ab-facts div:last-child { border-right: 0; }
.ab-facts b { display: block; font-size: 1.5rem; color: #111; }
.ab-facts span { font-size: .68rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #5f5f5f; }
.ab-section { margin-top: 44px; padding-top: 14px; border-top: 1px solid #2a2a2a; animation: ab-rise .5s ease both; }
.ab-kicker { color: #c8102e; font-size: .72rem; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; }
.ab-title { margin: 6px 0 4px !important; padding: 0 !important; font-size: 1.75rem !important; font-weight: 800 !important;
  letter-spacing: -.02em; color: #111; }
.ab-lead { margin: 0 0 12px; color: #5f5f5f; }
.ab-sub { margin: 22px 0 10px !important; padding: 0 !important; font-size: 1.05rem !important; color: #111; }
.ab-cards { display: grid; gap: 14px; margin-top: 14px; }
.ab-cards-3 { grid-template-columns: repeat(3, 1fr); }
.ab-card { padding: 18px 20px; background: #fff; border: 1px solid #2a2a2a; border-top: 3px solid #c8102e;
  box-shadow: 0 8px 22px rgba(17,17,17,.07); }
.ab-card h3 { margin: 0 0 8px !important; padding: 0 !important; font-size: 1.02rem !important; font-weight: 750 !important; color: #111; }
.ab-card p, .ab-card li { margin: 0; color: #3f3f3f; font-size: .9rem; line-height: 1.6; }
.ab-card ul { margin: 8px 0 0; padding-left: 18px; }
.ab-module-top { display: flex; justify-content: space-between; align-items: center; font-size: 1.4rem; }
.ab-n { font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: .74rem; color: #5f5f5f; }
.ab-module h3 { margin-top: 8px !important; }
.ab-q { color: #c8102e !important; font-weight: 600; }
.ab-question { margin: 14px 0 0; padding: 18px 22px; border: 1px solid #2a2a2a; border-left: 4px solid #c8102e;
  background: linear-gradient(90deg, rgba(200,16,46,.06), #fff 60%); font-size: 1.05rem; line-height: 1.65; color: #111; font-style: italic; }
.ab-objective { margin-top: 14px; border-top-color: #111; }
.ab-table { width: 100%; margin-top: 14px; border-collapse: collapse; border: 1px solid #2a2a2a; background: #fff;
  box-shadow: 0 8px 22px rgba(17,17,17,.06); font-size: .9rem; }
.ab-table th, .ab-table td { padding: 10px 14px; text-align: left; vertical-align: top; border: 0; border-bottom: 1px solid #e4e1da; color: #111; }
.ab-table tr:last-child th, .ab-table tr:last-child td { border-bottom: 0; }
.ab-table thead th { background: linear-gradient(180deg, #2b2b31, #1b1b1f); color: #fff; font-size: .72rem; letter-spacing: .1em;
  text-transform: uppercase; border-bottom: 2px solid #c8102e; }
.ab-kv tbody th { width: 220px; background: #f6f4ef; font-weight: 700; border-right: 1px solid #2a2a2a; }
.ab-code { width: 56px; font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-weight: 700; color: #c8102e !important; }
.ab-status { display: inline-block; padding: 2px 8px; font-size: .78rem; font-weight: 700; border: 1px solid; }
.ab-status.ok { color: #166534; border-color: #166534; background: #f0fdf4; }
.ab-status.pending { color: #92400e; border-color: #92400e; background: #fffbeb; }
.ab-groups { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px; }
.ab-group { display: grid; grid-template-columns: 1fr auto; align-items: center; padding: 10px 14px; background: #fff;
  border: 1px solid #2a2a2a; box-shadow: 0 4px 12px rgba(17,17,17,.05); }
.ab-group span { font-weight: 650; color: #111; }
.ab-group small { grid-column: 1; color: #5f5f5f; font-size: .76rem; }
.ab-group b { grid-column: 2; grid-row: 1 / span 2; font-size: 1.3rem; color: #c8102e; }
.ab-scope { border-top-color: #92400e; }
.ab-note { margin: 10px 0 0; color: #5f5f5f; font-size: .84rem; }
.ab-disclaimer { margin-top: 44px; padding: 16px 20px; border: 1px solid #2a2a2a; border-left: 4px solid #92400e;
  background: #fffbeb; color: #3f3f3f; font-size: .92rem; line-height: 1.6; }
@media (max-width: 900px) {
  .ab-cards-3 { grid-template-columns: 1fr; }
  .ab-facts { grid-template-columns: repeat(2, 1fr); }
  .ab-kv tbody th { width: 120px; }
}
@media (prefers-reduced-motion: reduce) { .ab-hero, .ab-section { animation: none; } }
</style>
"""
