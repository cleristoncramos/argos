"""
Seção "Explicação assistida por IA" (7B, bloco 2).

Aparece nas telas de análise como um botão. Não há campo de texto livre: a
explicação é gerada só a partir do contexto estruturado que a tela já calculou,
passa pelo validador e, em qualquer falha, mostra o texto educativo fixo.

Configuração (segredos do Streamlit ou variáveis de ambiente):
  ARGOS_LLM_MODE   off (padrão) | demo | live
  OPENAI_API_KEY   necessário só no modo live; nunca fica no repositório
  ARGOS_LLM_RECORD 1 para, no modo live, gravar cada resposta validada em
                   data/llm_demo.json (uso do pesquisador, para montar o modo demo)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Optional

import streamlit as st

from core import demo_mode, llm_mode, llm_service
from core.assets import ASSETS
from core.llm_render import explanation_view

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMO_PATH = PROJECT_ROOT / "data" / "llm_demo.json"
LOG_PATH = PROJECT_ROOT / "logs" / "llm_uso.jsonl"
DISCLAIMER = (
    "Conteúdo educativo gerado por modelo de linguagem a partir das métricas desta tela. "
    "Descreve dados históricos; não é recomendação de investimento nem previsão."
)


def _setting(name: str) -> Optional[str]:
    try:
        value = st.secrets.get(name)
    except Exception:  # sem arquivo de segredos
        value = None
    value = value if value else os.environ.get(name)
    return str(value).strip() if value else None


def current_mode() -> str:
    return llm_mode.resolve_mode(
        _setting("ARGOS_LLM_MODE"), demo_mode.is_demo_mode(), _recording()
    )


def _recording() -> bool:
    return (_setting("ARGOS_LLM_RECORD") or "").lower() in ("1", "true", "sim")


@st.cache_data(show_spinner=False)
def _demo_store() -> dict:
    return llm_service.load_demo_store(DEMO_PATH)


def _limiter() -> llm_service.UsageLimiter:
    if "llm_limiter" not in st.session_state:
        st.session_state["llm_limiter"] = llm_service.UsageLimiter()
    return st.session_state["llm_limiter"]


def _log_writer(page: str) -> Callable:
    def write(record: dict) -> None:
        try:
            llm_service.append_log(LOG_PATH, {**record, "page": page})
        except OSError:  # sistema de arquivos somente leitura: o registro é opcional na tela
            pass

    return write


def _show(result: llm_service.Explanation, context: dict) -> None:
    if not result.shown:
        st.info(llm_service.FALLBACK_TEXT)
        st.caption(f"Motivo técnico: {result.reason}")
        return
    view = explanation_view(result.data, context)
    if result.status == llm_service.STATUS_DEMO:
        st.caption("🧪 Resposta de demonstração (salva), não gerada agora.")
    st.markdown(f"**Resumo.** {view['resumo']}")
    st.markdown(f"**O que o gráfico mostra.** {view['grafico']}")
    for label, value, reading in view["metricas"]:
        st.markdown(f"- **{label}:** {value}. {reading}")
    st.markdown("**Limitações**")
    for item in view["limitacoes"]:
        st.markdown(f"- {item}")
    st.markdown("**O que não se pode concluir**")
    for item in view["nao_concluir"]:
        st.markdown(f"- {item}")
    st.caption(view["nota"])


def asset_name(symbol: str) -> Optional[str]:
    asset = next((a for a in ASSETS if a["ticker"] == symbol), None)
    return (asset or {}).get("name")


def render_explain_section(build_context: Callable[[], Optional[dict]], key: str) -> None:
    """
    `build_context` só é chamado se o recurso estiver ligado, para não gastar
    processamento nem expor nada no modo desativado (padrão).
    """
    mode = current_mode()
    if mode == llm_service.MODE_OFF:
        return
    context = build_context()
    if context is None:
        return

    st.divider()
    st.subheader("Explicação assistida por IA")
    st.caption(DISCLAIMER)

    state_key = f"llm_result_{key}"
    context_key = llm_service.context_key(context)
    if st.button("Explicar com IA", key=f"llm_btn_{key}"):
        with st.spinner("Gerando e validando a explicação..."):
            result = llm_service.explain(
                context,
                mode=mode,
                api_key=_setting("OPENAI_API_KEY"),
                known_tickers=[a["ticker"] for a in ASSETS],
                demo_store=_demo_store(),
                limiter=_limiter(),
                log_sink=_log_writer(key),
            )
        st.session_state[state_key] = (context_key, result)
        if mode == llm_service.MODE_LIVE and result.status == llm_service.STATUS_OK and _recording():
            try:
                llm_service.record_demo_entry(DEMO_PATH, context, result.data)
                _demo_store.clear()
            except OSError:
                st.caption("Não foi possível gravar a resposta de demonstração neste ambiente.")

    saved = st.session_state.get(state_key)
    if saved and saved[0] == context_key:  # só mostra se os dados da tela não mudaram
        _show(saved[1], context)
