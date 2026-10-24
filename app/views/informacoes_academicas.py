import os
import sys

import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.ui.landing import (  # noqa: E402
    ACADEMIC_INFO,
    build_academic_header_html,
    build_details_html,
    build_people_html,
    build_technologies_html,
    institutional_logo_uri,
)

st.markdown(
    """
<style>
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.block-container { max-width: 1100px !important; }

.acad-hero { display: flex; align-items: center; gap: 28px; flex-wrap: wrap; padding: 26px 30px; border-radius: 18px;
    background: radial-gradient(700px 300px at 100% 0%, rgba(239, 68, 68, .22), transparent 60%),
                linear-gradient(135deg, #0b1222 0%, #111c33 100%);
    border: 1px solid rgba(148, 163, 184, .2); box-shadow: 0 24px 60px rgba(2, 6, 23, .28); animation: rise .6s ease both; }
.acad-logos { display: flex; align-items: center; gap: 22px; padding: 14px 22px; border-radius: 14px; background: #fff;
    box-shadow: 0 10px 30px rgba(0, 0, 0, .25); }
.acad-logos img { height: 74px; width: auto; display: block; }
.acad-logos img + img { padding-left: 22px; border-left: 1px solid #e2e8f0; }
.acad-ids { flex: 1; min-width: 260px; }
.acad-inst { color: #f8fafc; font-size: 1.45rem; font-weight: 800; letter-spacing: -.02em; line-height: 1.2; }
.acad-center { margin-top: 6px; color: #fca5a5; font-weight: 650; font-size: .98rem; }
.acad-course { margin-top: 4px; color: #cbd5e1; font-size: .92rem; }

.acad-kicker { margin: 34px 0 10px; color: #ef4444; font-size: .72rem; font-weight: 750; letter-spacing: .2em; text-transform: uppercase; }
.acad-title { font-size: clamp(1.5rem, 3vw, 2.1rem); font-weight: 800; letter-spacing: -.03em; line-height: 1.2; animation: rise .6s .1s ease both; }
.acad-title small { display: block; margin-top: 8px; font-size: .95rem; font-weight: 500; letter-spacing: 0; opacity: .7; }

.acad-people { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; animation: rise .6s .18s ease both; }
.acad-person { display: flex; align-items: center; gap: 16px; padding: 20px; border-radius: 16px;
    background: rgba(148, 163, 184, .08); border: 1px solid rgba(148, 163, 184, .25); }
.acad-avatar { flex: none; width: 56px; height: 56px; border-radius: 16px; display: grid; place-items: center;
    color: #fff; font-weight: 800; font-size: 1.15rem; background: linear-gradient(135deg, #ef4444, #b91c1c); }
.acad-label { font-size: .7rem; font-weight: 750; letter-spacing: .14em; text-transform: uppercase; color: #ef4444; }
.acad-name { margin-top: 2px; font-size: 1.08rem; font-weight: 750; }
.acad-role { font-size: .85rem; opacity: .7; }

.acad-table { width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 16px; overflow: hidden;
    border: 1px solid rgba(148, 163, 184, .25); animation: rise .6s .26s ease both; }
.acad-table th, .acad-table td { padding: 13px 18px; text-align: left; vertical-align: top; border: none !important;
    border-bottom: 1px solid rgba(148, 163, 184, .18) !important; font-size: .93rem; }
.acad-table tr:last-child th, .acad-table tr:last-child td { border-bottom: none !important; }
.acad-table th { width: 200px; font-weight: 700; background: rgba(148, 163, 184, .1); }

.acad-techs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; animation: rise .6s .34s ease both; }
.acad-tech { padding: 14px 16px; border-radius: 14px; background: rgba(148, 163, 184, .08); border: 1px solid rgba(148, 163, 184, .25);
    border-left: 3px solid #ef4444; transition: transform .2s ease; }
.acad-tech:hover { transform: translateY(-2px); }
.acad-tech span { display: block; font-weight: 750; }
.acad-tech small { opacity: .7; font-size: .82rem; }

.acad-note { margin-top: 26px; padding: 14px 18px; border-radius: 12px; font-size: .85rem; opacity: .8;
    background: rgba(245, 158, 11, .1); border: 1px solid rgba(245, 158, 11, .35); }

@media (max-width: 760px) {
    .acad-people, .acad-techs { grid-template-columns: 1fr; }
    .acad-logos img { height: 54px; }
    .acad-table th { width: 120px; }
}
</style>
""",
    unsafe_allow_html=True,
)

logos = {
    "UFPI": institutional_logo_uri("UFPI"),
    "CEAD": institutional_logo_uri("CEAD"),
}
st.markdown(build_academic_header_html(logos), unsafe_allow_html=True)

st.markdown(
    f"""
<div class="acad-kicker">Trabalho acadêmico</div>
<div class="acad-title">Argos DataLab
  <small>{ACADEMIC_INFO["work_plan"]}</small></div>
<div class="acad-kicker">Equipe</div>
""",
    unsafe_allow_html=True,
)
st.markdown(build_people_html(), unsafe_allow_html=True)

st.markdown('<div class="acad-kicker">Identificação</div>', unsafe_allow_html=True)
st.markdown(build_details_html(), unsafe_allow_html=True)

st.markdown('<div class="acad-kicker">Tecnologias utilizadas</div>', unsafe_allow_html=True)
st.markdown(build_technologies_html(), unsafe_allow_html=True)

st.markdown(
    '<div class="acad-note">Projeto com finalidade exclusivamente acadêmica, educacional e de '
    "desenvolvimento tecnológico. As análises não constituem recomendação de investimento. "
    "Os logotipos pertencem às respectivas instituições e identificam apenas o vínculo acadêmico.</div>",
    unsafe_allow_html=True,
)

st.write("")
back, start, _ = st.columns([1, 1, 2])
with back:
    if st.button("← Voltar ao início", use_container_width=True):
        st.switch_page("views/home.py")
with start:
    if st.button("Get Started →", type="primary", use_container_width=True):
        st.switch_page("views/analise_individual.py")
