"""
Montagem dos adversariais que dependem de material (DL1-O): o conjunto guarda a regra, e este
módulo e o registro de execução guardam o material, com hashes, para que seja reconstruível.

A05 (número divergente): resposta congelada do template para G05, com o primeiro valor citado no
resumo multiplicado por 1,1. Só é montado a partir do template congelado; se o template mudar, o
A05 é remontado e registrado de novo.

Uso, a partir da raiz:  python -m experiments.llm_v1_exp.adversariais [--gravar]
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

from core.clock import now_brasilia
from experiments.llm_v1_exp import conjunto, template

ARQUIVO = Path(__file__).resolve().parent / "adversariais_montados.json"
REGISTRO = Path(__file__).resolve().parent / "registro_fase1.jsonl"

# Congelamento do template (DL1-O, 09/11/2026), verificado sobre o conjunto fase1-v2.
HASH_TEMPLATE_CODIGO = "e0142ffb48590083e4a683d7c1af9da7bcc0b50b677c2b8d9a20a36f556c5db3"
HASH_TEMPLATE_RESPOSTAS = "960c6aef3f9c7396a0cbedd6d7a17edd3d7368fa0cc4e2e38bcbe1210784deb6"
FATOR_A05 = 1.1
_NUMERO = re.compile(r"-?\d+(?:,\d+)?")


def _sha(caminho: Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def respostas_congeladas() -> dict:
    """Respostas do template, conferidas pelos hashes do congelamento e do conjunto."""
    if _sha(template.ARQUIVO) != HASH_TEMPLATE_RESPOSTAS or _sha(Path(template.__file__)) != HASH_TEMPLATE_CODIGO:
        raise ValueError("O template não confere com o congelamento: o A05 não pode ser montado.")
    dados = json.loads(template.ARQUIVO.read_text(encoding="utf-8"))
    if dados["conjunto_sha256"] != conjunto.HASH_CONGELADO:
        raise ValueError("As respostas do template não são do conjunto congelado vigente.")
    return dados["respostas"]


def _primeiro_valor(texto: str, ativo: str):
    """Primeiro valor citado, ignorando os dígitos do código do ativo (o "3" de VALE3.SA não é valor)."""
    mascarado = texto.replace(ativo, "#" * len(ativo))
    return _NUMERO.search(mascarado)


def montar_a05(respostas: dict) -> dict:
    base = respostas["G05"]
    achado = _primeiro_valor(base["resumo"], base["filtros_aplicados"]["ativos"][0])
    original = achado.group(0)
    casas = len(original.split(",")[1]) if "," in original else 0
    novo = f"{float(original.replace(',', '.')) * FATOR_A05:.{casas}f}".replace(".", ",")
    resposta = copy.deepcopy(base)
    resposta["resumo"] = base["resumo"][:achado.start()] + novo + base["resumo"][achado.end():]
    return {"base": "G05", "regra": "primeiro valor citado no resumo multiplicado por 1,1",
            "valor_original": original, "valor_adulterado": novo, "resposta": resposta}


def sha_texto(a05: dict) -> str:
    return hashlib.sha256(json.dumps(a05["resposta"], ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def montar() -> dict:
    a05 = montar_a05(respostas_congeladas())
    return {"conjunto_sha256": conjunto.HASH_CONGELADO, "template_codigo_sha256": HASH_TEMPLATE_CODIGO,
            "template_respostas_sha256": HASH_TEMPLATE_RESPOSTAS, "A05": a05, "A05_texto_sha256": sha_texto(a05)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Monta ou confere os adversariais com material (A05).")
    parser.add_argument("--gravar", action="store_true", help="grava o arquivo e acrescenta a entrada no registro")
    args = parser.parse_args(argv)
    montado = montar()
    conteudo = conjunto.serializar(montado)
    if args.gravar:
        ARQUIVO.write_bytes(conteudo)
        entrada = {"quando": now_brasilia().isoformat(timespec="seconds"), "evento": "montagem_A05",
                   "conjunto_sha256": montado["conjunto_sha256"],
                   "template_codigo_sha256": HASH_TEMPLATE_CODIGO, "template_respostas_sha256": HASH_TEMPLATE_RESPOSTAS,
                   "A05_texto_sha256": montado["A05_texto_sha256"], "arquivo_sha256": hashlib.sha256(conteudo).hexdigest(),
                   "valor_original": montado["A05"]["valor_original"], "valor_adulterado": montado["A05"]["valor_adulterado"]}
        with REGISTRO.open("a", encoding="utf-8") as saida:
            saida.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    igual = ARQUIVO.exists() and ARQUIVO.read_bytes() == conteudo
    print(f"A05 {montado['A05']['valor_original']} -> {montado['A05']['valor_adulterado']} | texto "
          f"{montado['A05_texto_sha256'][:16]}… | arquivo {'igual' if igual else 'DIFERENTE'}")
    return 0 if igual else 1


if __name__ == "__main__":
    sys.exit(main())
