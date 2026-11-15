"""
Apoio à página Configurações: padrões da análise, situação do ambiente e resumo do
arquivo SQLite do catálogo local.

- Padrões da análise: período, frequência e taxa livre de risco que a barra lateral
  e o módulo Risco e Retorno usam ao abrir. Valem na sessão do navegador e, numa
  instalação local com o catálogo editável, ficam salvos no SQLite.
- Situação do ambiente: o que cada variável de ambiente do Argos está fazendo nesta
  execução. Chaves de API nunca aparecem, nem se estão definidas.
- Resumo do arquivo: caminho, tamanho, data da última alteração e linhas por tabela.

Sem Streamlit: a interface fica em app/views/configuracoes.py.
"""

from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping, Optional

from core.config import config
from core.demo_mode import ENV_VAR as DEMO_ENV_VAR
from core.demo_mode import is_demo_mode
from core.edu_layer import ENV_VAR as EDU_ENV_VAR
from core.edu_layer import edu_layer_enabled
from core.llm_mode import MODE_DEMO, MODE_LIVE, resolve_mode
from core.local_catalog import DB_ENV_VAR, ENV_VAR as CATALOG_ENV_VAR
from core.local_catalog import db_path, editable_enabled
from core.periods import CUSTOM_PERIOD, DEFAULT_PERIOD, PERIOD_OPTIONS

# ------------------------------------------------------------------ padrões da análise
PERIOD_SETTING = "periodo_padrao"
FREQUENCY_SETTING = "frequencia_padrao"
RISK_FREE_SETTING = "taxa_livre_risco_padrao"

DEFAULT_FREQUENCY = "Mensal"
DEFAULT_RISK_FREE_PCT = 0.0
MAX_RISK_FREE_PCT = 100.0

# "Personalizado" depende de datas escolhidas na hora; não serve de padrão.
DEFAULT_PERIOD_CHOICES = tuple(p for p in PERIOD_OPTIONS if p != CUSTOM_PERIOD)
DEFAULT_FREQUENCY_CHOICES = tuple(config.FREQUENCIES)


@dataclass(frozen=True)
class AnalysisDefaults:
    period: str = DEFAULT_PERIOD
    frequency: str = DEFAULT_FREQUENCY
    risk_free_pct: float = DEFAULT_RISK_FREE_PCT


ARGOS_DEFAULTS = AnalysisDefaults()


def clean_period(value: Optional[str]) -> str:
    return value if value in DEFAULT_PERIOD_CHOICES else DEFAULT_PERIOD


def clean_frequency(value: Optional[str]) -> str:
    return value if value in DEFAULT_FREQUENCY_CHOICES else DEFAULT_FREQUENCY


def clean_risk_free(value) -> float:
    """Taxa anual em %, entre 0 e 100; texto inválido volta ao padrão do Argos."""
    try:
        number = float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return DEFAULT_RISK_FREE_PCT
    if number != number:  # NaN
        return DEFAULT_RISK_FREE_PCT
    return round(min(max(number, 0.0), MAX_RISK_FREE_PCT), 2)


def defaults_from_settings(settings: Mapping[str, Optional[str]]) -> AnalysisDefaults:
    """Padrões a partir das preferências salvas (valores ausentes ou inválidos viram o padrão)."""
    rate = settings.get(RISK_FREE_SETTING)
    return AnalysisDefaults(
        period=clean_period(settings.get(PERIOD_SETTING)),
        frequency=clean_frequency(settings.get(FREQUENCY_SETTING)),
        risk_free_pct=DEFAULT_RISK_FREE_PCT if rate is None else clean_risk_free(rate),
    )


def settings_from_defaults(defaults: AnalysisDefaults) -> dict[str, Optional[str]]:
    """Preferências a gravar; o padrão do Argos é gravado como ausência (None)."""
    return {
        PERIOD_SETTING: None if defaults.period == DEFAULT_PERIOD else defaults.period,
        FREQUENCY_SETTING: None if defaults.frequency == DEFAULT_FREQUENCY else defaults.frequency,
        RISK_FREE_SETTING: None if defaults.risk_free_pct == DEFAULT_RISK_FREE_PCT else f"{defaults.risk_free_pct:g}",
    }


def format_rate(pct: float) -> str:
    return f"{pct:.2f}".replace(".", ",") + "% ao ano"


# ------------------------------------------------------------------ situação do ambiente
def _shown(name: str, env: Mapping[str, str]) -> str:
    value = env.get(name, "").strip()
    return value if value else "(não definida)"


def environment_status(env: Optional[Mapping[str, str]] = None) -> list[dict]:
    """
    Uma linha por variável de ambiente do Argos: valor lido e efeito nesta execução.
    As chaves de API (OPENAI_API_KEY, XAI_API_KEY) ficam de fora de propósito.
    """
    env = os.environ if env is None else env
    demo = is_demo_mode()
    editable = editable_enabled()
    llm = resolve_mode(env.get("ARGOS_LLM_MODE"), demo, env.get("ARGOS_LLM_RECORD", "").strip() == "1")
    if editable:
        catalog_effect = "Ligada: o catálogo pode ser ampliado nesta página."
    elif demo and env.get(CATALOG_ENV_VAR, "").strip():
        catalog_effect = "Desligada pelo modo de demonstração."
    else:
        catalog_effect = "Desligada: catálogo fixo e somente leitura."
    llm_effect = {
        MODE_DEMO: "Respostas salvas e já validadas.",
        MODE_LIVE: "Chamadas à API do modelo de linguagem.",
    }.get(llm, "Desligada.")
    return [
        {"Variável": CATALOG_ENV_VAR, "Valor lido": _shown(CATALOG_ENV_VAR, env),
         "Efeito agora": catalog_effect},
        {"Variável": DB_ENV_VAR, "Valor lido": _shown(DB_ENV_VAR, env),
         "Efeito agora": f"Arquivo do catálogo local: {db_path()}" if editable
         else "Sem efeito: só é usada com a edição do catálogo ligada."},
        {"Variável": DEMO_ENV_VAR, "Valor lido": _shown(DEMO_ENV_VAR, env),
         "Efeito agora": "Ligado: só dados salvos, sem internet." if demo else "Desligado: dados do Yahoo Finance."},
        {"Variável": EDU_ENV_VAR, "Valor lido": _shown(EDU_ENV_VAR, env),
         "Efeito agora": "Textos educativos visíveis." if edu_layer_enabled() else "Textos educativos ocultos; avisos obrigatórios visíveis."},
        {"Variável": "ARGOS_LLM_MODE", "Valor lido": _shown("ARGOS_LLM_MODE", env),
         "Efeito agora": "Explicação assistida: " + llm_effect[0].lower() + llm_effect[1:]},
    ]


# ------------------------------------------------------------------ arquivo SQLite
TABLE_DESCRIPTIONS = (
    ("grupos", "chave, rotulo, classe", "Grupos criados por você, com a classe dos ativos (que define cores e regras de análise)."),
    ("ativos", "ticker, nome, grupo", "Ativos acrescentados, cada um ligado a um grupo do catálogo base ou a um grupo seu."),
    ("preferencias", "chave, valor", "Referência de comparação, período, frequência e taxa livre de risco padrão."),
)


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} bytes"
    return f"{size / 1024:.1f} KB".replace(".", ",")


def file_summary(path: Path | str, counts: Mapping[str, int]) -> dict:
    """Caminho, existência, tamanho e última alteração do arquivo, mais as linhas por tabela."""
    path = Path(path)
    if not path.exists():
        return {"path": str(path), "exists": False, "size": "", "modified": "", "counts": dict(counts)}
    info = path.stat()
    return {
        "path": str(path.resolve()),
        "exists": True,
        "size": format_size(info.st_size),
        "modified": datetime.fromtimestamp(info.st_mtime).strftime("%d/%m/%Y %H:%M"),
        "counts": dict(counts),
    }


def local_assets_csv(records: Iterable[Mapping], labels: Mapping[str, str]) -> bytes:
    """Ativos do catálogo local em CSV (separador ;, UTF-8 com BOM, para abrir no Excel)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", lineterminator="\n")
    writer.writerow(["ticker", "nome", "grupo", "classe"])
    for item in records:
        writer.writerow([item["ticker"], item["name"], labels.get(item["group"], item["group"]), item["class"]])
    return buffer.getvalue().encode("utf-8-sig")
