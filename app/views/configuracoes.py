"""
Configurações (etapa 4 da DL2, 13/11/2026; ampliada em 14/11/2026).

- Padrões da análise: referência de comparação (B1), período, frequência e taxa
  livre de risco usados ao abrir as análises.
- Catálogo de ativos (B2): consulta do catálogo inteiro. Fixo e somente leitura na
  versão pública; editável só numa instalação local com ARGOS_CATALOGO_EDITAVEL=on
  (DL2-E), com as alterações guardadas num arquivo SQLite.
- Instalação local e SQLite: como ligar a edição e o que fica guardado no arquivo.
- Ambiente: o que cada variável de ambiente está fazendo nesta execução.

A lógica fica em core/local_catalog.py, core/settings_info.py e app/ui/catalog_state.py.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import streamlit as st

from app.ui.catalog_state import (
    active_catalog,
    analysis_defaults,
    group_label,
    local_catalog,
    preferred_reference,
    set_analysis_defaults,
    set_preferred_reference,
)
from app.ui.sidebar import fetch_recent
from app.ui.state import apply_defaults_to_unloaded
from core.assets import ASSET_GROUPS, CATALOG_SIZE, CATEGORY_METADATA
from core.benchmark import BENCHMARKS, reference_name
from core.demo_mode import is_demo_mode
from core.local_catalog import DB_ENV_VAR, DB_FILE, ENV_VAR, CatalogError, db_path, local_group_labels
from core.settings_info import (
    ARGOS_DEFAULTS,
    DEFAULT_FREQUENCY_CHOICES,
    DEFAULT_PERIOD_CHOICES,
    MAX_RISK_FREE_PCT,
    TABLE_DESCRIPTIONS,
    AnalysisDefaults,
    clean_risk_free,
    environment_status,
    file_summary,
    format_rate,
    local_assets_csv,
)
from core.ticker_input import validate_ticker

st.set_page_config(page_title="Argos", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    '<header class="pg-head">'
    '<div class="pg-kicker">Preferências da plataforma</div>'
    '<h1 class="pg-title">Configurações</h1>'
    '<p class="pg-sub">Padrões das análises, catálogo de ativos, instalação local e ambiente de execução.</p>'
    "</header>",
    unsafe_allow_html=True,
)

catalog = active_catalog()
local = local_catalog()
FLASH_KEY = "config_catalogo_mensagem"
WHERE_SAVED = (
    "Ficam salvos no arquivo SQLite desta instalação." if local
    else "Valem até você fechar o navegador."
)

# Mensagem da última alteração, mostrada depois de recarregar a página.
if FLASH_KEY in st.session_state:
    st.success(st.session_state.pop(FLASH_KEY))

tab_defaults, tab_catalog, tab_local, tab_env = st.tabs(
    ["Padrões da análise", "Catálogo de ativos", "Instalação local e SQLite", "Ambiente"]
)

# ==========================================================
# Padrões da análise
# ==========================================================
with tab_defaults:
    st.markdown("### Referência de comparação padrão")
    st.markdown(
        "Na Análise Individual, a trajetória do ativo pode ser vista ao lado de uma referência "
        "de mercado, as duas começando em 100. Por padrão, o Argos **sugere a referência pela "
        "classe do ativo** (por exemplo, Ibovespa para ações brasileiras). Aqui você pode fixar "
        "outra referência para todas as análises. Ela é só um ponto de comparação, não uma meta."
    )

    AUTOMATIC = "__automatica__"
    TYPED = "__digitada__"
    current = preferred_reference()
    fixed = list(BENCHMARKS)
    others = sorted(
        (a["ticker"] for a in catalog if a["ticker"] not in BENCHMARKS),
        key=lambda t: reference_name(t, catalog).lower(),
    )
    options = [AUTOMATIC, *fixed, *others, TYPED]
    if current and current not in options:
        options.insert(-1, current)

    def option_label(value: str) -> str:
        if value == AUTOMATIC:
            return "Automática, pela classe do ativo (recomendado)"
        if value == TYPED:
            return "Digitar outro ticker…"
        return f"{reference_name(value, catalog)} ({value})"

    choice = st.selectbox(
        "Referência padrão",
        options,
        index=options.index(current) if current in options else 0,
        format_func=option_label,
        key="config_referencia",
    )
    typed = ""
    if choice == TYPED:
        typed = st.text_input("Ticker da referência (código do Yahoo Finance)", placeholder="Ex.: ^STOXX50E, EWW")

    if st.button("Salvar referência", type="primary"):
        if choice == AUTOMATIC:
            set_preferred_reference(None)
            st.success("Referência padrão: automática, pela classe do ativo.")
        elif choice == TYPED:
            with st.spinner("Verificando ticker..."):
                result = validate_ticker(typed, fetch_recent)
            if result.ok:
                set_preferred_reference(result.ticker)
                st.success(f"Referência padrão: {result.ticker}.")
            else:
                st.error(result.message)
        else:
            set_preferred_reference(choice)
            st.success(f"Referência padrão: {option_label(choice)}.")

    saved = preferred_reference()
    st.caption(
        ("Em uso: " + (option_label(saved) if saved else "automática, pela classe do ativo") + ". ")
        + ("Fica salva nesta instalação." if local else "Vale até você fechar o navegador.")
        + " Quando o ativo analisado é a própria referência, o Argos volta à sugestão automática."
    )

    st.divider()
    st.markdown("### Período, frequência e taxa livre de risco")
    st.markdown(
        "Valores que a barra lateral **Parâmetros** mostra ao abrir as análises, e a taxa livre "
        "de risco inicial do Risco e Retorno e da Comparação de Ativos. Uma análise já carregada "
        "nesta sessão mantém a escolha feita na barra lateral: mudar estes padrões não refaz "
        "nenhuma análise."
    )
    defaults = analysis_defaults()
    with st.form("form_padroes_analise"):
        col_period, col_freq, col_rate = st.columns(3)
        period = col_period.selectbox(
            "Período padrão", DEFAULT_PERIOD_CHOICES, index=DEFAULT_PERIOD_CHOICES.index(defaults.period)
        )
        frequency = col_freq.selectbox(
            "Frequência padrão", DEFAULT_FREQUENCY_CHOICES, index=DEFAULT_FREQUENCY_CHOICES.index(defaults.frequency)
        )
        rate = col_rate.number_input(
            "Taxa livre de risco anual (%)",
            min_value=0.0,
            max_value=MAX_RISK_FREE_PCT,
            value=float(defaults.risk_free_pct),
            step=0.25,
            help="Usada no Índice de Sharpe do Risco e Retorno e da Comparação de Ativos. Ex.: 10,00 = 10% ao ano.",
        )
        col_save, col_reset = st.columns(2)
        save_defaults = col_save.form_submit_button("Salvar padrões", type="primary", use_container_width=True)
        reset_defaults = col_reset.form_submit_button("Voltar aos padrões do Argos", use_container_width=True)
    if save_defaults:
        set_analysis_defaults(AnalysisDefaults(period, frequency, clean_risk_free(rate)))
        apply_defaults_to_unloaded(analysis_defaults())
        st.session_state[FLASH_KEY] = "Padrões da análise salvos."
        st.rerun()
    if reset_defaults:
        set_analysis_defaults(ARGOS_DEFAULTS)
        apply_defaults_to_unloaded(ARGOS_DEFAULTS)
        st.session_state[FLASH_KEY] = "Padrões do Argos restaurados."
        st.rerun()
    defaults = analysis_defaults()
    st.caption(
        f"Em uso: {defaults.period}, frequência {defaults.frequency.lower()} e taxa livre de risco de "
        f"{format_rate(defaults.risk_free_pct)}. {WHERE_SAVED} Padrões do Argos: "
        f"{ARGOS_DEFAULTS.period}, {ARGOS_DEFAULTS.frequency.lower()} e {format_rate(ARGOS_DEFAULTS.risk_free_pct)}."
    )

# ==========================================================
# Catálogo de ativos
# ==========================================================
with tab_catalog:
    st.markdown("### Catálogo de ativos")
    groups = [g["key"] for g in ASSET_GROUPS] + ([g["key"] for g in local.groups()] if local else [])
    summary = pd.DataFrame(
        [
            {
                "Grupo": group_label(key),
                "Ativos": sum(1 for a in catalog if a["group"] == key),
                "Seus ativos": sum(1 for a in catalog if a["group"] == key and a.get("local")),
            }
            for key in groups
        ]
    )
    if local:
        st.markdown(
            f"O catálogo base, com {CATALOG_SIZE} ativos, não muda. Por cima dele, esta instalação "
            "guarda os grupos e ativos que você acrescentar, no arquivo SQLite descrito na aba "
            "**Instalação local e SQLite**. Eles aparecem na escolha de ativos da barra lateral e "
            "da Comparação de Ativos, com ⭐ nos grupos novos. O Panorama do Catálogo continua "
            "mostrando só o catálogo base."
        )
    else:
        summary = summary.drop(columns="Seus ativos")
        st.info(
            f"Nesta versão, o catálogo é **fixo e somente leitura**: são {CATALOG_SIZE} ativos em "
            f"{len(ASSET_GROUPS)} grupos. A edição do catálogo só existe numa instalação local do "
            "Argos (veja a aba **Instalação local e SQLite**). Ativos fora do catálogo podem ser "
            "analisados pela opção \"Digitar ticker\" da barra lateral.",
            icon="🔒",
        )
    st.dataframe(summary, hide_index=True, use_container_width=True)

    st.markdown("#### Consultar ativos")
    col_group_filter, col_search = st.columns([1, 2])
    ALL_GROUPS = "__todos__"
    group_filter = col_group_filter.selectbox(
        "Grupo",
        [ALL_GROUPS, *groups],
        format_func=lambda k: "Todos os grupos" if k == ALL_GROUPS else group_label(k),
        key="config_consulta_grupo",
    )
    search = col_search.text_input(
        "Buscar por ticker ou nome", placeholder="Ex.: PETR, Apple, ouro", key="config_consulta_busca"
    ).strip().lower()
    rows = [
        {
            "Ticker": a["ticker"],
            "Nome": a["name"],
            "Grupo": group_label(a["group"]),
            "Classe": a["class"],
            "Mercado": a.get("market", ""),
            "Origem": "Seu catálogo" if a.get("local") else "Catálogo base",
        }
        for a in catalog
        if (group_filter == ALL_GROUPS or a["group"] == group_filter)
        and (not search or search in a["ticker"].lower() or search in str(a["name"]).lower())
    ]
    found = pd.DataFrame(rows, columns=["Ticker", "Nome", "Grupo", "Classe", "Mercado", "Origem"])
    if not local:
        found = found.drop(columns="Origem")
    st.caption(f"{len(found)} ativo(s) encontrado(s).")
    st.dataframe(found, hide_index=True, use_container_width=True, height=min(38 + 35 * max(len(found), 1), 420))

    if local:
        st.divider()
        col_asset, col_group = st.columns(2, gap="large")

        with col_asset:
            st.markdown("#### Acrescentar ativo")
            with st.form("form_ativo_local", clear_on_submit=True):
                ticker = st.text_input("Ticker (código do Yahoo Finance)", placeholder="Ex.: AMD, EMBR3.SA")
                name = st.text_input("Nome (opcional)", placeholder="Ex.: Embraer")
                group = st.selectbox("Grupo", groups, format_func=group_label)
                if st.form_submit_button("Acrescentar", type="primary", use_container_width=True):
                    try:
                        with st.spinner("Verificando ticker na fonte..."):
                            added = local.add_asset(ticker, name, group, fetch_recent)
                    except CatalogError as error:
                        st.error(str(error))
                    else:
                        st.session_state[FLASH_KEY] = f"{added} acrescentado a {group_label(group)}."
                        st.rerun()
            st.caption("O ticker é conferido no Yahoo Finance antes de ser salvo.")

        with col_group:
            st.markdown("#### Criar grupo")
            with st.form("form_grupo_local", clear_on_submit=True):
                label = st.text_input("Nome do grupo", max_chars=40, placeholder="Ex.: Tecnologia")
                asset_class = st.selectbox("Classe dos ativos", list(CATEGORY_METADATA))
                if st.form_submit_button("Criar grupo", use_container_width=True):
                    try:
                        local.add_group(label, asset_class)
                    except CatalogError as error:
                        st.error(str(error))
                    else:
                        st.session_state[FLASH_KEY] = f"Grupo \"{label.strip()}\" criado."
                        st.rerun()
            st.caption("A classe define as cores e as regras de análise dos ativos do grupo.")

        mine = local.assets()
        if mine:
            st.markdown("#### Seus ativos")
            for item in mine:
                with st.expander(f"{item['name']} ({item['ticker']}) · {group_label(item['group'])}"):
                    with st.form(f"form_editar_{item['ticker']}"):
                        new_name = st.text_input("Nome exibido", value=item["name"])
                        new_group = st.selectbox(
                            "Grupo", groups, index=groups.index(item["group"]) if item["group"] in groups else 0,
                            format_func=group_label,
                        )
                        if st.form_submit_button("Salvar alterações", use_container_width=True):
                            try:
                                local.update_asset(item["ticker"], new_name, new_group)
                            except CatalogError as error:
                                st.error(str(error))
                            else:
                                st.session_state[FLASH_KEY] = f"{item['ticker']} atualizado."
                                st.rerun()
                    if st.button("Remover do catálogo", key=f"remover_{item['ticker']}", use_container_width=True):
                        local.remove_asset(item["ticker"])
                        st.session_state[FLASH_KEY] = f"{item['ticker']} removido do seu catálogo."
                        st.rerun()

        empty_groups = [g for g in local.groups() if not any(a["group"] == g["key"] for a in mine)]
        if empty_groups:
            st.markdown("#### Grupos vazios")
            for g in empty_groups:
                col_info, col_remove = st.columns([4, 1], vertical_alignment="center")
                col_info.markdown(f"{g['label']} · {g['class']}")
                if col_remove.button("Remover grupo", key=f"remover_grupo_{g['key']}", use_container_width=True):
                    local.remove_group(g["key"])
                    st.rerun()

        if mine:
            st.download_button(
                "Baixar seus ativos em CSV",
                data=local_assets_csv(local.records(), local_group_labels(local.groups())),
                file_name="argos_catalogo_local.csv",
                mime="text/csv",
            )

# ==========================================================
# Instalação local e SQLite
# ==========================================================
with tab_local:
    st.markdown("### Versão pública e instalação local")
    st.markdown(
        "A **versão pública** do Argos (no Streamlit Community Cloud) é compartilhada por todos os "
        "visitantes. Por isso, nela o catálogo é fixo, e as suas escolhas valem só até fechar o "
        "navegador. Numa **instalação local**, o Argos roda no seu computador a partir do código do "
        "repositório. Com a variável de ambiente **`" + ENV_VAR + "=on`**, ele passa a guardar num "
        "arquivo SQLite os grupos e ativos que você acrescentar e as preferências desta página."
    )
    if local:
        st.success(f"A edição do catálogo está **ligada** nesta instalação ({ENV_VAR}=on).", icon="✅")
    elif is_demo_mode():
        st.warning("O modo de demonstração está ligado: nele, a edição do catálogo fica sempre desligada.")
    else:
        st.info(f"A edição do catálogo está **desligada** nesta execução ({ENV_VAR} não vale on).", icon="🔒")

    st.markdown("#### Como ligar a edição do catálogo")
    st.markdown(
        "1. Instale o Argos no seu computador, como descrito no README do repositório "
        "(clonar, criar o ambiente virtual e instalar as dependências).\n"
        f"2. No terminal, na pasta do projeto, defina `{ENV_VAR}` com o valor `on` e inicie o Argos "
        "**no mesmo terminal**:"
    )
    shell_ps, shell_cmd, shell_unix = st.tabs(["Windows (PowerShell)", "Windows (Prompt de Comando)", "macOS ou Linux"])
    shell_ps.code(f'$env:{ENV_VAR} = "on"\nstreamlit run app/main.py', language="powershell")
    shell_cmd.code(f"set {ENV_VAR}=on\nstreamlit run app/main.py", language="bat")
    shell_unix.code(f"{ENV_VAR}=on streamlit run app/main.py", language="bash")
    st.markdown(
        "3. Abra a página **Configurações**. Esta aba passa a mostrar que a edição está ligada, e a aba "
        "**Catálogo de ativos** ganha os formulários para acrescentar ativos e criar grupos.\n\n"
        "A variável vale só para o terminal em que foi definida. Ao abrir outro terminal, defina-a de "
        "novo. Também são aceitos os valores `1`, `true`, `sim` e `yes`. Com o modo de demonstração "
        "(`ARGOS_DEMO_MODE=true`) ligado, a edição fica desligada de qualquer forma."
    )

    st.markdown("#### Onde ficam as alterações: o arquivo SQLite")
    relative = os.path.relpath(DB_FILE, PROJECT_ROOT).replace(os.sep, "/")
    st.markdown(
        "SQLite é um banco de dados guardado **num único arquivo**, sem servidor e sem instalação à "
        "parte (o Python já traz o suporte). O Argos usa um arquivo assim para a camada local do "
        f"catálogo, por padrão em **`{relative}`**, dentro da pasta do projeto.\n\n"
        "- **Criação:** o arquivo é criado sozinho na primeira vez que o Argos abre com a edição ligada.\n"
        f"- **Catálogo base intacto:** os {CATALOG_SIZE} ativos do catálogo base ficam no código "
        "(`core/assets.py`) e nunca são alterados. O Argos lê o catálogo base e **soma** o que está "
        "no arquivo.\n"
        "- **Gravação imediata:** cada alteração (acrescentar, editar ou remover um ativo, criar ou "
        "remover um grupo, salvar uma preferência) é gravada na hora. Ao fechar e abrir o Argos de "
        "novo, tudo continua lá.\n"
        "- **Fica no seu computador:** a pasta `data/` está no `.gitignore`. O arquivo não vai para o "
        "GitHub e não chega à versão pública.\n"
        f"- **Outro arquivo:** com `{DB_ENV_VAR}` apontando para outro caminho (por exemplo, "
        "`D:/argos/meu_catalogo.sqlite`), o Argos usa esse arquivo. Assim é possível manter catálogos "
        "separados, um para cada turma ou estudo."
    )
    st.markdown("O arquivo tem três tabelas:")
    st.dataframe(
        pd.DataFrame(TABLE_DESCRIPTIONS, columns=["Tabela", "Colunas", "O que guarda"]),
        hide_index=True,
        use_container_width=True,
    )
    st.markdown(
        "- **Cópia de segurança:** copie o arquivo `.sqlite` (com o Argos fechado) ou use o botão "
        "abaixo, quando a edição estiver ligada.\n"
        "- **Levar para outro computador:** copie o arquivo para a mesma pasta da outra instalação, "
        f"ou aponte `{DB_ENV_VAR}` para ele.\n"
        "- **Recomeçar do zero:** feche o Argos e apague o arquivo. Na próxima abertura, ele é criado "
        "vazio. O catálogo base continua igual.\n"
        "- **Abrir fora do Argos:** qualquer leitor de SQLite (por exemplo, o DB Browser for SQLite) "
        "abre o arquivo. Edite por fora com cuidado: o Argos só confere o ticker na fonte quando o "
        "ativo é acrescentado por esta página."
    )

    if local:
        st.markdown("#### Arquivo desta instalação")
        info = file_summary(db_path(), local.table_counts())
        counts = info["counts"]
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Grupos criados", counts["grupos"])
        col_b.metric("Ativos acrescentados", counts["ativos"])
        col_c.metric("Preferências salvas", counts["preferencias"])
        st.markdown(
            f"- **Caminho:** `{info['path']}`\n"
            f"- **Tamanho:** {info['size']}\n"
            f"- **Última alteração:** {info['modified']}"
        )
        st.download_button(
            "Baixar cópia de segurança (.sqlite)",
            data=local.snapshot(),
            file_name="catalogo_local.sqlite",
            mime="application/vnd.sqlite3",
        )

        st.markdown("#### Apagar o catálogo local")
        st.markdown(
            "Remove do arquivo **todos os grupos e ativos que você acrescentou**. As preferências "
            "(referência e padrões da análise) continuam. Não há como desfazer: se quiser guardar o "
            "catálogo, baixe a cópia de segurança antes."
        )
        confirm = st.checkbox("Entendi que os grupos e ativos acrescentados serão apagados.", key="config_confirma_apagar")
        if st.button("Apagar grupos e ativos acrescentados", disabled=not confirm):
            local.clear_entries()
            st.session_state.pop("config_confirma_apagar", None)
            st.session_state[FLASH_KEY] = "Catálogo local apagado. O catálogo base continua completo."
            st.rerun()

# ==========================================================
# Ambiente
# ==========================================================
with tab_env:
    st.markdown("### Ambiente desta execução")
    st.markdown(
        "Variáveis de ambiente que o Argos lê ao abrir e o efeito de cada uma agora. Elas só podem ser "
        "mudadas no terminal, antes de iniciar o Argos. Chaves de API não aparecem aqui."
    )
    st.dataframe(pd.DataFrame(environment_status()), hide_index=True, use_container_width=True)
    st.caption("A descrição completa de cada variável está na seção Configuração do README do projeto.")
