# Fase 1 — Etapa 9: Publicação

## Objetivo

Disponibilizar o MVP em ambiente público para acesso, validação manual e demonstração do projeto.

## Publicação registrada

A aplicação está documentada como publicada no Streamlit Community Cloud:

```text
URL: [https://argos-datalab.streamlit.app](https://argos-datalab.streamlit.app)
Repositório: cleristoncramos/argos
Branch: main
Arquivo principal: app/main.py
```

## Fluxo de entrega

```text
criar ou atualizar branch de trabalho
→ implementar alterações
→ executar python -m pytest
→ validar manualmente
→ commit e push
→ abrir Pull Request
→ merge na main
→ deploy automático no Streamlit Community Cloud
```

## Critérios de validação

- aplicação abre pela URL publicada;
- página principal carrega;
- páginas multipágina podem ser acessadas;
- consultas válidas retornam resultados;
- consultas inválidas produzem mensagens controladas;
- CSVs podem ser baixados;
- dados e métricas são apresentados com aviso de finalidade educacional.

## Arquivos relacionados

- `README.md`
- `TESTES.md`
- `app/main.py`
- `app/pages/`
- histórico Git e Pull Requests

## Resultado

O MVP passou a estar acessível para demonstração e validação fora do ambiente local.
