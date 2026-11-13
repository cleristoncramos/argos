"""
Período e eventos históricos nos gráficos de série temporal.

Recurso trazido do painel do projeto "Previsão Financial Risk" a pedido do
desenvolvedor (13/11/2026): o usuário vê, como linhas pontilhadas, o que acontecia
no mundo no período carregado. O período é sempre o da barra lateral; não há
recorte próprio dentro da página.

- A base do sistema fica em data/eventos_historicos.csv: data, categoria, título,
  descrição, fonte, endereço da fonte e ativos. Etapa 5 da DL2 (DL2-D): todo evento
  do sistema tem fonte. A coluna "ativos" (tickers separados por espaço) liga um
  evento a ativos específicos (categoria "Do ativo"); vazia, o evento vale para todos.
- O usuário pode incluir eventos próprios (categoria "Seus eventos"), baixá-los
  em CSV e carregá-los de novo numa próxima visita.
- Os eventos são contexto, não explicação: o sistema não afirma que um evento
  causou uma alta ou uma queda (DL2-D).

Funções puras, sem Streamlit.
"""

from __future__ import annotations

import io
from datetime import date
from pathlib import Path
from typing import Iterable

import pandas as pd

EVENTS_FILE = Path(__file__).resolve().parent.parent / "data" / "eventos_historicos.csv"
EVENT_COLUMNS = ["data", "categoria", "titulo", "descricao", "fonte", "url", "ativos"]
TEXT_COLUMNS = ["descricao", "fonte", "url", "ativos"]
USER_CATEGORY = "Seus eventos"
ASSET_CATEGORY = "Do ativo"
# Ordem fixa das categorias (legenda e filtro) e cor de cada uma.
CATEGORY_COLORS = {
    "Mercado e crises": "#b91c1c",
    "Saúde": "#c2410c",
    "Política": "#7c3aed",
    "Mundo": "#0f766e",
    ASSET_CATEGORY: "#1d4ed8",
    USER_CATEGORY: "#111827",
}

EVENTS_NOTE = (
    "As linhas pontilhadas marcam acontecimentos que mexeram com o mercado, para dar "
    "contexto ao período analisado. Elas não indicam que o evento causou a variação do "
    "ativo: o preço muda por muitos motivos ao mesmo tempo."
)
CSV_FORMAT_ERROR = (
    "O arquivo precisa das colunas data e titulo (e, opcionalmente, descricao), "
    "separadas por ponto e vírgula."
)


def empty_events() -> pd.DataFrame:
    return pd.DataFrame({column: pd.Series(dtype="object") for column in EVENT_COLUMNS}).astype(
        {"data": "datetime64[ns]"}
    )


def load_events(path: Path = EVENTS_FILE) -> pd.DataFrame:
    """Base de eventos do sistema; vazia se o arquivo não existir."""
    if not Path(path).exists():
        return empty_events()
    events = pd.read_csv(path, encoding="utf-8", dtype=str).reindex(columns=EVENT_COLUMNS)
    events["data"] = pd.to_datetime(events["data"])
    events[TEXT_COLUMNS] = events[TEXT_COLUMNS].fillna("")
    return events


def user_events_frame(records: Iterable[dict]) -> pd.DataFrame:
    """Eventos do usuário (lista de dicionários guardada na sessão)."""
    records = list(records)
    if not records:
        return empty_events()
    events = pd.DataFrame(records).reindex(columns=EVENT_COLUMNS)
    events["data"] = pd.to_datetime(events["data"])
    events[TEXT_COLUMNS] = events[TEXT_COLUMNS].fillna("")
    return events


def combine_events(base: pd.DataFrame, user: pd.DataFrame) -> pd.DataFrame:
    frames = [frame for frame in (base, user) if not frame.empty]
    if not frames:
        return empty_events()
    events = pd.concat(frames, ignore_index=True)
    events["data"] = pd.to_datetime(events["data"])
    return events


def available_categories(events: pd.DataFrame) -> list[str]:
    """Categorias presentes, na ordem fixa de CATEGORY_COLORS."""
    present = set(events["categoria"])
    return [category for category in CATEGORY_COLORS if category in present]


def applies_to(events: pd.DataFrame, ticker: str | None) -> pd.Series:
    """Eventos gerais valem para todos; eventos de ativos, só para os tickers listados."""
    wanted = str(ticker or "").strip().upper()
    return events["ativos"].map(lambda value: not str(value).strip() or wanted in str(value).upper().split())


def filter_events(
    events: pd.DataFrame, categories: Iterable[str], start: date, end: date, ticker: str | None = None
) -> pd.DataFrame:
    days = events["data"].dt.date
    keep = events["categoria"].isin(list(categories)) & (days >= start) & (days <= end)
    return events[keep & applies_to(events, ticker)]


def event_traces(events: pd.DataFrame, y_min: float, y_max: float) -> list[dict]:
    """
    Uma série por categoria (liga e desliga pela legenda): cada evento é uma linha
    vertical pontilhada, com título e descrição ao passar o mouse.
    """
    traces = []
    order = list(CATEGORY_COLORS)
    for category in sorted(events["categoria"].unique(), key=lambda c: order.index(c) if c in order else 99):
        group = events[events["categoria"] == category].sort_values("data")
        xs, ys, texts = [], [], []
        for _, event in group.iterrows():
            text = f"<b>{event['titulo']}</b> ({event['data']:%d/%m/%Y})"
            if isinstance(event["descricao"], str) and event["descricao"].strip():
                text += f"<br>{event['descricao']}"
            if event["fonte"]:
                text += f"<br><i>Fonte: {event['fonte']}</i>"
            xs += [event["data"], event["data"], None]
            ys += [y_min, y_max, None]
            texts += [text, text, ""]
        traces.append(dict(
            type="scatter",
            x=xs,
            y=ys,
            mode="lines",
            name=category,
            legendgroup=f"evento_{category}",
            line=dict(color=CATEGORY_COLORS.get(category, "#111827"), width=1.2, dash="dot"),
            opacity=0.75,
            customdata=texts,
            hovertemplate="%{customdata}<extra></extra>",
            connectgaps=False,
            showlegend=True,
        ))
    return traces


def new_user_event(day: date, title: str, description: str = "") -> dict:
    """Registro de um evento do usuário. ValueError sem título."""
    title = (title or "").strip()
    if not title:
        raise ValueError("Informe um título para o evento.")
    return {"data": pd.Timestamp(day), "categoria": USER_CATEGORY, "titulo": title,
            "descricao": (description or "").strip(), "fonte": "", "url": "", "ativos": ""}


def parse_user_csv(content: bytes) -> list[dict]:
    """
    Lê um CSV de eventos salvo antes (data;titulo;descricao, datas dd/mm/aaaa).
    ValueError com CSV_FORMAT_ERROR se faltar coluna ou se uma data for inválida.
    """
    try:
        loaded = pd.read_csv(io.BytesIO(content), sep=";", encoding="utf-8-sig", dtype=str)
        loaded.columns = [column.strip().lower() for column in loaded.columns]
        loaded["data"] = pd.to_datetime(loaded["data"], format="%d/%m/%Y")
        loaded["titulo"] = loaded["titulo"].fillna("").str.strip()
    except (KeyError, ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
        raise ValueError(CSV_FORMAT_ERROR) from error
    if "descricao" not in loaded.columns:
        loaded["descricao"] = ""
    loaded["descricao"] = loaded["descricao"].fillna("").str.strip()
    loaded = loaded[loaded["titulo"] != ""]
    loaded["categoria"] = USER_CATEGORY
    return loaded.reindex(columns=EVENT_COLUMNS).fillna({c: "" for c in TEXT_COLUMNS}).to_dict("records")


def sources_table(events: pd.DataFrame) -> pd.DataFrame:
    """Tabela "Eventos no período e fontes": data, categoria, evento, fonte e endereço."""
    ordered = events.sort_values("data")
    return pd.DataFrame({
        "Data": ordered["data"].dt.strftime("%d/%m/%Y"),
        "Categoria": ordered["categoria"],
        "Evento": ordered["titulo"],
        "Fonte": ordered["fonte"].replace("", "Evento seu (sem fonte)"),
        "Endereço": ordered["url"].replace("", None),
    }).reset_index(drop=True)


def user_events_csv(events: pd.DataFrame) -> bytes:
    """CSV dos eventos do usuário (ponto e vírgula, datas dd/mm/aaaa), pronto para baixar."""
    out = events.assign(data=events["data"].dt.strftime("%d/%m/%Y"))[["data", "titulo", "descricao"]]
    return out.to_csv(sep=";", index=False).encode("utf-8-sig")
