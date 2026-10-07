"""Geração de arquivos para download (CSV). Sem dependência de UI."""

import re
import unicodedata

import pandas as pd

UTF8_BOM = b"\xef\xbb\xbf"
_INVALID_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def dataframe_to_csv_bytes(
    df: pd.DataFrame | None,
    *,
    sep: str = ",",
    decimal: str = ".",
    bom: bool = False,
) -> bytes:
    """
    Converte um DataFrame em CSV (UTF-8, sem a coluna de índice).

    Os padrões reproduzem o formato usado até agora nas páginas (vírgula como
    separador e ponto decimal). `sep=";"`, `decimal=","` e `bom=True` geram
    um arquivo que o Excel em português abre com as colunas separadas.
    Devolve bytes vazios quando `df` é None.
    """
    if df is None:
        return b""

    encoded = df.to_csv(index=False, sep=sep, decimal=decimal).encode("utf-8")
    return UTF8_BOM + encoded if bom else encoded


def csv_filename(*parts: str) -> str:
    """
    Monta um nome de arquivo .csv seguro a partir de partes de texto.

    Remove acentos e o prefixo "^" de índices, troca caracteres inválidos por
    "_" e junta as partes com "_". Sem nenhuma parte útil, devolve "dados.csv".
    Exemplos: ("^BVSP", "risco") -> "BVSP_risco.csv";
    ("USDBRL=X", "dados") -> "USDBRL_X_dados.csv".
    """
    cleaned = []
    for part in parts:
        text = unicodedata.normalize("NFKD", str(part).strip().lstrip("^"))
        text = text.encode("ascii", "ignore").decode("ascii")
        text = _INVALID_FILENAME_CHARS.sub("_", text).strip("_")
        if text:
            cleaned.append(text)

    return ("_".join(cleaned) or "dados") + ".csv"