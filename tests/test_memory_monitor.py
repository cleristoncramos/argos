"""Monitor de RAM da barra lateral (app/ui/memory_monitor.py)."""

from pathlib import Path

from app.ui import memory_monitor as mm

ROOT = Path(__file__).resolve().parents[1]


def test_memory_usage_is_read_from_the_process():
    usage = mm.get_memory_usage()
    assert 1 < usage < 100_000  # MB


def test_share_is_clamped_between_zero_and_one():
    assert mm.memory_share(512) == 0.5
    assert mm.memory_share(2048) == 1.0
    assert mm.memory_share(-1) == 0.0


def test_warning_starts_above_850_mb_of_1_gb():
    assert mm.MEMORY_LIMIT_MB == 1024
    assert not mm.is_near_limit(850)
    assert mm.is_near_limit(850.01)


def test_badge_is_discreet_and_turns_red_near_the_limit():
    ok = mm.memory_badge_html(246.05)
    assert 'class="ram-badge ok"' in ok and "RAM 246 MB" in ok and "24% de 1024 MB" in ok
    high = mm.memory_badge_html(900)
    assert 'class="ram-badge high"' in high and "próximo do limite" in high


def test_psutil_is_in_both_requirements_files():
    for path in ("requirements.txt", "app/requirements.txt"):
        lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
        assert any(line.startswith("psutil") for line in lines), path


def test_monitor_runs_on_every_page():
    # Antes de pg.run(): as páginas podem parar a execução com st.stop().
    main = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert main.index("render_memory_monitor()\n") < main.index("\npg.run()")
