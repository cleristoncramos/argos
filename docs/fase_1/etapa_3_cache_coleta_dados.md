# Fase 1 — Etapa 3: Cache na Coleta de Dados

## Objetivo

Reduzir chamadas repetidas à fonte externa, melhorar a responsividade da aplicação e diminuir dependência de requisições sucessivas ao Yahoo Finance.

## Implementação realizada

A coleta histórica foi dividida em uma função pública de normalização e uma função interna cacheada.

```python
@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
```

A função pública `download_active_data()` normaliza símbolo, datas e intervalo antes de delegar a consulta à função cacheada.

## Regras do cache

- TTL de 3.600 segundos, equivalente a uma hora.
- Símbolo convertido para maiúsculas e sem espaços externos.
- Intervalo convertido para minúsculas.
- Datas convertidas para texto normalizado.
- Chamadas equivalentes reutilizam a mesma chave de cache.

Exemplos equivalentes:

```text
aapl
 AAPL
AAPL
```

Todos utilizam `AAPL` como símbolo normalizado na chave de cache.

## Arquivos relacionados

- `core/data_loader.py`
- `tests/test_data_loader.py`
- `TESTES.md`
- `README.md`

## Resultado

A aplicação passou a reutilizar resultados recentes de consultas equivalentes, reduzindo latência e volume de chamadas à fonte de dados.
