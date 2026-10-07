# Checklist de Pendências — Pós-Reunião 30/09/2026

Lista consolidada das deliberações da reunião com o orientador, organizada por prioridade e fase de execução. Ver `docs/ata_reuniao_2026-09-30.md` para o contexto completo.

**Última atualização:** 07/10/2026 · **Testes:** 276 passando, cobertura de `core/` em 96,87% (última execução registrada, antes dos arquivos entregues em 07/10).

## Como usar este checklist

Legenda de status:

- `[x]` **Concluído e validado** (implementado e confirmado por testes ou por conferência na interface).
- `[~]` **Implementado, aguardando validação** (código entregue, mas ainda sem teste automatizado ou sem conferência visual/aplicação).
- `[ ]` **Pendente**.

Regras:

- Só marcar `[x]` quando o item estiver implementado **e** validado (não apenas codificado).
- Itens de "Prioridade alta" bloqueiam o avanço para as fases seguintes do plano de trabalho.
- Mudanças de escopo devem ser registradas como adendo a este arquivo (ver "Adendo de 07/10/2026"), não como edição silenciosa.

Decisões já tomadas (registro):

- Mantidas as 13 classes/grupos do catálogo; digitação livre de ticker incluída, com a seleção hierárquica como fluxo principal.
- RSI no método de Wilder; Bandas de Bollinger com desvio-padrão amostral (`ddof=1`); RSI de série plana resulta em `NaN`.
- Anualização: √252 para dados diários (52 semanal, 12 mensal), aplicada a todas as classes de ativos para manter comparabilidade.
- Tabelas sem separador de milhar (comportamento atual mantido).
- Sistema posicionado como ferramenta de pesquisa e educação financeira; sem recomendação de investimento.

---

## Prioridade alta

- [ ] Definir escopo acadêmico e pergunta de pesquisa (três formulações candidatas; escolha pendente com o orientador — ver aba/seção "Pendências acadêmicas")
- [~] Adicionar explicações educativas às métricas de risco (Fase 2)
- [~] Revisar e documentar indicadores técnicos (Fase 3) — descrições, fórmulas e limitações em `core/indicator_docs.py`; falta MACD com controles próprios
- [~] Melhorar mensagens sobre histórico disponível (Fase 5)
- [~] Separar claramente análise histórica de recomendação (Fase 1, transversal) — avisos centralizados e lista de frases proibidas testada; revisar a cada nova página
- [x] Corrigir e documentar a seleção de ativos (Fase 0/5) — `docs/catalogo-de-ativos.md` revisado e testado
- [ ] Validar todos os fluxos atuais após alterações (Fase 8, contínuo) — checkpoint em `docs/checkpoint_qualidade.md`
- [~] Implementar e validar digitação livre de ticker (ver Seção 2) — lógica testada (`core/ticker_input.py`); falta conferência final na barra lateral

## Prioridade média

- [~] Reutilizar cards de destaque na comparação (Fase 6)
- [x] Criar glossário educativo (Fase 1/4) — 10 termos, testado
- [~] Criar simulação histórica de aportes (Fase 7) — entregue em 07/10 (`core/simulation.py`, página e testes); aguarda validação do formato com o orientador
- [~] Melhorar tabelas e tooltips (Fase 4)
- [~] Consolidar componentes visuais (Fase 4)
- [~] Adicionar metadados nos gráficos (Fase 5/6)

## Prioridade baixa

- [ ] Revisar nome "Argos DataLab" (Fase 10)
- [ ] Refinar identidade visual (Fase 10)
- [ ] Adicionar mais classes e ativos (Fase 10)
- [ ] Criar modelos avançados de previsão (fora do escopo atual)
- [ ] Integrar dados fundamentais, sentimento ou on-chain (fora do escopo atual)
- [ ] Expandir para recomendação personalizada — **não recomendado nesta fase**

---

## Detalhamento por seção da ata

### 1. Direcionamento geral
- [ ] Registrar no projeto que as funcionalidades atuais são um protótipo evolutivo (selo na interface e texto em "Sobre o Projeto")
- [ ] Definir nome/identidade visual somente após nova conversa com o orientador

### 2. Seleção e catálogo de ativos
- [~] Exibir nome amigável, ticker e descrição em toda seleção de ativo
- [x] Confirmar se as 13 classes são necessárias para a primeira versão → **confirmado: manter as 13**
- [x] Documentar o critério usado para escolher os ativos do catálogo
- [x] Registrar que a seleção atual é amostra inicial, não o universo do mercado (aviso em `core/catalog_notice.py`)
- [x] Avaliar digitação opcional de ticker para usuários avançados → **decidido: incluir nesta fase**
- [~] Implementar campo de digitação livre de ticker (modo alternativo à seleção hierárquica)
- [~] Validar ticker digitado contra o yfinance antes de prosseguir
- [~] Exibir mensagem de erro clara quando o ticker não existir ou não retornar dados
- [~] Manter seleção hierárquica como fluxo principal/padrão para iniciantes

### 3. Período e frequência
- [~] Informar quando o ativo não possui histórico suficiente
- [~] Não sugerir que "10 anos" garante dez anos de dados reais
- [~] Exibir período efetivamente utilizado após a consulta
- [~] Exibir quantidade real de observações
- [~] Diferenciar "período solicitado" de "período disponível"
- [ ] Documentar que criptos e ativos recentes podem ter histórico menor (Fase 9)
- [~] Tratar corretamente ativos com datas de início diferentes — período comum implementado; alinhamento por fim de período (PeriodEnd) pendente de aplicação
- [ ] Avaliar frequências semestral e anual (a configuração atual tem apenas Diário, Semanal e Mensal; depende do orientador)

### 4. Análise Individual
- [~] Exibir fonte dos dados e data da última atualização
- [~] Mensagem quando houver dados insuficientes
- [~] Indicar que lacunas podem vir de indisponibilidade do ativo
- [x] Revisar fallback de logos (URL indisponível → emoji) — coberto por `test_asset_logos.py`
- [~] Confirmar rótulo "anualizada" na volatilidade
- [~] Explicação curta do mapa de calor de sazonalidade
- [ ] Diferenciar retorno mensal de valorização acumulada — `create_monthly_return_matrix` criada em 07/10; falta usá-la no mapa de calor da página
- [~] Tooltip com unidade, período e interpretação

### 5. Indicadores técnicos
- [x] Revisar todos os indicadores hoje disponíveis
- [~] Reduzir ao conjunto priorizado (ver ata) — SMA, EMA, Bollinger, RSI, MACD, ATR, volatilidade móvel e volume
- [x] Descrição simples por indicador
- [x] Fórmula/lógica de cálculo por indicador
- [x] O que o indicador mede
- [x] Limitações do indicador
- [~] Não apresentar indicador como sinal automático de compra/venda
- [x] Separar visualização de geração de sinal
- [ ] Avaliar uso futuro como variável preditiva (depende de hipóteses e variáveis-alvo)
- [x] Criar tabela de features para modelos futuros (`core/features.py`)
- [~] Documentar parâmetros (janelas, períodos)
- [x] Auditar vazamento de informação futura (look-ahead bias) — testes de truncamento
- [x] Testes unitários por indicador

### 6. Indicadores e modelos futuros
- [x] Criar camada separada para features
- [x] Não misturar visualização, sinal e variável preditiva
- [ ] Definir indicadores de entrada dos modelos
- [ ] Definir horizonte de previsão
- [ ] Definir alvo (retorno, direção, volatilidade)
- [ ] Priorizar modelos simples e benchmarks antes de complexos
- [ ] Validação temporal (treino/validação/teste)
- [ ] Não confundir acurácia com rentabilidade (registrar no relatório metodológico)

### 7-8. Risco/Retorno e Educação Financeira
- [~] Exibir data do pior drawdown — função `get_max_drawdown_date` entregue em 07/10; falta integrar à página
- [~] Texto explicativo por métrica (textos prontos na ata)
- [~] Indicar se maior/menor é desejável, com ressalva de contexto
- [~] Exibir unidades (%, R$/US$, índice)
- [~] Explicar taxa livre de risco e fator de anualização
- [~] Indicar limitações de cada métrica
- [x] Criar glossário (retorno, volatilidade, drawdown, Sharpe, correlação, médias móveis, RSI, MACD, Base 100, sazonalidade)
- [~] Separar informação histórica / interpretação estatística / simulação / recomendação
- [~] Eliminar linguagem tipo "compre aqui"/"venda aqui"
- [~] Aviso de que a ferramenta não avalia perfil individual

### 9. Simulação de aportes
- [~] Simulação de aporte hipotético (não personalizado ao perfil real)
- [~] Cenários positivo, negativo, neutro — implementados como pior, mediana e melhor janela histórica
- [~] Comparar aporte único vs. periódico
- [~] Disclaimer de simulação histórica (texto pronto na ata)
- [~] Nunca declarar ativo "barato" ou "caro"

### 10. Comparação de ativos
- [~] Avaliar cards de destaque reaproveitados da Análise Individual
- [~] Exibir metadados dos ativos comparados
- [~] Avisar sobre períodos históricos divergentes entre ativos
- [~] Evitar comparação direta com frequências incompatíveis sem explicação

### 11. Interface
- [ ] Padronizar títulos e subtítulos
- [ ] Reduzir poluição visual
- [~] Evitar DataFrames brutos sem interpretação
- [~] Padronizar cores (retorno positivo/negativo) e casas decimais — separadores brasileiros nos gráficos entregues em 07/10; cores ainda duplicadas entre `core/visualizations.py` e `app/ui/colors.py`
- [ ] Melhorar responsividade da sidebar

### 12. Componentização
- [x] Card de métrica reutilizável
- [x] Componente de explicação educativa reutilizável
- [~] Seleção de ativos unificada entre páginas
- [~] Seletor de período/frequência unificado
- [x] Componente de tabela padrão
- [x] Componente de aviso metodológico
- [~] Cálculos em `core/`, renderização em `app/` — `core/visualizations.py` ainda contém código de apresentação

### 13. Documentação técnica
- [ ] Arquitetura do sistema
- [x] Catálogo de ativos
- [ ] Fontes de dados
- [ ] Tratamento de dados
- [ ] Cálculo de indicadores
- [ ] Cálculo de risco
- [ ] Limitações do yfinance
- [ ] Ativos sem histórico completo
- [ ] Tratamento de dados ausentes
- [ ] Decisões sobre frequência
- [ ] Hipóteses para previsão futura
- [ ] Reforço de que histórico não é previsão

### 14. Validação acadêmica
- [ ] Revisão teórica sobre análise técnica
- [ ] Relacionar indicadores a métodos de análise de dados
- [ ] Formalizar pergunta de pesquisa (três candidatas; falta decidir com o orientador)
- [ ] Definir hipóteses, variáveis-alvo, benchmarks
- [ ] Protocolo de validação temporal
- [ ] Registrar limitações e resultados negativos
- [ ] Relatório metodológico para o orientador

### 15. Qualidade e testes
- [x] Testes para novos indicadores
- [x] Testes para catálogo de ativos
- [x] Testes para logos e fallbacks
- [x] Testes para dados insuficientes
- [x] Testes para ativos sem histórico completo
- [ ] Testes para filtros sem resultado (confirmar se `test_assets.py` já tem caso de filtro vazio)
- [ ] Testes para exportação CSV (exige extrair a geração do CSV para uma função em `core/`)
- [ ] Testes para validação de datas (localizar a regra na barra lateral)
- [x] Manter cobertura ≥ 80% (meta), preservar ~95% (atual: 96,87%)
- [~] Testes de bordas de `comparison.py` e `data_processor.py` (entregues em 07/10)

---

## Adendo de 07/10/2026 — itens incluídos após a ata

### A. Pendências técnicas

Fase 6 (comparação):
- [~] Alinhamento por fim de período (`PeriodEnd`) em `data_processor.py` e `comparison.py` — arquivos entregues, ainda não aplicados (a cobertura mostra a versão antiga de `data_processor.py`)
- [ ] Usar `PeriodEnd` na página de comparação quando a frequência for semanal ou mensal
- [ ] Proteção do Base 100 na página: remover ativos com primeiro valor ≤ 0, com aviso
- [ ] Commit da Fase 6 após aplicar e testar

Fase 7 e navegação:
- [~] Registrar a página "Simulação de Aportes" em `app/main.py` (arquivo entregue)
- [ ] Rodar `python -m pytest` com os testes novos (`test_simulation.py`, `test_review_adjustments.py`, `test_visualizations_br.py`, `test_data_processor_edges.py`, `test_comparison_edges.py`)

Correções da revisão de 07/10 (`risk_metrics.py`, `analyzer.py`, `visualizations.py`, `state.py`):
- [~] Versões corrigidas entregues; falta aplicar e rodar os testes
- [ ] Integrar `get_max_drawdown_date` à página de risco e retorno
- [ ] Trocar `create_year_month_matrix` por `create_monthly_return_matrix` no mapa de calor (ou forçar frequência mensal nessa visualização)
- [ ] Passar a moeda do ativo (`price_label`) aos gráficos de preço
- [ ] Capturar `ValueError` de valores ≤ 0 nas páginas de risco (ex.: petróleo WTI negativo em abril de 2020) com mensagem clara
- [ ] Decidir se volatilidade e retorno médio sem dados passam a retornar `NaN` em vez de `0.0` (exige ajustar testes e exibição)
- [ ] Confirmar com `Select-String` se `sync_asset_widget_state` e `persist_asset_widget_state` são usadas; remover se não forem
- [ ] Decidir sobre o símbolo padrão (`BTC-USD` no estado × placeholder vazio na seleção)
- [ ] Tema: fundos claros fixos em `core/visualizations.py` num app de tema escuro; `COLORS` duplicado em `app/ui/colors.py`

Interface e conteúdo:
- [ ] MACD com controles próprios (hoje reutiliza os períodos das EMAs)
- [ ] Contagens automáticas (ativos, grupos, classes) em "Sobre o Projeto"
- [ ] Padronizar a terminologia "grupos" × "classes"
- [ ] Selo "protótipo evolutivo"

Qualidade (continuação da Fase 8):
- [ ] Cobrir linhas restantes: `assets.py` (331, 343, 351), `data_loader.py` (96, 119, 157), `indicator_docs.py` (114), `indicators_extra.py` (43), `data_availability.py` (107)
- [ ] Atualizar `docs/checkpoint_qualidade.md` a cada fase

### B. Pendências acadêmicas

- [ ] 1. Revisão teórica sobre análise técnica (capítulo de 8 a 15 páginas com referências)
- [ ] 2. Pergunta de pesquisa — escolher entre as formulações A (ferramenta compreensível para leigos), B (plataforma de educação financeira) e C (base reprodutível para análise e previsão); sugestão em discussão: uma como pergunta geral e outra como objetivo específico
- [ ] 3. Matriz de literatura (20 a 30 trabalhos)
- [ ] 4. Hipóteses, variáveis-alvo e horizontes de previsão
- [ ] 5. Benchmarks e modelos simples (regressão, classificação, ARIMA, Random Forest)
- [ ] 6. Protocolo de validação temporal (treino/validação/teste, fora da amostra)
- [ ] 7. Relatório metodológico para o orientador

Ordem de dependência: 2 define 4; 1 e 3 alimentam 4; 4 define 5; 5 define 6; 7 reúne tudo.

### C. Dúvidas para o orientador (registrar a resposta ao lado)

- [ ] Nome "Argos DataLab" e identidade visual: manter ou revisar?
- [ ] As 13 classes/grupos bastam para a primeira versão?
- [ ] O critério de seleção do catálogo está adequado como amostra inicial?
- [ ] Incluir frequências semestral e anual? São estatisticamente adequadas?
- [ ] Confirmar a convenção de anualização (√252 diário) e a taxa livre de risco do Sharpe
- [ ] Aprovar RSI de Wilder, Bollinger com `ddof=1` e RSI plano = `NaN`
- [ ] Quais indicadores serão features futuras de modelos?
- [ ] Horizonte e alvo da previsão: retorno, direção ou volatilidade?
- [ ] Simulação de aportes: formato aprovado? (aporte único × periódico, valor hipotético, janelas históricas, sem recomendação)
- [ ] Estrutura esperada do relatório metodológico
- [ ] Prazo da próxima entrega ou apresentação