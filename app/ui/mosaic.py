"""
Mosaico de ativos da página inicial (revisto em 16/11/2026).

Componente st.components.v2, sem iframe: as logomarcas são botões, e o clique volta
ao Python na mesma sessão, sem recarregar a página. A página inicial então abre a
Análise Individual do ativo com 5 anos e frequência mensal.

- "Todos": quatro faixas que deslizam em sentidos alternados (pausam com o mouse).
- Uma categoria ou uma busca: grade fixa, para escolher com calma.

Os dados (logos, categorias, ordem) vêm de core/mosaic.py.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

import streamlit as st

from core.mosaic import mosaic_data

MOSAIC_KEY = "mosaico_ativos"

HTML = '<div class="mz" data-root></div>'

CSS = """
:host{display:block}
*{box-sizing:border-box;border-radius:0}
.mz{font-family:"Source Sans 3","Source Sans Pro",-apple-system,"Segoe UI",sans-serif;color:#111}
.bar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 20px;margin:0 0 16px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{appearance:none;cursor:pointer;display:inline-flex;align-items:baseline;gap:6px;padding:7px 12px;
  font:600 .82rem/1 inherit;font-family:inherit;color:#2A2A2A;background:#FFFFFF;border:1px solid #D9D5CC;
  transition:background .15s ease,border-color .15s ease,color .15s ease}
.chip small{font:500 .7rem/1 "JetBrains Mono",ui-monospace,Consolas,monospace;color:#8A867E}
.chip:hover{border-color:#111}
.chip[aria-pressed="true"]{background:#111;color:#F7F6F2;border-color:#111;box-shadow:inset 0 -2px 0 #C8102E}
.chip[aria-pressed="true"] small{color:#F2B8C0}
.search{position:relative;flex:0 1 260px;min-width:200px}
.search input{width:100%;padding:8px 10px 8px 32px;font:500 .86rem/1.2 inherit;font-family:inherit;color:#111;
  background:#FFFFFF;border:1px solid #D9D5CC;outline:none}
.search input:focus{border-color:#111;box-shadow:inset 0 -2px 0 #C8102E}
.search svg{position:absolute;left:10px;top:50%;transform:translateY(-50%);width:14px;height:14px;stroke:#8A867E}
.stage{position:relative}
.lanes{display:flex;flex-direction:column;gap:10px;
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent);
          mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}
.lane{overflow:hidden;padding:3px 0 7px}
.track{display:flex;gap:10px;width:max-content;animation:slide var(--d) linear infinite;animation-direction:var(--dir)}
.lanes:hover .track,.lanes:focus-within .track{animation-play-state:paused}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(212px,1fr));gap:10px;padding:3px 0 7px}
.tile{appearance:none;cursor:pointer;position:relative;display:flex;align-items:center;gap:12px;width:228px;
  padding:9px 30px 9px 9px;text-align:left;font-family:inherit;color:inherit;background:#FFFFFF;
  border:1px solid #E4E1DA;box-shadow:0 1px 0 rgba(17,17,17,.03),0 6px 14px -10px rgba(17,17,17,.25);
  transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}
.grid .tile{width:auto}
.tile::after{content:"";position:absolute;left:-1px;right:-1px;bottom:-1px;height:2px;background:var(--c);opacity:.85}
.tile .go{position:absolute;right:10px;top:50%;transform:translate(-4px,-50%);opacity:0;color:#C8102E;
  font:700 .95rem/1 "JetBrains Mono",ui-monospace,monospace;transition:opacity .18s ease,transform .18s ease}
.tile:hover,.tile:focus-visible{transform:translateY(-2px);border-color:#111;outline:none;
  box-shadow:0 14px 26px -14px rgba(17,17,17,.45)}
.tile:hover .go,.tile:focus-visible .go{opacity:1;transform:translate(0,-50%)}
.logo{position:relative;flex:none;width:46px;height:46px;display:grid;place-items:center;overflow:hidden;
  background:#FFFFFF;border:1px solid #E4E1DA}
.logo img.brand{width:78%;height:78%;object-fit:contain}
.logo.flags{display:flex;background:#EFEDE7}
.logo.flags img{flex:1 1 0;min-width:0;height:100%;object-fit:cover}
.logo.flags img+img{border-left:1px solid #FFFFFF}
.logo .tag{position:absolute;left:0;right:0;bottom:0;padding:2px 0 1px;text-align:center;color:#FFFFFF;
  background:rgba(17,17,17,.82);font:700 .5rem/1 "JetBrains Mono",ui-monospace,Consolas,monospace;letter-spacing:.02em}
.logo.mark{color:#FFFFFF;border-color:transparent;font:700 1.02rem/1 "JetBrains Mono",ui-monospace,Consolas,monospace;
  letter-spacing:-.01em;background-image:linear-gradient(160deg,rgba(255,255,255,.18),rgba(255,255,255,0) 55%)}
.logo.mark.l4{font-size:.78rem}.logo.mark.l5{font-size:.62rem}
.txt{display:flex;flex-direction:column;gap:2px;min-width:0}
.tk{font:700 .84rem/1.1 "JetBrains Mono",ui-monospace,Consolas,monospace;letter-spacing:.01em;color:#111}
.nm{font-size:.78rem;line-height:1.15;color:#55524C;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px}
.grid .nm{max-width:none}
.gp{font-size:.66rem;line-height:1;color:#9A968D;text-transform:uppercase;letter-spacing:.08em;white-space:nowrap}
.foot{display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px 16px;margin-top:10px;font-size:.8rem;color:#6A665E}
.foot b{color:#111;font-weight:700}
.empty{padding:28px 0;text-align:center;color:#6A665E;font-size:.9rem;border:1px dashed #D9D5CC;background:#FFFFFF}
@media (max-width:640px){.tile{width:200px}.search{flex:1 1 100%}}
@media (prefers-reduced-motion:reduce){.track{animation:none}}
"""

JS = r"""
export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  const root = parentElement.querySelector("[data-root]");
  if (!root || !data) return;
  const state = root.__mz || (root.__mz = { cat: "todos", q: "" });
  const norm = (s) => String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  };

  function mark(box, text, bg) {
    box.className = "logo mark" + (text.length >= 5 ? " l5" : text.length === 4 ? " l4" : "");
    box.style.background = bg;
    box.replaceChildren(document.createTextNode(text));
  }

  function logo(tile) {
    const spec = tile.logo;
    const box = el("span", "logo");
    if (spec.kind === "mark") { mark(box, spec.text, spec.bg); return box; }
    const fail = () => mark(box, spec.fallback, tile.c);
    if (spec.kind === "img") {
      box.style.background = spec.bg;
      if (spec.bg !== "#FFFFFF") box.style.borderColor = spec.bg;
      const img = el("img", "brand");
      img.alt = ""; img.decoding = "async";  // sem "lazy": nas faixas animadas a imagem não carregava
      img.onerror = fail; img.src = spec.src;
      box.append(img);
      return box;
    }
    box.classList.add("flags");
    for (const src of spec.src) {
      const img = el("img");
      img.alt = ""; img.decoding = "async";  // sem "lazy": nas faixas animadas a imagem não carregava
      img.onerror = fail; img.src = src;
      box.append(img);
    }
    box.append(el("span", "tag", spec.tag));
    return box;
  }

  function tileNode(tile) {
    const btn = el("button", "tile");
    btn.type = "button";
    btn.style.setProperty("--c", tile.c);
    const hint = `Abrir a Análise Individual de ${tile.n} (${tile.t}): ${data.period}, frequência ${data.frequency.toLowerCase()}`;
    btn.title = tile.logo.note ? `${hint}\n${tile.logo.note}` : hint;
    btn.setAttribute("aria-label", hint);
    const txt = el("span", "txt");
    txt.append(el("span", "tk", tile.t), el("span", "nm", tile.n), el("span", "gp", tile.g));
    btn.append(logo(tile), txt, el("span", "go", "→"));
    btn.addEventListener("click", () => setTriggerValue("selected", tile.t));
    return btn;
  }

  function visible() {
    const q = norm(state.q.trim());
    return data.tiles.filter((t) =>
      (state.cat === "todos" || t.cat === state.cat) &&
      (!q || norm(t.t).includes(q) || norm(t.n).includes(q) || norm(t.g).includes(q)));
  }

  function renderStage(stage, foot) {
    const tiles = visible();
    stage.replaceChildren();
    if (!tiles.length) {
      stage.append(el("div", "empty", "Nenhum ativo encontrado. Tente outro nome ou ticker."));
    } else if (state.cat === "todos" && !state.q.trim()) {
      const lanes = el("div", "lanes");
      for (let i = 0; i < data.lanes; i++) {
        const items = tiles.filter((t) => t.lane === i);
        const lane = el("div", "lane");
        const track = el("div", "track");
        track.style.setProperty("--d", `${Math.max(60, items.length * 6.5) + i * 9}s`);
        track.style.setProperty("--dir", i % 2 ? "reverse" : "normal");
        // Conteúdo duplicado: o deslocamento de -50% fecha o ciclo sem salto.
        for (let copy = 0; copy < 2; copy++) {
          for (const t of items) {
            const node = tileNode(t);
            if (copy) { node.tabIndex = -1; node.setAttribute("aria-hidden", "true"); }
            track.append(node);
          }
        }
        lane.append(track);
        lanes.append(lane);
      }
      stage.append(lanes);
    } else {
      const grid = el("div", "grid");
      tiles.forEach((t) => grid.append(tileNode(t)));
      stage.append(grid);
    }
    foot.firstChild.replaceChildren(
      el("b", "", String(tiles.length)),
      document.createTextNode(` de ${data.tiles.length} ativos` + (state.cat === "todos" && !state.q.trim() ? " · passe o mouse para pausar" : "")));
  }

  root.replaceChildren();
  const bar = el("div", "bar");
  const chips = el("div", "chips");
  chips.setAttribute("role", "group");
  chips.setAttribute("aria-label", "Filtrar por categoria");
  const stage = el("div", "stage");
  const foot = el("div", "foot");
  foot.append(el("span"), el("span", "", `Clique em um ativo para abrir a Análise Individual (${data.period}, frequência ${data.frequency.toLowerCase()}).`));

  for (const c of data.categories) {
    const chip = el("button", "chip", c.label);
    chip.type = "button";
    chip.append(el("small", "", String(c.count)));
    chip.setAttribute("aria-pressed", String(c.key === state.cat));
    chip.addEventListener("click", () => {
      state.cat = c.key;
      chips.querySelectorAll(".chip").forEach((n) => n.setAttribute("aria-pressed", String(n === chip)));
      renderStage(stage, foot);
    });
    chips.append(chip);
  }

  const search = el("label", "search");
  search.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke-width="2.4"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>';
  const input = el("input");
  input.type = "search"; input.placeholder = "Buscar por nome ou ticker"; input.value = state.q;
  input.setAttribute("aria-label", "Buscar ativo por nome ou ticker");
  input.addEventListener("input", () => { state.q = input.value; renderStage(stage, foot); });
  search.prepend(input);

  bar.append(chips, search);
  root.append(bar, stage, foot);
  renderStage(stage, foot);
}
"""

_MOSAIC = st.components.v2.component("argos_mosaico_ativos", html=HTML, css=CSS, js=JS)


def render_asset_mosaic(assets: Iterable[Mapping[str, str]]) -> Optional[str]:
    """Desenha o mosaico e devolve o ticker clicado nesta execução (ou None)."""
    result = _MOSAIC(data=mosaic_data(assets), key=MOSAIC_KEY, on_selected_change=lambda: None)
    return getattr(result, "selected", None) or None
