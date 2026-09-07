# Requisitos — Fase 2 do Argos DataLab

## Objetivo

Evoluir o MVP para oferecer indicadores técnicos, métricas de risco,
comparação entre ativos e visualizações analíticas.

## Requisitos funcionais

- RF01: Permitir informar e analisar múltiplos símbolos.
- RF02: Comparar retornos normalizados entre ativos.
- RF03: Calcular médias móveis simples e exponenciais.
- RF04: Calcular RSI.
- RF05: Calcular MACD e linha de sinal.
- RF06: Calcular retorno acumulado.
- RF07: Calcular retorno médio por período.
- RF08: Calcular volatilidade anualizada.
- RF08A: Usar fator de anualização como simplificação configurável por mercado e frequência, sem assumir que 252 vale para todos os ativos; para criptoativos, em cenários futuros, o valor pode ser 365 em razão da operação diária.
- RF09: Calcular máximo drawdown.
- RF10: Calcular índice de Sharpe com taxa livre de risco configurável.
- RF11: Exibir gráficos e tabelas comparativas.
- RF12: Exportar dados e métricas da análise.
- RF13: Validar símbolos, períodos e frequência antes do cálculo.
- RF14: Informar que indicadores são descritivos e não recomendação.
- RF15: Documentar claramente que a premissa de 252 dias úteis por ano é um atalho para mercados de ações e não uma regra universal para ativos que operam 24/7.

## Diretrizes de comparação entre ativos

### 1. Comparação base 100

Para comparar o desempenho relativo de múltiplos ativos, o sistema deve normalizar o primeiro valor observado de cada série para 100. A partir daí, o valor em cada período representa a evolução relativa ao início do intervalo.

Exemplo:
- BTC-USD: 100 -> 120
- AAPL: 100 -> 110
- USD/BRL: 100 -> 105

Interpretação:
- BTC-USD valorizou 20%.
- AAPL valorizou 10%.
- USD/BRL valorizou 5%.

### 2. Retorno acumulado

A tabela de comparação deve usar a fórmula:

Retorno total = (último valor / primeiro valor) - 1

Exemplos em percentual:
- 0.20 -> 20,00%
- -0.15 -> -15,00%

A conversão para percentual deve ser feita no front-end ou no módulo de resumo para facilitar a leitura e comparação entre ativos.

### 3. Risco e retorno

Após a entrega do módulo de métricas de risco, o resumo comparativo deve incluir as seguintes métricas:

| Métrica | Por que faz sentido |
|---|---|
| Retorno total | Mostra o desempenho no período |
| Retorno médio | Mostra o comportamento médio por período |
| Volatilidade | Mostra a dispersão dos retornos |
| Drawdown máximo | Mostra a maior perda desde um pico |
| Percentual positivo | Mostra a frequência de retornos positivos |
| Sharpe | Pode entrar depois, quando a taxa livre de risco estiver definida |

A comparação mais útil não é apenas "qual ativo cresceu mais?", mas sim:

> Qual ativo teve melhor retorno, com qual volatilidade e com qual perda máxima intermediária?

### 4. Observação sobre o fator 252

Para ações, 252 é uma aproximação comum de dias úteis de negociação por ano. Contudo, esse valor deve ser tratado como simplificação configurável e não como regra universal para todos os mercados. Em criptoativos, que operam todos os dias, será possível, futuramente, permitir um fator como 365, sem aplicar a mesma premissa sem ressalva a todos os ativos.

## Gerenciamento de datas

Ações, ETFs, câmbio e criptoativos possuem calendários diferentes:

- Ações e ETFs não negociam em fins de semana e feriados.
- Criptoativos podem registrar preços em todos os dias.
- Ativos podem ter dados ausentes em determinadas janelas.
- Algumas fontes retornam datas em fusos diferentes.

Por isso, a comparação precisa tratar datas explicitamente.

### Regra adotada

A implementação proposta usa:

```python
how="outer"
```

na união de séries. Isso cria uma tabela com todas as datas disponíveis em qualquer ativo.

Exemplo:

```text
Data    BTC-USD    AAPL
sexta   valor      valor
sábado  valor      NaN
domingo valor      NaN
segunda valor      valor
```

Isso preserva o fato de que AAPL não teve negociação no fim de semana.

### Regra para correlação

A correlação do Pandas ignora, por pares, as datas sem dados nos dois ativos. Assim, BTC-USD e AAPL serão comparados apenas nas datas em que os dois possuam retornos válidos.

Não preencha fins de semana de ações com valores inventados no MVP. Uma futura versão poderá oferecer opções explícitas de alinhamento, como:

- Somente datas comuns.
- Preenchimento com último valor disponível.
- Reamostragem mensal.

A implementação proposta evita criar dados artificiais e mantém transparência metodológica. A própria documentação e histórico do yfinance reconhecem desafios de alinhamento de índices quando ativos possuem calendários, dados vazios ou fusos diferentes.

### Ajuste importante sobre frequência

Reutilize a mesma função atual:

```python
aggregate_by_frequency()
```

Fluxo por ativo:

```text
download_active_data()
        ↓
prepare_dataframe()
        ↓
aggregate_by_frequency()
        ↓
select_primary_variable()
        ↓
calculate_returns()
        ↓
calculate_drawdown()
```

Na comparação, os dados devem ser agregados antes de serem unidos.

## Requisitos não funcionais

- RNF01: Cálculos devem estar isolados em módulos testáveis.
- RNF02: Funções de dados e cálculos devem usar cache quando adequado.
- RNF03: O sistema deve tratar falhas de consulta sem exibir traceback.
- RNF04: Gráficos devem ter título, unidade, período e legenda claros.
- RNF05: A interface deve funcionar em tela desktop e permanecer legível.
- RNF06: Mudanças não podem quebrar o MVP já publicado.