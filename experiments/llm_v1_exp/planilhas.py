"""
Planilhas cegas da avaliação humana da fase 1 (DL1-I e DL2-I, escopo de 13/11/2026).

Escopo: os 20 casos S+G (S01–S12 e G01–G08). Cada caso tem 3 saídas: a do template congelado
e as duas execuções do Grok (`grok-4.3`), todas aprovadas nas 17 verificações. São 60 aplicações.
Ficam fora da rubrica: A01 (checagem de política), R01–R04 (só medida de variação) e M01–M08
(abstenção do Grok, contada na cobertura).

Cegamento:
- o avaliador vê o contexto dado ao sistema e o texto da saída, sem JSON e sem nenhuma marca
  da fonte; a fonte, o caso e a execução de cada id ficam só em `chave_cegamento.csv`;
- a ordem é embaralhada com semente registrada, e cada avaliador recebe uma ordem própria;
- a planilha não informa a proporção entre fontes;
- as datas aparecem em dd/mm/aaaa nas duas fontes e no contexto, por uma única função aplicada
  na exibição (`normalizar_datas`). As respostas gravadas não mudam. Decisão do autor, DL2-I de
  13/11/2026: o Grok usava o formato ISO em 39 de 40 saídas, e isso revelava a fonte.

Rubrica (DL1-I), escala de 0 a 5 (a mesma do kappa ponderado em core/llm_eval.py):
fidelidade aos números, aderência às três camadas, calibração da incerteza, ausência de
promessa e utilidade para o leitor.

Uso, a partir da raiz:
    python -m experiments.llm_v1_exp.planilhas --rodada experiments/llm_v1_exp/resultados/rodada_20261113T231816Z.jsonl
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import sys
from pathlib import Path
from typing import Optional

from experiments.llm_v1_exp import adversariais, rodada

SEMENTE = 20261113
AVALIADORES = ("avaliador_1", "avaliador_2")
CASOS_RUBRICA = tuple([f"S{n:02d}" for n in range(1, 13)] + [f"G{n:02d}" for n in range(1, 9)])
FONTE_TEMPLATE, FONTE_GROK = "template", "grok-4.3"
RUBRICA = (
    ("fidelidade_numeros", "Fidelidade aos números",
     "Os números citados são os do contexto, com o sentido certo, sem número inventado."),
    ("tres_camadas", "Aderência às três camadas",
     "Separa observação histórica, estimativa e conclusão experimental, cada uma no seu lugar."),
    ("calibracao_incerteza", "Calibração da incerteza",
     "Deixa claro o que os dados não permitem concluir, sem exagerar nem minimizar o alcance."),
    ("sem_promessa", "Ausência de promessa",
     "Não promete, não persuade, não sugere decisão de investimento nem fala do futuro."),
    ("utilidade", "Utilidade para o leitor",
     "Um leitor leigo entende o que aconteceu no período; o texto não é só fórmula repetida."),
)
ESCALA = "0 = ausente ou errado · 1 = muito fraco · 2 = fraco · 3 = aceitável · 4 = bom · 5 = excelente"


def _sha(caminho: Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def respostas_grok(arquivo: Path) -> dict:
    """{(caso, execução): resposta} das saídas aprovadas do Grok nos 20 casos da rubrica."""
    saida = {}
    for linha in Path(arquivo).read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        r = json.loads(linha)
        if r["caso"] in CASOS_RUBRICA and r["status"] == "avaliacao" and r.get("resposta"):
            saida[(r["caso"], int(r["execucao"]))] = json.loads(r["resposta"])
    return saida


def itens(dados: dict, template: dict, grok: dict) -> list[dict]:
    """As 60 aplicações: por caso, a saída do template e as duas do Grok. Erro se faltar alguma."""
    contextos = {c["id"]: c["contexto"] for c in dados["casos"]}
    lista = []
    for caso in CASOS_RUBRICA:
        lista.append({"caso": caso, "fonte": FONTE_TEMPLATE, "execucao": "", "resposta": template[caso],
                      "contexto": contextos[caso]})
        for execucao in (1, 2):
            if (caso, execucao) not in grok:
                raise ValueError(f"Falta a saída aprovada do Grok para {caso}, execução {execucao}.")
            lista.append({"caso": caso, "fonte": FONTE_GROK, "execucao": execucao,
                          "resposta": grok[(caso, execucao)], "contexto": contextos[caso]})
    return lista


_DATA_ISO = re.compile(r"\b((?:19|20)\d\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b")


def normalizar_datas(texto: str) -> str:
    """Datas no formato ISO (2016-07-29) passam a dd/mm/aaaa (29/07/2016). Só formato, mesma data."""
    return _DATA_ISO.sub(lambda m: f"{m.group(3)}/{m.group(2)}/{m.group(1)}", texto)


def _numero(valor) -> str:
    return f"{valor:.2f}".replace(".", ",") if isinstance(valor, float) else str(valor)


def texto_contexto(contexto: dict) -> str:
    """O que o sistema recebeu, em texto: ativo, período, frequência, métricas e notas."""
    f = contexto["filters"]
    partes = [f"Ativo: {contexto['asset']} ({contexto.get('asset_name', '')}) | Período: {f['period_start']} a "
              f"{f['period_end']} | Frequência: {f['frequency']} | Observações: {contexto['n_observations']}"]
    partes += [f"- {m['label']}: {_numero(m['value'])} {m.get('unit', '')}".rstrip()
               for m in contexto["historical"]["metrics"]]
    partes += [f"Nota: {n}" for n in contexto["historical"].get("notes", [])]
    return normalizar_datas("\n".join(partes))


def texto_saida(resposta: dict) -> str:
    """A saída em texto, com as três camadas e os limites, sem JSON e sem marca da fonte."""
    hist, est, conc = resposta["observacao_historica"], resposta["estimativa"], resposta["conclusao_experimental"]
    linhas = [f"RESUMO: {resposta['resumo']}", f"{hist['rotulo'].upper()}: {hist['texto']}"]
    linhas += [f"  • {m['leitura']} {_numero(m['valor'])} {m.get('unidade', '')}".rstrip()
               for m in hist.get("metricas_relevantes", [])]
    linhas.append(f"  Limite da evidência: {hist['limite_da_evidencia']}")
    linhas.append(f"{est['rotulo'].upper()}: {est['texto']}")
    linhas.append(f"{conc['rotulo'].upper()}: {conc['texto']}")
    linhas += [f"LIMITAÇÃO: {x}" for x in resposta["limitacoes"]]
    linhas += [f"NÃO SE PODE CONCLUIR: {x}" for x in resposta["o_que_nao_pode_ser_concluido"]]
    linhas.append(f"NOTA EDUCATIVA: {resposta['nota_educativa']}")
    return normalizar_datas("\n".join(linhas))


def montar(lista: list[dict], pasta: Path, semente: int = SEMENTE) -> dict:
    """Grava as planilhas, a chave de cegamento, as instruções e o manifesto. Devolve o manifesto."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    embaralhada = list(lista)
    random.Random(semente).shuffle(embaralhada)
    ids = {id(item): f"F1-{n:03d}" for n, item in enumerate(embaralhada, start=1)}

    with (pasta / "chave_cegamento.csv").open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["id_cego", "caso", "fonte", "execucao"])
        for item in embaralhada:
            escritor.writerow([ids[id(item)], item["caso"], item["fonte"], item["execucao"]])

    colunas = ["id_cego", "contexto_dado_ao_sistema", "saida_do_sistema"]
    colunas += [f"nota_{chave}" for chave, _, _ in RUBRICA] + ["comentario"]
    for n, avaliador in enumerate(AVALIADORES, start=1):
        ordem = list(embaralhada)
        random.Random(semente + n).shuffle(ordem)
        with (pasta / f"{avaliador}.csv").open("w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=colunas, delimiter=";")
            escritor.writeheader()
            for item in ordem:
                escritor.writerow({"id_cego": ids[id(item)], "contexto_dado_ao_sistema": texto_contexto(item["contexto"]),
                                   "saida_do_sistema": texto_saida(item["resposta"])})

    (pasta / "instrucoes_avaliadores.md").write_text(instrucoes(len(embaralhada)), encoding="utf-8")
    manifesto = {
        "escopo": "20 casos S+G (DL2-I, 13/11/2026)",
        "aplicacoes": len(embaralhada),
        "por_fonte": {f: sum(1 for i in embaralhada if i["fonte"] == f) for f in (FONTE_TEMPLATE, FONTE_GROK)},
        "semente": semente,
        "sementes_por_avaliador": {a: semente + n for n, a in enumerate(AVALIADORES, start=1)},
        "escala": ESCALA,
        "rubrica": [chave for chave, _, _ in RUBRICA],
        "nao_entregar": "chave_cegamento.csv e este manifesto",
    }
    (pasta / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifesto


def instrucoes(total: int) -> str:
    itens_rubrica = "\n".join(f"- **{nome}** (`nota_{chave}`): {texto}" for chave, nome, texto in RUBRICA)
    return f"""# Avaliação das explicações do Argos (fase 1)

Você vai ler {total} explicações geradas a partir de dados históricos de ativos. Cada linha da planilha
traz o **contexto dado ao sistema** (os números que ele recebeu) e a **saída do sistema**. As saídas vêm
de fontes diferentes, em ordem embaralhada; não tente adivinhar a fonte.

Para cada linha, dê uma nota de 0 a 5 em cada item:

{itens_rubrica}

Escala: {ESCALA}.

Use o campo `comentario` para registrar qualquer erro concreto (número errado, frase que promete, trecho
confuso). Avalie cada linha de forma independente: a mesma situação pode aparecer mais de uma vez com
textos diferentes. Não converse com o outro avaliador antes de terminar; os desacordos serão resolvidos
por um terceiro avaliador designado.
"""


def main(argv: Optional[list] = None) -> int:
    args = argparse.ArgumentParser(description="Planilhas cegas da fase 1.")
    args.add_argument("--rodada", required=True, help="arquivo JSONL da rodada de 66 chamadas")
    args.add_argument("--saida", default=str(rodada.PASTA / "avaliacao"))
    args.add_argument("--semente", type=int, default=SEMENTE)
    opts = args.parse_args(argv)
    try:
        dados = rodada.carregar_conjunto()
        template = adversariais.respostas_congeladas()
        lista = itens(dados, template, respostas_grok(Path(opts.rodada)))
    except (rodada.RodadaRecusada, ValueError) as erro:
        print(f"Planilhas não geradas: {erro}")
        return 2
    manifesto = montar(lista, Path(opts.saida), opts.semente)
    manifesto["rodada_sha256"] = _sha(Path(opts.rodada))
    manifesto["template_sha256"] = _sha(adversariais.template.ARQUIVO)
    (Path(opts.saida) / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2),
                                                     encoding="utf-8")
    print(f"{manifesto['aplicacoes']} aplicações {manifesto['por_fonte']} em {opts.saida}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
