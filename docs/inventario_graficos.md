# Inventário de gráficos e roteiros de leitura

Plano 2, Bloco 5, item 5.1. Atualizado em 09/10/2026. Cada gráfico tem um
roteiro fixo em `core/chart_guides.py` (o que mede · o que mostra · principal
cuidado · o que não permite concluir), aberto pelo botão "Como ler este
gráfico" (`app/ui/chart_guide.py`). Os mesmos textos são o conteúdo de reserva
da explicação assistida (Bloco 7).

| Página | Gráfico / bloco | Identificador do roteiro | Caixa "O que significa?" já existente |
| --- | --- | --- | --- |
| Análise Individual | Evolução temporal | `evolucao_temporal` | — |
| Análise Individual | Volatilidade anualizada por mês | `volatilidade_mensal` | `volatilidade` |
| Análise Individual | Variação percentual | `variacao_percentual` | — |
| Análise Individual | Mapa de calor sazonal | `mapa_sazonal` | `sazonalidade` |
| Análise Individual | Média consolidada por mês | `media_mensal` | `sazonalidade` |
| Análise Individual | Recorte por anos e meses (Bloco 2) | `recorte_anos` | — |
| Análise Individual | Janela de retorno (Bloco 2) | `janela_retorno` | — |
| Comparação | Evolução em Base 100 | `base_100` | `base_100`, `retorno` |
| Comparação | Mapa de correlação | `correlacao` | `correlacao` |
| Comparação | Sazonalidade comparada (Bloco 3) | `sazonalidade_comparada` | — |
| Comparação | Retorno móvel (Bloco 6) | `tendencia_retorno_movel` | `retorno` |
| Comparação | Razão de desempenho (Bloco 6) | `tendencia_razao` | — |
| Risco e Retorno | Retorno acumulado | `retorno_acumulado` | — |
| Risco e Retorno | Drawdown | `drawdown` | `drawdown` |
| Risco e Retorno | Distribuição de retornos | `distribuicao_retornos` | — |
| Indicadores Técnicos | Candles | `candles` | — |
| Indicadores Técnicos | Preço, médias móveis e Bollinger | `preco_indicadores` | notas por indicador |
| Indicadores Técnicos | Volume | `volume` | notas por indicador |
| Indicadores Técnicos | RSI | `rsi` | notas por indicador |
| Indicadores Técnicos | MACD | `macd` | notas por indicador |
| Indicadores Técnicos | ATR | `atr` | notas por indicador |
| Indicadores Técnicos | Volatilidade móvel | `volatilidade_movel` | notas por indicador |
| Simulação Histórica | Caminho do valor hipotético | `simulacao_caminho` | — |
| Simulação Histórica | Retorno de cada janela histórica | `simulacao_janelas` | — |

Os recursos do Bloco 6 (tendência) já têm roteiro (item 5.3).

Verificação automática: `tests/test_chart_guides.py` falha se uma página tiver
mais chamadas de `st.plotly_chart` do que roteiros, ou se um roteiro citado não
existir.