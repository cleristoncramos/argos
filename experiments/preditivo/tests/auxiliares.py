"""Séries sintéticas para os testes (sem rede, com semente fixa)."""

import numpy as np
import pandas as pd


def precos_sinteticos(inicio="2008-01-02", fim="2026-10-30", semente=7) -> pd.DataFrame:
    datas = pd.bdate_range(inicio, fim)
    rng = np.random.default_rng(semente)
    fechamento = 20.0 * np.cumprod(1.0 + rng.normal(0.0003, 0.02, len(datas)))
    abertura = fechamento * (1.0 + rng.normal(0.0, 0.003, len(datas)))
    maxima = np.maximum(abertura, fechamento) * 1.01
    minima = np.minimum(abertura, fechamento) * 0.99
    return pd.DataFrame({"Date": datas, "Open": abertura, "High": maxima, "Low": minima, "Close": fechamento})


def cdi_sintetico(inicio="2007-12-01", fim="2026-11-30", taxa=0.0004) -> pd.DataFrame:
    datas = pd.bdate_range(inicio, fim)
    return pd.DataFrame({"data": datas, "taxa_percentual_ao_dia": taxa * 100, "taxa": taxa})
