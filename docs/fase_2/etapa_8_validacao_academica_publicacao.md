# Etapa 8 — Validação Acadêmica e Publicação

## Contexto

Este documento define o protocolo de validação acadêmica do Argos DataLab, desenvolvido no contexto do PIBITI UFPI 2026–2027, no plano de trabalho **Análise de Dados para Apoio à Tomada de Decisão em Investimentos no Mercado Financeiro**.

O objetivo é avaliar se a aplicação produz resultados historicamente coerentes, reproduzíveis e adequadamente comunicados para fins educacionais e de pesquisa. O sistema não fornece recomendação de investimento.

## Objetivos da validação

- Verificar a consistência dos dados históricos carregados.
- Confirmar a coerência dos cálculos de retorno, risco e indicadores técnicos.
- Comparar ativos de classes distintas em uma mesma janela temporal.
- Avaliar a interpretação dos resultados em conjunto com as limitações metodológicas.
- Registrar evidências reproduzíveis para discussão com a orientação acadêmica.
- Validar a aplicação publicada no Streamlit Community Cloud.

## Ambiente e versão

| Item | Registro |
|---|---|
| Aplicação | Argos DataLab |
| URL pública | https://argos-datalab.streamlit.app |
| Repositório | https://github.com/cleristoncramos/argos |
| Branch de publicação | `main` |
| Arquivo de entrada | `app/main.py` |
| Fonte de dados | Yahoo Finance, via `yfinance` |
| Frequências disponíveis | Diário, Semanal e Mensal |
| Validação automatizada | 110 testes aprovados |
| Cobertura de `core/` | 93,75% |
| Cobertura mínima exigida | 80% |

## Procedimento geral

Para cada cenário:

1. Registrar os parâmetros utilizados: ativos, datas, frequência e taxa livre de risco.
2. Executar a análise na aplicação publicada.
3. Registrar o total de observações retornadas.
4. Salvar capturas de tela dos gráficos, métricas e tabelas relevantes.
5. Exportar o CSV quando aplicável.
6. Verificar se os resultados apresentados são coerentes com a evolução histórica conhecida do período.
7. Registrar limitações, dados ausentes, diferenças de calendário e observações metodológicas.
8. Repetir o cenário em caso de alteração de código, fonte de dados ou dependências.

## Cenários de validação

### Cenário A — Ação individual: AAPL

| Parâmetro | Valor |
|---|---|
| Ativo | `AAPL` |
| Data inicial | 01/01/2022 |
| Data final | 31/12/2024 |
| Frequência | Semanal |

**Objetivo:** validar uma ação norte-americana com histórico amplo, liquidez elevada e presença de dados em dias úteis.

**Verificações:**

- A série possui datas em ordem crescente.
- A agregação semanal produz valores OHLC e volume coerentes.
- O retorno acumulado é consistente com o primeiro e último fechamento do período.
- O gráfico de preço não apresenta lacunas artificiais além de feriados ou períodos sem negociação.
- O download CSV contém as colunas esperadas.

### Cenário B — Criptoativo: BTC-USD

| Parâmetro | Valor |
|---|---|
| Ativo | `BTC-USD` |
| Data inicial | 01/01/2022 |
| Data final | 31/12/2024 |
| Frequência | Semanal |

**Objetivo:** contrastar um ativo negociado continuamente com uma ação tradicional.

**Verificações:**

- A série possui maior continuidade de datas do que ativos negociados apenas em dias úteis.
- A volatilidade anualizada tende a refletir maior dispersão de retornos em relação a ativos tradicionais, dependendo da janela escolhida.
- Drawdown e retorno acumulado são calculados corretamente.
- Indicadores técnicos são renderizados sem erro.
- Candles são exibidos apenas em frequências diária ou semanal.

### Cenário C — Câmbio: USDBRL=X

| Parâmetro | Valor |
|---|---|
| Ativo | `USDBRL=X` |
| Data inicial | 01/01/2022 |
| Data final | 31/12/2024 |
| Frequência | Semanal |

**Objetivo:** validar uma série cambial e confirmar o símbolo correto do par USD/BRL no provedor de dados.

**Verificações:**

- O símbolo retorna dados válidos.
- A escala de preços é compatível com cotação de dólar por real.
- Datas e frequência são processadas sem erro.
- A série pode ser comparada com AAPL, BTC-USD e SPY.

### Cenário D — Comparação multiclasse

| Parâmetro | Valor |
|---|---|
| Símbolos | `BTC-USD,AAPL,USDBRL=X,SPY` |
| Data inicial | 01/01/2022 |
| Data final | 31/12/2024 |
| Frequência | Semanal |
| Taxa livre de risco anual | 0,00% e 10,00% |

**Objetivo:** comparar desempenho, volatilidade, drawdown, Sharpe e correlação entre classes de ativos distintas.

**Verificações:**

- A comparação contém pelo menos dois ativos válidos.
- A série Base 100 inicia cada ativo em 100 no primeiro período válido.
- A matriz de correlação é simétrica.
- A diagonal da matriz de correlação é igual a 1 quando houver dados suficientes.
- A alteração da taxa livre de risco altera os Sharpes após novo cálculo.
- Alterar a taxa sem clicar em **Comparar ativos** não altera os resultados confirmados.
- O CSV exportado corresponde à tabela Base 100 exibida.

### Cenário E — Risco e retorno com taxa livre de risco

| Parâmetro | Valor |
|---|---|
| Ativo | `AAPL` |
| Data inicial | 01/01/2022 |
| Data final | 31/12/2024 |
| Frequência | Semanal |
| Taxa livre de risco | 0,00% e 10,00% |

**Objetivo:** validar a sensibilidade do índice de Sharpe à taxa livre de risco anual.

**Verificações:**

- Com taxa maior, o Sharpe tende a diminuir quando os demais parâmetros permanecem iguais.
- A legenda apresenta a mesma taxa usada no cálculo.
- Ao navegar para outra página e retornar, taxa, gráficos e métricas permanecem consistentes.
- A taxa exibida na interface não é confundida com a taxa da última análise confirmada.

### Cenário F — Indicadores técnicos

| Parâmetro | Valor |
|---|---|
| Ativo | `AAPL` |
| Data inicial | 01/01/2022 |
| Data final | 31/12/2024 |
| Frequência | Semanal |
| SMA curta / longa | 20 / 50 |
| EMA curta / longa | 12 / 26 |
| RSI | 14 |
| Bollinger | 20 períodos e 2 desvios-padrão |

**Objetivo:** verificar a renderização e a coerência estrutural dos indicadores.

**Verificações:**

- SMA e EMA possuem valores ausentes no início da série de acordo com suas janelas.
- RSI permanece no intervalo de 0 a 100.
- As bandas de Bollinger obedecem à ordem inferior ≤ média ≤ superior.
- O MACD e seu histograma são exibidos.
- Ao selecionar candles com frequência mensal, a aplicação informa a substituição por linha de fechamento.

## Resultado da validação executada

**Data da execução:** 07/09/2026  
**Ambiente validado:** aplicação publicada no Streamlit Community Cloud  
**URL:** https://argos-datalab.streamlit.app

Os cenários A a F foram executados conforme o protocolo definido neste documento. Foram registradas capturas de tela e arquivos CSV exportados em `docs/evidencias/`.

### Síntese dos resultados

| Cenário | Resultado |
|---|---|
| A — AAPL | Dados, agregação semanal, retorno acumulado, tabelas e exportação validados |
| B — BTC-USD | Série de criptoativo, volatilidade, drawdown, indicadores e gráficos validados |
| C — USDBRL=X | Série cambial carregada e processada corretamente |
| D — Comparação multiclasse | Base 100, correlação, métricas por ativo e exportação validadas |
| E — Risco e retorno | Sensibilidade do Sharpe à taxa livre de risco e persistência entre páginas validadas |
| F — Indicadores técnicos | SMA, EMA, RSI, MACD, Bollinger, volume e regra de candles mensais validados |

### Observações metodológicas

- Os dados dependem da disponibilidade e nomenclatura dos símbolos no Yahoo Finance.
- As séries podem conter lacunas decorrentes de feriados, diferenças de calendário e horários de negociação.
- A comparação Base 100 normaliza cada série no primeiro período válido; ela mede desempenho relativo, não preço absoluto.
- Volatilidade e Sharpe dependem da frequência, do fator de anualização e da taxa livre de risco informada.
- Indicadores técnicos descrevem dados históricos e não constituem recomendação de investimento.
- Resultados históricos não garantem desempenho futuro.

## Perguntas para a reunião de orientação

### Escopo e contribuição

1. O conjunto atual de funcionalidades é suficiente para caracterizar o protótipo como um sistema de apoio educacional à análise de investimentos?
2. Quais funcionalidades devem ser priorizadas para a próxima fase: carteira, benchmark, análise fundamentalista, previsão, alertas ou exportação avançada?
3. A comparação entre ações, criptoativos, câmbio e ETF atende ao escopo proposto no plano de trabalho?
4. Há uma classe de ativo adicional que deveria ser incluída como cenário de validação?

### Metodologia e métricas

5. A convenção de 252 períodos anuais para dados diários e 52 para dados semanais está adequada ao objetivo acadêmico?
6. Para BTC-USD, seria metodologicamente preferível anualizar usando 365 períodos no modo diário?
7. A taxa livre de risco deve permanecer como entrada manual ou deve ser vinculada a uma série pública de referência?
8. Quais taxas de referência devem ser usadas em exemplos acadêmicos brasileiros: Selic, CDI, taxa do Tesouro dos EUA ou taxa zero?
9. O uso de retorno simples e logarítmico está suficientemente explicado na interface e na documentação?
10. Quais limitações de dados do Yahoo Finance devem ser explicitadas no relatório final?

### Validação e interpretação

11. Quais resultados devem ser comparados com fontes externas para demonstrar a correção do sistema?
12. É necessário reproduzir algum cenário em uma planilha ou ferramenta externa para validação cruzada?
13. Qual nível de evidência deve ser registrado: capturas de tela, CSVs exportados, planilhas de conferência ou notebook?
14. O intervalo 2022–2024 é adequado como janela principal de análise ou deve ser complementado por outros períodos?
15. Quais critérios devem ser utilizados para avaliar a utilidade didática da aplicação?

### Qualidade e publicação

16. A cobertura automatizada de 93,75% em `core/` é adequada para o estágio atual do projeto?
17. Os testes manuais de estado e navegação são suficientes ou deve ser adotada automação de interface no futuro?
18. A publicação no Streamlit Community Cloud atende às necessidades de demonstração e avaliação?
19. Quais critérios de acessibilidade, usabilidade e apresentação visual devem ser avaliados antes da entrega final?
20. O README, o registro de testes e o protocolo de validação são suficientes para reprodutibilidade acadêmica?

## Evidências a registrar

Para cada cenário validado, armazenar em local apropriado e sem dados sensíveis:

```text
docs/evidencias/
├── cenario_a_aapl/
├── cenario_b_btc/
├── cenario_c_usdbrl/
├── cenario_d_comparacao/
├── cenario_e_risco_retorno/
└── cenario_f_indicadores/
```

Cada pasta pode conter:

- Capturas de tela.
- CSVs exportados.
- Arquivo de parâmetros utilizados.
- Observações e limitações.
- Data de execução.
- Hash do commit ou versão da aplicação.

Não é necessário versionar CSVs grandes, capturas extensas ou arquivos temporários. Para evidências selecionadas, prefira arquivos pequenos, anonimizados e relevantes à reprodução.

## Checklist de conclusão

### Código e qualidade

- [x] Estrutura modular com `app/`, `core/`, `tests/` e `docs/`.
- [x] Consulta, processamento e visualização de dados históricos.
- [x] Indicadores técnicos.
- [x] Métricas de risco e retorno.
- [x] Comparação de ativos.
- [x] Persistência de parâmetros e resultados entre páginas.
- [x] Cache de dados históricos.
- [x] Testes automatizados configurados.
- [x] Cobertura mínima obrigatória de 80%.
- [x] Resultado atual de 110 testes aprovados.
- [x] Cobertura atual de 93,75% em `core/`.
- [x] Testes de carregamento independentes de internet.
- [x] Documentação de testes atualizada.

### Publicação

- [x] Repositório GitHub atualizado.
- [x] Branch `main` configurada como branch de publicação.
- [x] Aplicação publicada no Streamlit Community Cloud.
- [x] URL pública validada.
- [ ] Versão final da Etapa 8 integrada à `main`.
- [ ] Deployment final após integração da Etapa 8 confirmado.

### Validação acadêmica

- [x] Cenário A — AAPL executado e evidências registradas.
- [x] Cenário B — BTC-USD executado e evidências registradas.
- [x] Cenário C — USDBRL=X executado e evidências registradas.
- [x] Cenário D — comparação multiclasse executada e evidências registradas.
- [x] Cenário E — risco e retorno com taxa 0% e 10% executado.
- [x] Cenário F — indicadores técnicos executados.
- [ ] Resultados discutidos com orientação.
- [x] Limitações metodológicas registradas.
- [ ] Próximos passos aprovados pela orientação.

## Resultado esperado da Etapa 8

Ao finalizar esta etapa, o projeto deverá apresentar:

- Uma aplicação acessível e publicada.
- Uma suíte automatizada com cobertura mínima definida.
- Cenários de validação reproduzíveis.
- Evidências organizadas para reunião de orientação.
- Perguntas objetivas para decisão metodológica.
- Checklist de encerramento para o ciclo atual do projeto.