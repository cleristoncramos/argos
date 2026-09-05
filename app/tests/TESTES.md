# Registro de Testes

## Ambiente

- Sistema operacional: Windows
- Python: 3.13.15
- Streamlit: 1.63.0
- Pandas: 3.0.5
- yfinance: 1.7.0
- Data do teste: 05/09/2026

## Testes automatizados

Comando executado:

```powershell
pytest -v
```

Resultado:

```text
14 passed in 4.02s
```

## Testes manuais

| Cenário | Parâmetros | Resultado | Status |
|---|---|---|---|
| Bitcoin mensal | BTC-USD; 2020-01-01 a 2020-12-31 | Painel, gráficos e tabela carregados | Aprovado |
| Bitcoin diário | BTC-USD; 2020-01-01 a 2020-01-31 | Painel carregado | Aprovado |
| Símbolo inválido | SIMBOLO-INEXISTENTE-XYZ | Mensagem de erro controlada | Aprovado |