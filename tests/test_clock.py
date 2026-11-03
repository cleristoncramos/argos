"""Data e hora de Brasília (core/clock.py)."""

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core import clock

APP = Path(__file__).resolve().parents[1] / "app"


def test_now_is_in_brasilia_time():
    now = clock.now_brasilia()
    assert now.utcoffset() == timedelta(hours=-3)
    # O mesmo instante que o relógio UTC do servidor, três horas atrás no mostrador.
    utc = datetime.now(timezone.utc)
    assert abs((now - utc).total_seconds()) < 5
    assert clock.today_brasilia() == clock.now_brasilia().date()


def test_pages_do_not_use_the_server_clock():
    # datetime.now() e date.today() seguem o fuso do servidor (UTC no Streamlit Cloud).
    for path in APP.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                owner = getattr(node.func.value, "id", "")
                assert (owner, node.func.attr) not in {("datetime", "now"), ("date", "today")}, (
                    f"{path.name}:{node.lineno}"
                )
