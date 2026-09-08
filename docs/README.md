# Documentação do Projeto — Argos DataLab

Este diretório organiza o histórico técnico do Argos DataLab em duas fases de desenvolvimento:

- **Fase 1:** consolidação, validação e publicação do MVP.
- **Fase 2:** transformação do MVP em uma plataforma analítica mais robusta.

A aplicação possui finalidade educacional e de pesquisa. Dados históricos, indicadores técnicos e métricas quantitativas não constituem recomendação de investimento.

## Fase 1 — MVP

| Etapa | Documento | Entrega principal |
|---:|---|---|
| 1 | [Consolidação do MVP](fase_1/etapa_1_consolidacao_mvp.md) | Organização da aplicação, núcleo analítico e testes |
| 2 | [Validação de entradas](fase_1/etapa_2_validacao_entradas.md) | Símbolos, datas, períodos e estruturas de dados |
| 3 | [Cache da coleta](fase_1/etapa_3_cache_coleta_dados.md) | Cache de dados históricos por uma hora |
| 4 | [Tratamento de erros](fase_1/etapa_4_tratamento_erros_fonte.md) | Respostas seguras para falhas e retornos inválidos |
| 5 | [Sobre o Projeto](fase_1/etapa_5_sobre_o_projeto.md) | Propósito, escopo e limitações |
| 6 | [Atualização do README](fase_1/etapa_6_atualizacao_readme.md) | Instalação, execução, testes e publicação |
| 7 | [Validação do MVP](fase_1/etapa_7_validacao_mvp.md) | Fluxos funcionais e qualidade dos dados |
| 8 | [Registro de testes](fase_1/etapa_8_registro_testes.md) | Estratégia de qualidade e cobertura |
| 9 | [Publicação](fase_1/etapa_9_publicacao.md) | Deploy no Streamlit Community Cloud |

## Fase 2 — Plataforma analítica

| Etapa | Documento | Entrega principal |
|---:|---|---|
| 0 | [Preparação](fase_2/etapa_0_preparacao.md) | Ambiente, qualidade e planejamento da expansão |
| 1 | [Fundamentos analíticos](fase_2/etapa_1_fundamentos_analiticos.md) | Processamento, retornos, estatísticas e sazonalidade |
| 2 | [Indicadores técnicos](fase_2/etapa_2_indicadores_tecnicos.md) | SMA, EMA, Bollinger, RSI, MACD, candles e volume |
| 3 | [Risco e retorno](fase_2/etapa_3_risco_retorno.md) | Volatilidade, drawdown, Sharpe e distribuição de retornos |
| 4 | [Comparação de ativos](fase_2/etapa_4_comparacao_multiplos_ativos.md) | Base 100, correlação e métricas entre ativos |
| 5 | [Melhorias de visualização](fase_2/etapa_5_melhorias_visualizacoes.md) | Gráficos padronizados, contexto e validação visual |
| 6 | [Integração com a interface](fase_2/etapa_6_integracao_interface.md) | Páginas Streamlit, estado persistente e controles reutilizáveis |
| 7 | [Qualidade, testes e documentação](fase_2/etapa_7_qualidade_testes_documentacao.md) | Pirâmide de testes, `pytest.ini`, cobertura e rastreabilidade |
| 8 | [Validação acadêmica e publicação](fase_2/etapa_8_validacao_academica_publicacao.md) | Cenários, CSVs, evidências visuais e deploy |

## Documentos complementares

- [Integração da interface](etapa_6_integracao_interface.md)
- [Validação acadêmica](etapa_8_validacao_academica.md)
- [Registro de testes](../TESTES.md)
- [Guia do projeto](../README.md)
- [Evidências tabulares](evidencias/)

## Evidências

As evidências tabulares dos cenários de validação ficam em `docs/evidencias/`:

- `cenario_a_aapl/AAPL_dados_tratados.csv`
- `cenario_b_btc/BTC-USD_dados_tratados.csv`
- `cenario_c_usdbrl/USDBRL=X_dados_tratados.csv`
- `cenario_d_comparacao/comparacao_ativos_base_100.csv`
- `cenario_e_risco_retorno/BTC-USD_risco_retorno.csv`
- `cenario_f_indicadores/BTC-USD_indicadores.csv`

As capturas PNG são preservadas localmente e ignoradas pelo Git:

```gitignore
/docs/evidencias/**/*.png
```

## Rastreabilidade

A documentação foi consolidada a partir dos módulos em `app/` e `core/`, da suíte em `tests/`, dos arquivos `README.md` e `TESTES.md`, das evidências CSV e do histórico Git.

Commits relevantes:

- `ff181c0` — `test: ampliar cobertura e documentar qualidade`
- `4d0b62e` — `Added Dev Container Folder`
- `7a54224` — `docs: registrar validação acadêmica e evidências`
- `cccb190` — merge do Pull Request #3 na `main`
