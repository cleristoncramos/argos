"""Retornos simples período a período, sem preenchimento de lacunas.

Por que existe: em versões do pandas anteriores à 3.0, ``pct_change()`` usa
``fill_method='pad'`` por padrão e repete o último valor válido sobre lacunas
(NaN). Uma lacuna vira, então, um retorno 0 seguido de um retorno que
acumula todo o intervalo. Esta função calcula ``x_t / x_(t-1) - 1`` e deixa a
lacuna visível: se ``x_t`` ou ``x_(t-1)`` for NaN, o retorno é NaN. O
resultado é o mesmo em qualquer versão do pandas.

Unidade: DECIMAL (0,10 = 10%).
"""

from typing import TypeVar

import pandas as pd

PandasObject = TypeVar("PandasObject", pd.Series, pd.DataFrame)


def simple_returns(data: PandasObject) -> PandasObject:
    """Retorno simples entre observações consecutivas, em decimal.

    Aceita Series ou DataFrame (cada coluna é tratada separadamente). A
    primeira observação não tem retorno (NaN). Lacunas não são preenchidas:
    o retorno do período da lacuna e o do período seguinte ficam NaN.
    """
    return data / data.shift(1) - 1