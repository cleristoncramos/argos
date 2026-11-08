"""
Trava da avaliação final (protocolo, seções 6.3 e 12).

O período final só pode ser aberto se:
- as 8 condições da seção 12 estiverem marcadas como cumpridas em condicoes_abertura.json;
- os hashes registrados ali (protocolo, nota, configuração, manifesto de dados e
  lista de datas elegíveis) forem iguais aos atuais;
- a avaliação final ainda não tiver sido usada;
- quem executa confirmar explicitamente a abertura.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments.preditivo import config
from experiments.preditivo.registro import hashes_atuais
from experiments.preditivo.util import sha256

CONDICOES_SECAO_12 = (
    "1_decisoes_incorporadas_ao_protocolo",
    "2_versao_consolidada_e_hash_registrados",
    "3_dados_e_configuracao_congelados",
    "4_teste_de_alinhamento_das_datas",
    "5_teste_de_expurgo_externo_e_interno",
    "6_custos_caixa_e_referencias_conferidos",
    "7_nota_metodologica_fechada",
    "8_confirmacao_original_arquivada",
)
DATAS_ELEGIVEIS = config.RAIZ / "datas_elegiveis.json"


class AberturaNegada(RuntimeError):
    pass


def modelo_condicoes() -> dict:
    return {
        "condicoes": {nome: False for nome in CONDICOES_SECAO_12},
        "hashes": {"protocolo": None, "nota": None, "configuracao": None,
                   "manifesto_dados": None, "politica_qualidade": None, "datas_elegiveis": None},
        "observacoes": "Preencher só quando cada condição estiver cumprida e documentada.",
    }


def verificar_abertura(confirmo: bool, condicoes: Path = config.CONDICOES,
                       marca: Path = config.MARCA_FINAL_USADO, datas: Path = DATAS_ELEGIVEIS) -> None:
    motivos = []
    if Path(marca).exists():
        motivos.append("a avaliação final já foi usada (protocolo, seção 11)")
    if not confirmo:
        motivos.append("falta a confirmação explícita de abertura (--confirmo-abertura)")
    if not Path(condicoes).exists():
        motivos.append(f"arquivo de condições ausente: {Path(condicoes).name}")
    else:
        registro = json.loads(Path(condicoes).read_text(encoding="utf-8"))
        pendentes = [n for n in CONDICOES_SECAO_12 if registro.get("condicoes", {}).get(n) is not True]
        if pendentes:
            motivos.append("condições pendentes: " + ", ".join(pendentes))
        atuais = hashes_atuais()
        atuais["datas_elegiveis"] = sha256(datas) if Path(datas).exists() else None
        for nome, valor in atuais.items():
            registrado = registro.get("hashes", {}).get(nome)
            if valor is None or registrado != valor:
                motivos.append(f"hash de {nome} ausente ou diferente do registrado")
    if motivos:
        raise AberturaNegada("Avaliação final não autorizada: " + "; ".join(motivos) + ".")
