import math


def format_number_br(value, prefix=""):
    """
    Formata um valor numérico no padrão brasileiro.

    Exemplos:
    9350.53 -> 9.350,53
    42156.90 -> 42.156,90
    None -> —
    """
    if value is None:
        return "—"

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return "—"

    if math.isnan(numeric_value):
        return "—"

    formatted = f"{numeric_value:,.2f}"

    formatted = (
        formatted
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"{prefix}{formatted}"


def format_brl(value, prefix=""):
    """
    Atalho para format_number_br.

    Use prefix="R$ " quando o valor precisar exibir moeda.
    """
    return format_number_br(value, prefix=prefix)


def format_return_pct(value):
    """
    Formata uma variação percentual decimal no padrão brasileiro.

    Exemplos:
    0.20 -> 20,00%
    -0.15 -> -15,00%
    0.0 -> 0,00%
    None -> —
    """
    if value is None:
        return "—"

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return "—"

    if math.isnan(numeric_value):
        return "—"

    return f"{numeric_value * 100:.2f}%".replace(".", ",")