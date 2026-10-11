"""
Interruptor da camada educativa (condição experimental da avaliação O6).

``ARGOS_EDU_LAYER=off`` oculta os componentes educativos da interface:
"O que significa?", glossário, notas e fichas dos indicadores e o roteiro
"Como ler este gráfico". Os avisos obrigatórios (natureza histórica dos
dados, ausência de recomendação, texto da simulação) NÃO dependem deste
interruptor e aparecem sempre.
"""

import os

ENV_VAR = "ARGOS_EDU_LAYER"
_OFF_VALUES = {"off", "0", "false", "no", "nao", "não", "desligada"}


def edu_layer_enabled() -> bool:
    """True, exceto quando ``ARGOS_EDU_LAYER`` vale off, 0, false, no ou não."""
    return os.environ.get(ENV_VAR, "").strip().lower() not in _OFF_VALUES