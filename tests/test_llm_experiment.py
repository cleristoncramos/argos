"""Pipeline do experimento 7A com cliente simulado (sem rede e sem custo)."""

import csv
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core import llm_prompts, llm_validation
from experiments.llm_7a import analyze, build_cases, make_rating_sheets, run_experiment, runner
from scripts import gerar_dados_demo as gerador

_TMP = []


def _tmp():
    path = tempfile.mkdtemp(prefix="argos_7a_")
    _TMP.append(path)
    return Path(path)


def _fake_fetch(ticker, start, end):
    freq = "D" if ticker == "BTC-USD" else "B"
    dates = pd.date_range(start, pd.Timestamp(end) - pd.Timedelta(days=1), freq=freq)
    seed = sum(ord(c) for c in ticker)
    close = 100 + np.cumsum(np.random.default_rng(seed).normal(0.2, 1.0, len(dates)))
    return pd.DataFrame(
        {"Date": dates, "Open": close - 0.5, "High": close + 1, "Low": close - 1, "Close": close,
         "Adj Close": close, "Volume": 1000.0, "Dividends": 0.0, "Stock Splits": 0.0}
    )


def _package():
    directory = _tmp()
    gerador.build_package(_fake_fetch, gerador.DEFAULT_ASSETS, "2020-01-02", "2026-10-10", directory, "v1", "2026-10-10")
    return directory


def _cases(directory=None):
    return build_cases.build_cases(directory or _package())


# ---------------------------------------------------------------- casos
def test_cases_are_complete_and_valid():
    payload = _cases()
    cases = payload["casos"]
    assert len(cases) >= 14
    assert len({c["id"] for c in cases}) == len(cases)
    kinds = {c["tipo"] for c in cases}
    assert {"normal", "negativo", "dados_insuficientes"} <= kinds
    assert all(c["resposta_esperada"].strip() and c["pontos_obrigatorios"] for c in cases)
    texts = " ".join(c["contexto"]["user_request"]["text"] for c in cases if c["contexto"]["user_request"])
    assert "Seria bom investir em setembro" in texts
    assert payload["prompt_version"] == llm_prompts.PROMPT_VERSION
    assert any(c["sintetico"] for c in cases)
    json.dumps(payload)  # serializável


def test_build_cases_requires_all_assets_and_cli():
    directory = _tmp()
    gerador.build_package(_fake_fetch, gerador.DEFAULT_ASSETS[:4], "2020-01-02", "2026-10-10", directory, "v1", "2026-10-10")
    with pytest.raises(SystemExit):
        build_cases.build_cases(directory)
    good = _package()
    out = _tmp() / "sub" / "cases.json"
    assert build_cases.main(["--directory", str(good), "--out", str(out)]) == 0
    assert len(json.loads(out.read_text(encoding="utf-8"))["casos"]) >= 14


# ---------------------------------------------------------------- respostas simuladas
def test_canned_answers_pass_validation_for_every_case():
    payload = _cases()
    tickers = ["AAPL", "BTC-USD", "PETR4.SA", "^GSPC", "GC=F", "CL=F"]
    for case in payload["casos"]:
        data = runner.canned_answer(case["contexto"])
        result = llm_validation.validate_response(data, case["contexto"], tickers)
        assert result.ok, (case["id"], result.as_dict())


# ---------------------------------------------------------------- chamada
class _Scripted:
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.payloads = []

    def __call__(self, payload, key, timeout):
        self.payloads.append(dict(payload))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _ok(content="{}"):
    return {"choices": [{"message": {"content": content}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 10, "completion_tokens": 5}}


def _case():
    return _cases()["casos"][0]


def test_call_model_removes_unsupported_param():
    t = _Scripted(runner.ApiError(400, "Unsupported parameter: 'reasoning_effort' is not supported"), _ok())
    data, used, removed, latency, attempts = runner.call_model(
        "gpt-5-nano", _case()["contexto"], "k", t, 900, {"reasoning_effort": "minimal"}, sleep=lambda s: None)
    assert removed == ["reasoning_effort"] and used == {} and attempts == 2
    assert "reasoning_effort" in t.payloads[0] and "reasoning_effort" not in t.payloads[1]


def test_call_model_retries_then_succeeds_or_fails():
    sleeps = []
    t = _Scripted(runner.ApiError(429, "limite"), TimeoutError("lento"), _ok())
    assert runner.call_model("gpt-5-mini", _case()["contexto"], "k", t, sleep=sleeps.append)[4] == 3
    assert sleeps == [2, 4]
    t = _Scripted(*[runner.ApiError(500, "erro")] * 5)
    with pytest.raises(RuntimeError):
        runner.call_model("gpt-5-mini", _case()["contexto"], "k", t, sleep=lambda s: None)
    t = _Scripted(runner.ApiError(401, "chave inválida"))
    with pytest.raises(RuntimeError):
        runner.call_model("gpt-5-mini", _case()["contexto"], "k", t, sleep=lambda s: None)
    t = _Scripted(runner.ApiError(400, "Unsupported parameter"))
    with pytest.raises(RuntimeError):  # nada a remover
        runner.call_model("gpt-5-mini", _case()["contexto"], "k", t, params={}, sleep=lambda s: None)
    t = _Scripted(TimeoutError("a"), TimeoutError("b"), TimeoutError("c"))
    with pytest.raises(RuntimeError):
        runner.call_model("gpt-5-mini", _case()["contexto"], "k", t, sleep=lambda s: None)


def test_run_one_records_failures_and_invalid_answers():
    case = _case()
    bad = runner.run_one("gpt-5-mini", case, 1, "k", _Scripted(runner.ApiError(401, "x")), 900, {}, [], sleep=lambda s: None)
    assert bad["error"] and not bad["validation"]["ok"] and bad["cost_usd"] == 0
    invalid = runner.run_one("gpt-5-mini", case, 1, "k", _Scripted(_ok("não é json")), 900, {}, [])
    assert invalid["validation"]["failed"][0] == "json_valido"
    assert invalid["cost_usd"] > 0 and invalid["finish_reason"] == "stop"
    empty = runner.run_one("gpt-5-mini", case, 1, "k", _Scripted({"choices": [{"message": {"content": None}}]}), 900, {}, [])
    assert empty["raw"] == "" and empty["input_tokens"] == 0


def test_http_transport_errors():
    import io
    import urllib.error
    import urllib.request

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    real = urllib.request.urlopen
    try:
        urllib.request.urlopen = lambda req, timeout=0: Resp(json.dumps({"ok": 1}).encode())
        assert runner.http_transport({"a": 1}, "k") == {"ok": 1}

        def boom(body):
            def raiser(req, timeout=0):
                raise urllib.error.HTTPError("u", 400, "bad", {}, io.BytesIO(body))
            return raiser

        urllib.request.urlopen = boom(json.dumps({"error": {"message": "ruim"}}).encode())
        with pytest.raises(runner.ApiError, match="ruim"):
            runner.http_transport({}, "k")
        urllib.request.urlopen = boom(b"texto solto")
        with pytest.raises(runner.ApiError, match="texto solto"):
            runner.http_transport({}, "k")
    finally:
        urllib.request.urlopen = real


def test_get_api_key():
    import os
    old = os.environ.pop("OPENAI_API_KEY", None)
    try:
        with pytest.raises(SystemExit):
            runner.get_api_key()
        os.environ["OPENAI_API_KEY"] = " abc "
        assert runner.get_api_key() == "abc"
    finally:
        os.environ.pop("OPENAI_API_KEY", None)
        if old is not None:
            os.environ["OPENAI_API_KEY"] = old


# ---------------------------------------------------------------- experimento completo (simulado)
def _run_dry(payload=None, out=None, **kw):
    payload = payload or _cases()
    out = out or _tmp() / "respostas.jsonl"
    logs = []
    summary = runner.run_experiment(
        payload, out, kw.pop("models", ("gpt-5-mini", "gpt-5-nano")), kw.pop("repetitions", 3), "k",
        runner.fake_transport, dry_run=True, log=logs.append,
        known_tickers=["AAPL", "BTC-USD", "PETR4.SA", "^GSPC", "GC=F"], **kw)
    return payload, out, summary, logs


def test_experiment_dry_run_resume_and_cost_cap():
    payload, out, summary, logs = _run_dry()
    n = len(payload["casos"]) * 2 * 3
    assert summary["executadas"] == n and n >= 72
    assert all(" ok" in line or ": ok" in line for line in logs)
    again = runner.run_experiment(payload, out, ("gpt-5-mini", "gpt-5-nano"), 3, "k", runner.fake_transport, dry_run=True, log=lambda s: None)
    assert again["executadas"] == 0 and again["puladas"] == n
    only = _run_dry(payload, _tmp() / "x.jsonl", models=("gpt-5-mini",), repetitions=1, only_cases=[payload["casos"][0]["id"]])[2]
    assert only["executadas"] == 1
    capped = _run_dry(payload, _tmp() / "c.jsonl", max_cost=0.0005)[2]
    assert capped["interrompido_por_custo"] and capped["executadas"] < n


def test_experiment_logs_failures():
    payload = _cases()

    def bad_transport(p, k, t):
        return _ok("{}")

    logs = []
    out = _tmp() / "f.jsonl"
    runner.run_experiment(payload, out, ("gpt-5-mini",), 1, "k", bad_transport, only_cases=[payload["casos"][0]["id"]], log=logs.append)
    assert "FALHOU" in logs[0]


def test_run_experiment_cli():
    directory = _package()
    cases_path = _tmp() / "cases.json"
    build_cases.main(["--directory", str(directory), "--out", str(cases_path)])
    out = _tmp() / "r" / "respostas.jsonl"
    assert run_experiment.main(["--cases", str(cases_path), "--out", str(out), "--dry-run", "--repetitions", "1"]) == 0
    assert len(out.read_text(encoding="utf-8").splitlines()) == len(json.loads(cases_path.read_text(encoding="utf-8"))["casos"]) * 2
    assert run_experiment.main(["--cases", str(cases_path), "--out", str(out), "--dry-run", "--probe", "--reasoning-effort", ""]) == 0
    assert (out.parent / "sonda.jsonl").exists()
    payload = json.loads(cases_path.read_text(encoding="utf-8"))
    payload["casos"][0]["resposta_esperada"] = ""
    cases_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SystemExit):
        run_experiment.main(["--cases", str(cases_path), "--dry-run"])


# ---------------------------------------------------------------- planilhas e análise
def _fill(path, rater, fill_all, score=4, flags=True):
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig"), delimiter=";"))
    dim = make_rating_sheets.RATERS[rater]["dimensao"]
    for row in rows:
        for d in ("clareza", "correcao", "neutralidade"):
            if d == dim or (row["calibracao"] == "sim" and fill_all):
                row[f"nota_{d}"] = str(score)
        if rater == "tecnico" and flags:
            row.update(correcao_factual_ok="sim", limitacoes_ok="sim", nao_concluir_ok="1", alucinacao="nao")
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def test_sheets_and_analysis_end_to_end():
    payload, out, _, _ = _run_dry()
    records = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    assert make_rating_sheets.select_items(records) == []  # dry-run nunca vai para avaliadores reais
    for r in records:
        r["dry_run"] = False
    records[0]["validation"]["ok"] = False  # resposta reprovada não é avaliada
    cases = {c["id"]: c for c in payload["casos"]}
    sheets = _tmp()
    info = make_rating_sheets.build_sheets(records, cases, sheets)
    assert info["respostas"] == len(records) - 1
    assert round(info["respostas"] * 0.2) == info["calibracao"]
    key = list(csv.DictReader((sheets / "chave_cegamento.csv").open(encoding="utf-8"), delimiter=";"))
    assert len(key) == info["respostas"] and "model" in key[0]
    leigo = list(csv.DictReader((sheets / "leigo.csv").open(encoding="utf-8-sig"), delimiter=";"))
    assert "model" not in leigo[0] and "resposta_esperada" not in leigo[0]
    tecnico = list(csv.DictReader((sheets / "tecnico.csv").open(encoding="utf-8-sig"), delimiter=";"))
    assert tecnico[0]["resposta_esperada"] and "RESUMO:" in tecnico[0]["resposta_do_sistema"]
    assert make_rating_sheets.select_items(records, seed=1)[0]["id_cego"] == "R001"

    # sem notas: critérios humanos ficam pendentes
    merged_none, kappas_none = analyze.merge(records, key, {})
    assert kappas_none == {}
    text = analyze.build_report(merged_none, kappas_none, cases, payload)
    assert "pendente" in text.lower() and "Pendente: sem notas" in text

    for rater in make_rating_sheets.RATERS:
        _fill(sheets / f"{rater}.csv", rater, fill_all=True, score=4)
    ratings = analyze.load_ratings(sheets)
    assert set(ratings) == {"leigo", "tecnico", "neutro"}
    merged, kappas = analyze.merge(records, key, ratings)
    rated = [r for r in merged if "nota" in r]
    assert rated and all(r["nota"] == 4 for r in rated)
    assert set(kappas) == {"clareza", "correcao", "neutralidade"}
    report = analyze.build_report(merged, kappas, cases, payload)
    assert "gpt-5-mini" in report and "Kappa" in report
    assert "violam critério" in report
    assert "ATENÇÃO" not in report

    # nota baixa e alucinação aparecem na regra por resposta
    first = key[0]
    tec = ratings["tecnico"][first["id_cego"]]
    tec["nota_correcao"] = "1"
    tec["alucinacao"] = "sim"
    merged, kappas = analyze.merge(records, key, ratings)
    assert any(r.get("alucinacao") for r in merged)
    assert "| gpt-5" in analyze.build_report(merged, kappas, cases, payload).split("nota ≤ 2")[1]


def test_analyze_validations_and_cli():
    assert analyze._num("") is None and analyze._num("4,0") == 4
    with pytest.raises(ValueError):
        analyze._num("4.5")
    with pytest.raises(ValueError):
        analyze._num("7")
    assert analyze._flag("") is None and analyze._flag("Não") is False and analyze._flag("S") is True
    with pytest.raises(ValueError):
        analyze._flag("talvez")
    assert analyze._fmt(None) == "—" and analyze._fmt(0.123456) == "0.1235" and analyze._fmt("x") == "x"

    payload, out, _, _ = _run_dry(models=("gpt-5-mini",), repetitions=1)
    cases_path = _tmp() / "cases.json"
    cases_path.write_text(json.dumps(payload), encoding="utf-8")
    report_path = _tmp() / "rel.md"
    empty = _tmp()
    assert analyze.main(["--responses", str(out), "--cases", str(cases_path), "--ratings", str(empty), "--out", str(report_path)]) == 0
    assert "ATENÇÃO" in report_path.read_text(encoding="utf-8")

    records = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    for r in records:
        r["dry_run"] = False
    real = _tmp() / "real.jsonl"
    real.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
    sheets = _tmp()
    assert make_rating_sheets.main(["--responses", str(real), "--cases", str(cases_path), "--out", str(sheets)]) == 0
    for rater in make_rating_sheets.RATERS:
        _fill(sheets / f"{rater}.csv", rater, fill_all=True, score=5)
    assert analyze.main(["--responses", str(real), "--cases", str(cases_path), "--ratings", str(sheets), "--out", str(report_path)]) == 0
    assert "ATENÇÃO" not in report_path.read_text(encoding="utf-8")


def test_render_helpers():
    case = _cases()["casos"][-1]
    text = make_rating_sheets.render_context(case["contexto"])
    assert "Pergunta do usuário" in text and "Ativo(s)" in text
    assert "Nota:" in make_rating_sheets.render_context(_cases()["casos"][0]["contexto"])


def test_cleanup():
    for path in _TMP:
        shutil.rmtree(path, ignore_errors=True)


def test_diagnose_summary_and_cli():
    from experiments.llm_7a import diagnose

    payload, out, _, _ = _run_dry(models=("gpt-5-mini",), repetitions=1)
    records = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    records[0]["validation"] = {"ok": False, "failed": ["valores_rastreaveis"], "details": {"valores_rastreaveis": "número fora do contexto: 56"}}
    records[1]["validation"] = {"ok": False, "failed": ["json_valido"]}
    records[1]["raw"] = '{"resumo": "cortado'
    records[1]["finish_reason"] = "length"
    records[2]["validation"] = {"ok": False}
    records[2]["error"] = "HTTP 500"
    text = diagnose.summarize(records)
    assert "Reprovadas: 3 de" in text and "número fora do contexto: 56" in text
    assert "(JSON inválido)" in text and "length): 1" in text and "erro: HTTP 500" in text
    path = _tmp() / "r.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
    dest = _tmp() / "diag.txt"
    assert diagnose.main(["--responses", str(path), "--out", str(dest)]) == 0
    assert "Reprovadas" in dest.read_text(encoding="utf-8")


def test_termos_finds_forbidden_terms_with_field_and_sentence():
    from experiments.llm_7a import termos

    raw = json.dumps({"resumo": "Ok. O ativo está barato.", "o_que_o_grafico_mostra": "x",
                      "limitacoes": ["a"], "o_que_nao_pode_ser_concluido": ["Dizer que vai subir."],
                      "nota_educativa": "n", "metricas_relevantes": [{"leitura": "está caro"}]})
    found = termos.find_terms(raw)
    assert ("resumo", "O ativo está barato.", "barato") in found
    assert any(f[0] == "o_que_nao_pode_ser_concluido" and f[2] == "vai subir" for f in found)
    assert any(f[0] == "metricas_relevantes.leitura" for f in found)
    assert termos.find_terms("{") == []
    negated = json.dumps({"resumo": "Não indica se está barato.", "limitacoes": ["a"]})
    assert termos.find_terms(negated) == []
    path = _tmp() / "r.jsonl"
    record = {"model": "m", "case_id": "c", "repetition": 1, "raw": raw, "validation": {"ok": False, "failed": ["sem_termos_proibidos"]}}
    other = {"model": "m", "case_id": "d", "repetition": 1, "raw": raw, "validation": {"ok": True}}
    path.write_text("\n".join(json.dumps(r) for r in (record, other)), encoding="utf-8")
    assert termos.main(["--responses", str(path)]) == 0


# ---------------------------------------------------------------- casos de reserva
def test_holdout_cases_are_new_and_valid():
    from experiments.llm_7a import holdout_cases, runner

    directory = _package()
    base = {c["id"] for c in _cases(directory)["casos"]}
    payload = holdout_cases.build_holdout(directory)
    cases = payload["casos"]
    assert len(cases) == 8 and payload["conjunto"] == "reserva"
    assert not base & {c["id"] for c in cases}
    assert {c["tipo"] for c in cases} == {"normal", "negativo"}
    for case in cases:
        answer = runner.canned_answer(case["contexto"])
        assert llm_validation.validate_response(json.dumps(answer), case["contexto"], ["AAPL", "BTC-USD"]).passed
    out = _tmp() / "h.json"
    assert holdout_cases.main(["--directory", str(directory), "--out", str(out)]) == 0
    assert len(json.loads(out.read_text(encoding="utf-8"))["casos"]) == 8
    small = _tmp()
    gerador.build_package(_fake_fetch, gerador.DEFAULT_ASSETS[:4], "2020-01-02", "2026-10-10", small, "v1", "2026-10-10")
    with pytest.raises(SystemExit):
        holdout_cases.build_holdout(small)


# ---------------------------------------------------------------- revalidação offline
def test_revalidate_changes_only_validation_and_cli():
    from experiments.llm_7a import revalidar

    payload = _cases()
    case = payload["casos"][0]
    good = json.dumps(runner.canned_answer(case["contexto"]), ensure_ascii=False)
    bad = json.dumps({**runner.canned_answer(case["contexto"]), "resumo": "Compre agora."}, ensure_ascii=False)
    records = [
        {"model": "m", "case_id": case["id"], "repetition": 1, "raw": good, "validation": {"ok": False}},
        {"model": "m", "case_id": case["id"], "repetition": 2, "raw": bad, "validation": {"ok": True}},
    ]
    out, (now_fail, now_pass) = revalidar.revalidate(payload, records)
    assert (now_fail, now_pass) == (1, 1)
    assert out[0]["raw"] == good and out[0]["validation"]["ok"] and not out[1]["validation"]["ok"]
    with pytest.raises(SystemExit):
        revalidar.revalidate(payload, [{"case_id": "inexistente", "raw": ""}])

    directory = _tmp()
    cases_path, src, dst = directory / "cases.json", directory / "in.jsonl", directory / "sub" / "out.jsonl"
    cases_path.write_text(json.dumps(payload), encoding="utf-8")
    src.write_text("\n".join(json.dumps(r) for r in records) + "\n\n", encoding="utf-8")
    assert revalidar.main(["--cases", str(cases_path), "--responses", str(src), "--out", str(dst)]) == 0
    assert len(dst.read_text(encoding="utf-8").splitlines()) == 2


def test_holdout_b_is_new_and_valid():
    from experiments.llm_7a import holdout_cases, runner

    directory = _package()
    used = {c["id"] for c in _cases(directory)["casos"]} | {c["id"] for c in holdout_cases.build_holdout(directory)["casos"]}
    payload = holdout_cases.build_holdout_b(directory)
    cases = payload["casos"]
    assert len(cases) == 8 and payload["conjunto"] == "reserva_b"
    assert not used & {c["id"] for c in cases}
    assert {c["tipo"] for c in cases} == {"normal", "negativo"}
    for case in cases:
        answer = runner.canned_answer(case["contexto"])
        assert llm_validation.validate_response(json.dumps(answer), case["contexto"], ["AAPL", "BTC-USD"]).passed
    out = _tmp() / "b.json"
    assert holdout_cases.main(["--directory", str(directory), "--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["conjunto"] == "reserva_b"
    out_a = _tmp() / "a.json"
    assert holdout_cases.main(["--conjunto", "a", "--directory", str(directory), "--out", str(out_a)]) == 0
    small = _tmp()
    gerador.build_package(_fake_fetch, gerador.DEFAULT_ASSETS[:4], "2020-01-02", "2026-10-10", small, "v1", "2026-10-10")
    with pytest.raises(SystemExit):
        holdout_cases.build_holdout_b(small)


# ---------------------------------------------------------------- combinar execuções
def test_combine_merges_sets_and_filters_models():
    from experiments.llm_7a import combinar, holdout_cases

    directory = _package()
    main_payload = _cases(directory)
    other = holdout_cases.build_holdout_b(directory)
    fp = main_payload["prompt_fingerprint"]

    def rec(case, model):
        return {"model": model, "case_id": case["id"], "repetition": 1, "prompt_fingerprint": fp, "validation": {"ok": True}}

    a = [rec(main_payload["casos"][0], "gpt-5-mini"), rec(main_payload["casos"][0], "gpt-5-nano")]
    b = [rec(other["casos"][0], "gpt-5-mini")]
    payload, records = combinar.combine([main_payload, other], [a, b], ["gpt-5-mini"])
    assert len(payload["casos"]) == len(main_payload["casos"]) + len(other["casos"]) and len(records) == 2
    assert len(combinar.combine([main_payload, other], [a, b])[1]) == 3

    with pytest.raises(SystemExit):
        combinar.combine([main_payload, {**other, "prompt_fingerprint": "outro"}], [a, b])
    with pytest.raises(SystemExit):
        combinar.combine([main_payload, main_payload], [a, b])
    with pytest.raises(SystemExit):
        combinar.combine([main_payload], [[{**a[0], "case_id": "nao_existe"}]])
    with pytest.raises(SystemExit):
        combinar.combine([main_payload], [[{**a[0], "prompt_fingerprint": "antigo"}]])

    folder = _tmp()
    cases_a, cases_b = folder / "a.json", folder / "b.json"
    cases_a.write_text(json.dumps(main_payload), encoding="utf-8")
    cases_b.write_text(json.dumps(other), encoding="utf-8")
    resp_a, resp_b = folder / "ra.jsonl", folder / "rb.jsonl"
    resp_a.write_text("\n".join(json.dumps(r) for r in a) + "\n\n", encoding="utf-8")
    resp_b.write_text(json.dumps(b[0]) + "\n", encoding="utf-8")
    out = folder / "final"
    assert combinar.main(["--responses", str(resp_a), str(resp_b), "--cases", str(cases_a), str(cases_b),
                          "--models", "gpt-5-mini", "--out-dir", str(out)]) == 0
    assert len((out / "respostas_combinado.jsonl").read_text(encoding="utf-8").splitlines()) == 2
    assert json.loads((out / "cases_combinado.json").read_text(encoding="utf-8"))["conjunto"] == "combinado"


# ---------------------------------------------------------------- sinais de alerta nas notas
def test_constant_ratings_are_flagged_and_kappa_is_indeterminate():
    payload = _cases()
    cases = {c["id"]: c for c in payload["casos"]}
    flat = {f"R{i:03d}": {"nota_clareza": "5"} for i in range(1, 13)}
    varied = {f"R{i:03d}": {"nota_correcao": str(3 + i % 3)} for i in range(1, 13)}
    few = {"R001": {"nota_neutralidade": "5"}}
    empty = {"R001": {"nota_neutralidade": ""}}
    alerts = analyze.rater_alerts({"leigo": flat, "tecnico": varied, "neutro": few})
    by = {a["avaliador"]: a for a in alerts}
    assert by["leigo"]["alerta"] and by["leigo"]["parcela"] == 1.0
    assert not by["tecnico"]["alerta"] and not by["neutro"]["alerta"]  # poucas notas: sem alerta
    assert analyze.rater_alerts({"neutro": empty}) == []

    kappas = {"clareza": {"leigo-neutro": float("nan"), "leigo-tecnico": 0.8, "neutro-tecnico": 0.2}}
    text = analyze.build_report([], kappas, cases, payload, alerts)
    assert "indeterminado" in text and "n/d" in text and "abaixo de 0,60" in text
    assert "ALERTA: quase sem variação" in text and "não demonstram qualidade" in text
    text_ok = analyze.build_report([], {}, cases, payload, [by["tecnico"]])
    assert "ALERTA" not in text_ok and "ok" in text_ok


def test_second_round_excludes_rated_items_and_is_all_calibration():
    payload, out, _, _ = _run_dry()
    records = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    for r in records:
        r["dry_run"] = False
    real = _tmp() / "real.jsonl"
    real.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
    cases_path = _tmp() / "cases.json"
    cases_path.write_text(json.dumps(payload), encoding="utf-8")
    first = _tmp()
    assert make_rating_sheets.main(["--responses", str(real), "--cases", str(cases_path), "--out", str(first)]) == 0
    second = _tmp()
    argv = ["--responses", str(real), "--cases", str(cases_path), "--out", str(second),
            "--segunda-rodada", "5", "--excluir-chave", str(first / "chave_cegamento.csv")]
    assert make_rating_sheets.main(argv) == 0
    k1 = list(csv.DictReader((first / "chave_cegamento.csv").open(encoding="utf-8"), delimiter=";"))
    k2 = list(csv.DictReader((second / "chave_cegamento.csv").open(encoding="utf-8"), delimiter=";"))
    ids1 = {(r["model"], r["case_id"], r["repetition"]) for r in k1}
    ids2 = {(r["model"], r["case_id"], r["repetition"]) for r in k2}
    assert len(k2) == min(5, len(records) - len(k1)) and not (ids1 & ids2)
    assert all(r["calibracao"] == "sim" and r["id_cego"].startswith("S") for r in k2)


def test_expected_view_for_refusals_and_third_round_alias():
    normal = {"tipo": "normal", "resposta_esperada": "x", "pontos_obrigatorios": ["a"]}
    assert make_rating_sheets.expected_view(normal) == ("x", ["a"])
    neg = {"tipo": "negativo", "resposta_esperada": 'Responde começando EXATAMENTE por: "Frase fixa." e depois descreve (1).',
           "pontos_obrigatorios": ["velho"]}
    expected, points = make_rating_sheets.expected_view(neg)
    assert "EXCLUSIVAMENTE" in expected and "Frase fixa." in expected and "descreve" not in expected
    assert points == make_rating_sheets.REFUSAL_POINTS_V06
    odd = {"tipo": "negativo", "resposta_esperada": "sem aspas", "pontos_obrigatorios": ["p"]}
    assert make_rating_sheets.expected_view(odd) == ("sem aspas", ["p"])

    payload, out, _, _ = _run_dry()
    records = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    for r in records:
        r["dry_run"] = False
    real = _tmp() / "real.jsonl"
    real.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
    cases_path = _tmp() / "cases.json"
    cases_path.write_text(json.dumps(payload), encoding="utf-8")
    third = _tmp()
    argv = ["--responses", str(real), "--cases", str(cases_path), "--out", str(third), "--terceira-rodada", "4", "--prefixo", "T"]
    assert make_rating_sheets.main(argv) == 0
    key = list(csv.DictReader((third / "chave_cegamento.csv").open(encoding="utf-8"), delimiter=";"))
    assert len(key) == 4 and all(r["id_cego"].startswith("T") and r["calibracao"] == "sim" for r in key)


def test_report_has_complementary_agreement_and_distribution():
    payload, out, _, _ = _run_dry()
    records = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    for r in records:
        r["dry_run"] = False
    real = _tmp() / "real.jsonl"
    real.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
    cases_path = _tmp() / "cases.json"
    cases_path.write_text(json.dumps(payload), encoding="utf-8")
    sheets = _tmp()
    assert make_rating_sheets.main(["--responses", str(real), "--cases", str(cases_path), "--out", str(sheets),
                                    "--terceira-rodada", "6", "--prefixo", "T"]) == 0
    for rater, score in (("leigo", 5), ("tecnico", 4), ("neutro", 5)):
        _fill(sheets / f"{rater}.csv", rater, fill_all=True, score=score)
    report = _tmp() / "rel.md"
    assert analyze.main(["--responses", str(real), "--cases", str(cases_path), "--ratings", str(sheets), "--out", str(report)]) == 0
    text = report.read_text(encoding="utf-8")
    assert "Concordância complementar" in text and "Distribuição das notas" in text
    assert "| clareza | leigo-tecnico | 6 | 0% | 100% |" in text
    assert "| clareza | leigo | 5: 6 |" in text


def test_verificar_rodada_detects_problems_and_passes_clean_sheets():
    from experiments.llm_7a import verificar_rodada as vr

    payload, out, _, _ = _run_dry()
    records = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    for r in records:
        r["dry_run"] = False
    real = _tmp() / "real.jsonl"
    real.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
    cases_path = _tmp() / "cases.json"
    cases_path.write_text(json.dumps(payload), encoding="utf-8")
    first = _tmp()
    argv = ["--responses", str(real), "--cases", str(cases_path), "--out", str(first), "--terceira-rodada", str(len(records)), "--prefixo", "T"]
    assert make_rating_sheets.main(argv) == 0
    assert vr.check(first, "T", []) == []
    assert vr.main(["--planilhas", str(first), "--prefixo", "T"]) == 0
    problems = vr.check(first, "S", [first])
    assert any("prefixo" in p for p in problems) and any("idênticas" in p for p in problems)
    assert vr.main(["--planilhas", str(first), "--prefixo", "S"]) == 1
    # resposta esperada antiga e recusa sem EXCLUSIVAMENTE
    path = first / "tecnico.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig"), delimiter=";"))
    for row in rows:
        if row["caso"].startswith("Negativo"):
            row["resposta_esperada"] = "Responde e depois apenas descreve os dados."
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    problems = vr.check(first, "T", [])
    assert any("EXCLUSIVAMENTE" in p for p in problems) and any("antiga" in p for p in problems)
    # notas já preenchidas
    _fill(first / "leigo.csv", "leigo", fill_all=True, score=5)
    assert any("notas preenchidas" in p for p in vr.check(first, "T", []))
    # ids diferentes, itens fora da calibração, planilha vazia e arquivo ausente
    other = _tmp()
    make_rating_sheets.main(["--responses", str(real), "--cases", str(cases_path), "--out", str(other)])
    assert any("calibração" in p for p in vr.check(other, "R", []))
    (other / "leigo.csv").write_text(
        (other / "leigo.csv").read_text(encoding="utf-8-sig").splitlines()[0] + "\n", encoding="utf-8-sig")
    problems = vr.check(other, "R", [])
    assert any("mesmos ids" in p for p in problems)
    empty = _tmp()
    assert vr.check(empty, "T", []) == ["Falta leigo.csv", "Falta neutro.csv", "Falta tecnico.csv"]
    blank = _tmp()
    for name in ("leigo", "neutro", "tecnico"):
        (blank / f"{name}.csv").write_text("id_cego;calibracao;caso;resposta_do_sistema;resposta_esperada\n", encoding="utf-8-sig")
    assert "Planilhas vazias." in vr.check(blank, "T", [])


def test_exclude_sheets_removes_identical_responses():
    payload, out, _, _ = _run_dry()
    records = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    for r in records:
        r["dry_run"] = False
    real = _tmp() / "real.jsonl"
    real.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
    cases_path = _tmp() / "cases.json"
    cases_path.write_text(json.dumps(payload), encoding="utf-8")
    first = _tmp()
    base = ["--responses", str(real), "--cases", str(cases_path)]
    assert make_rating_sheets.main(base + ["--out", str(first), "--terceira-rodada", "4", "--prefixo", "T"]) == 0
    seen = {r["resposta_do_sistema"].strip() for r in csv.DictReader((first / "leigo.csv").open(encoding="utf-8-sig"), delimiter=";")}
    second = _tmp()
    assert make_rating_sheets.main(base + ["--out", str(second), "--terceira-rodada", "50", "--prefixo", "U",
                                           "--excluir-planilhas", str(first), str(_tmp())]) == 0
    now = {r["resposta_do_sistema"].strip() for r in csv.DictReader((second / "leigo.csv").open(encoding="utf-8-sig"), delimiter=";")}
    assert seen and not (seen & now)
