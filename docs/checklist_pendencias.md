# Checklist de Pendências — Pós-Reunião 30/09/2026

Lista consolidada das deliberações da reunião com o orientador, organizada por prioridade e fase de execução. Ver `docs/ata_reuniao_2026-09-30.md` para o contexto completo.

**Última atualização:** 10/10/2026 (adendo do Plano 2 ao final; testes e cobertura da execução de 07/10) · **Testes:** 487 passando, cobertura de `core/` em 100% (execução de 10/10/2026, fim do Bloco 6).

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
- Pergunta de pesquisa: **opção A** (ferramenta de apoio à interpretação, compreensível para usuários sem formação em finanças), escolhida em 07/10/2026. Previsão e validação temporal de modelos ficam como trabalho futuro.

---

## Prioridade alta

- [x] Definir escopo acadêmico e pergunta de pesquisa — opção A escolhida em 07/10/2026 (ver `docs/validacao_academica.md`)
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
- [x] Documentar que criptos e ativos recentes podem ter histórico menor — `docs/fontes_e_tratamento_de_dados.md`, seções 5 e 8
- [~] Tratar corretamente ativos com datas de início diferentes — período comum e alinhamento por fim de período (PeriodEnd) aplicados em `core/`; integrado na página de comparação em 07/10; falta conferir no navegador
- [ ] Avaliar frequências semestral e anual (a configuração atual tem apenas Diário, Semanal e Mensal; depende do orientador)

### 4. Análise Individual
- [~] Exibir fonte dos dados e data da última atualização
- [~] Mensagem quando houver dados insuficientes
- [~] Indicar que lacunas podem vir de indisponibilidade do ativo
- [x] Revisar fallback de logos (URL indisponível → emoji) — coberto por `test_asset_logos.py`
- [~] Confirmar rótulo "anualizada" na volatilidade
- [~] Explicação curta do mapa de calor de sazonalidade
- [ ] Diferenciar retorno mensal de valorização acumulada — `create_monthly_return_matrix` integrada ao mapa de calor da Análise Individual em 07/10; falta conferir no navegador
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
- [~] Exibir data do pior drawdown — `get_max_drawdown_date` integrada à página de risco e retorno em 07/10; falta conferir no navegador
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
- [x] Arquitetura do sistema — `docs/arquitetura.md`
- [x] Catálogo de ativos — `docs/catalogo-de-ativos.md`
- [x] Fontes de dados — `docs/fontes_e_tratamento_de_dados.md`, seção 1
- [x] Tratamento de dados — `docs/fontes_e_tratamento_de_dados.md`, seções 2, 3 e 6
- [x] Cálculo de indicadores — `docs/metodologia_de_calculo.md`, seção 3
- [x] Cálculo de risco — `docs/metodologia_de_calculo.md`, seção 4
- [x] Limitações do yfinance — `docs/fontes_e_tratamento_de_dados.md`, seção 8
- [x] Ativos sem histórico completo — `docs/fontes_e_tratamento_de_dados.md`, seção 5
- [x] Tratamento de dados ausentes — `docs/fontes_e_tratamento_de_dados.md`, seção 7
- [x] Decisões sobre frequência — `docs/fontes_e_tratamento_de_dados.md`, seção 4
- [~] Hipóteses para previsão futura — rascunho em `docs/metodologia_de_calculo.md`, seção 7; com a pergunta A, previsão passou a trabalho futuro (`docs/validacao_academica.md`, seção 8)
- [x] Reforço de que histórico não é previsão — `docs/fontes_e_tratamento_de_dados.md`, seção 9, e `docs/metodologia_de_calculo.md`, seção 8
- [ ] Revisar os 3 documentos com o orientador e conferir os pontos marcados como convenção (RSI de Wilder, Bollinger `ddof=1`, √252, taxa livre de risco)

### 14. Validação acadêmica
- [~] Revisão teórica sobre análise técnica — estrutura e plano de busca em `docs/validacao_academica.md`, seção 3; capítulo a escrever
- [~] Relacionar indicadores a métodos de análise de dados — tabela em `docs/validacao_academica.md`, seção 3.2 (rascunho)
- [x] Formalizar pergunta de pesquisa — opção A (ferramenta compreensível para leigos), com objetivos O1–O6 em `docs/validacao_academica.md`, seção 1; confirmar o texto com o orientador
- [~] Definir hipóteses, variáveis-alvo, benchmarks — hipóteses H1–H4 em `docs/validacao_academica.md`, seção 2; variáveis-alvo e benchmarks de previsão ficam como trabalho futuro (seção 8)
- [~] Protocolo de validação — técnica, de conteúdo, com usuários e de neutralidade em `docs/validacao_academica.md`, seção 5; validação temporal de modelos mantida como trabalho futuro (seção 8)
- [~] Registrar limitações e resultados negativos — estrutura em `docs/validacao_academica.md`, seção 6; resultados a registrar após a avaliação
- [~] Relatório metodológico para o orientador — esqueleto em `docs/validacao_academica.md`, seção 7
- [ ] Testes de valores de referência independentes (cálculo manual, planilha ou outra biblioteca) para SMA, EMA, RSI, retorno, drawdown e Sharpe
- [ ] Questionário de interpretação e roteiro da avaliação com usuários (objetivo O6)
- [ ] Confirmar com o orientador a necessidade de CEP/TCLE para a avaliação com usuários

### 15. Qualidade e testes
- [x] Testes para novos indicadores
- [x] Testes para catálogo de ativos
- [x] Testes para logos e fallbacks
- [x] Testes para dados insuficientes
- [x] Testes para ativos sem histórico completo
- [x] Testes para filtros sem resultado — confirmado: `test_get_assets_with_no_match_returns_empty_list` em `test_assets.py`
- [x] Testes para exportação CSV — geração extraída para `core/exports.py` (`dataframe_to_csv_bytes`, `csv_filename`), usada nas 4 páginas; `test_exports.py` (10 testes)
- [x] Validação de datas do período personalizado: `core/date_validation.py` + `test_date_validation.py` (8 testes); a barra lateral exibe o erro e desabilita o botão
- [x] Manter cobertura ≥ 80% (meta), preservar ~95% (atual: 100%)
- [x] Testes de bordas de `comparison.py` e `data_processor.py` — ambos em 100% de cobertura

---

## Adendo de 07/10/2026 — itens incluídos após a ata

### A. Pendências técnicas

Fase 6 (comparação):
- [x] Alinhamento por fim de período (`PeriodEnd`) em `data_processor.py` e `comparison.py` — aplicado e coberto por testes (393 passando em 07/10; 405 em 09/10)
- [~] Usar `PeriodEnd` na página de comparação quando a frequência for semanal ou mensal — já aplicado na página; falta conferir no navegador
- [~] Proteção do Base 100 na página: ativos com preços ≤ 0 são excluídos com aviso (`calculate_drawdown` levanta `ValueError`); falta conferir no navegador com `CL=F`
- [ ] Commit da Fase 6 após aplicar e testar

Fase 7 e navegação:
- [~] Registrar a página "Simulação de Aportes" em `app/main.py` (arquivo entregue; conferir no navegador)
- [x] Rodar `python -m pytest` com os testes novos (`test_simulation.py`, `test_review_adjustments.py`, `test_visualizations_br.py`, `test_data_processor_edges.py`, `test_comparison_edges.py`) — 393 passando em 07/10/2026; 405 em 09/10/2026

Correções da revisão de 07/10 (`risk_metrics.py`, `analyzer.py`, `visualizations.py`, `state.py`):
- [x] Versões corrigidas aplicadas e testadas (393 passando em 07/10; 405 em 09/10); as integrações nas páginas estão listadas abaixo
- [~] Integrar `get_max_drawdown_date` à página de risco e retorno — feito; conferir no navegador
- [~] Trocar `create_year_month_matrix` por `create_monthly_return_matrix` no mapa de calor — feito; conferir em frequência diária e mensal
- [~] Passar a moeda do ativo (`price_label`) aos gráficos de preço — feito em Indicadores Técnicos; conferir no navegador
- [~] Capturar `ValueError` de valores ≤ 0 nas páginas de risco e de comparação (ex.: petróleo WTI negativo em abril de 2020) com mensagem clara — feito; conferir com `CL=F`
- [ ] Conferir no navegador as 5 páginas alteradas em 07/10 (Análise Individual, Risco e Retorno, Indicadores Técnicos, Comparação, Simulação de Aportes) e os 4 downloads de CSV
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
- [x] Cobrir as 9 linhas restantes (`test_coverage_gaps.py`, 12 testes; `core/` em 100%): `assets.py` (331, 343, 351), `data_loader.py` (96, 119, 157), `indicator_docs.py` (114), `indicators_extra.py` (43), `data_availability.py` (107)
- [ ] Atualizar `docs/checkpoint_qualidade.md` a cada fase

### B. Pendências acadêmicas

- [~] 1. Revisão teórica sobre análise técnica (capítulo de 8 a 15 páginas com referências) — estrutura e plano de busca prontos; capítulo a escrever
- [x] 2. Pergunta de pesquisa — **opção A escolhida em 07/10/2026**; B e C não foram adotadas; C (previsão) fica como trabalho futuro
- [~] 3. Matriz de literatura (20 a 30 trabalhos) — colunas e pontos de partida em `docs/validacao_academica.md`, seções 3.4 e 3.5; busca a fazer
- [~] 4. Hipóteses — reformuladas para a pergunta A (H1–H4); variáveis-alvo e horizontes de previsão passam a trabalho futuro
- [ ] 5. Benchmarks e modelos simples (regressão, classificação, ARIMA, Random Forest) — trabalho futuro, fora do escopo da pergunta A
- [~] 6. Protocolo de validação — reformulado em quatro frentes (técnica, conteúdo, usuários, neutralidade); validação temporal de modelos é trabalho futuro
- [~] 7. Relatório metodológico para o orientador — esqueleto pronto; depende das demais pendências

Ordem de dependência: 2 define 4; 1 e 3 alimentam 4; 7 reúne tudo. Com a pergunta A, o item 5 deixa de ser dependência do 6.

### C. Dúvidas para o orientador (registrar a resposta ao lado)

- [ ] Nome "Argos DataLab" e identidade visual: manter ou revisar?
- [ ] As 13 classes/grupos bastam para a primeira versão?
- [ ] O critério de seleção do catálogo está adequado como amostra inicial?
- [ ] Incluir frequências semestral e anual? São estatisticamente adequadas?
- [ ] Confirmar a convenção de anualização (√252 diário) e a taxa livre de risco do Sharpe
- [ ] Aprovar RSI de Wilder, Bollinger com `ddof=1` e RSI plano = `NaN`
- [ ] Quais indicadores serão features futuras de modelos? (trabalho futuro com a pergunta A)
- [ ] Horizonte e alvo da previsão: retorno, direção ou volatilidade? (trabalho futuro com a pergunta A)
- [ ] Confirmar que previsão e validação temporal de modelos ficam como trabalho futuro, fora do escopo da pergunta A
- [ ] Avaliação da compreensão com usuários sem formação em finanças: aprovar o formato (questionário, SUS, versão com × sem camada educativa) ou a alternativa por especialistas
- [x] A avaliação com usuários exige parecer do CEP e TCLE? — **Sim** (09/10/2026): o CEP exige parecer favorável antes da coleta; o TCLE não o substitui; só adultos (18+)
- [ ] Simulação de aportes: formato aprovado? (aporte único × periódico, valor hipotético, janelas históricas, sem recomendação)
- [ ] Estrutura esperada do relatório metodológico
- [ ] Prazo da próxima entrega ou apresentação

---

## Adendo de 09/10/2026 — Plano de Ajustes 2

Origem: reunião de 07/10/2026 e respostas de 09/10/2026 (duas rodadas). Detalhes em `docs/ata_reuniao_2026-10-07.md`, `docs/plano_de_ajustes_2.md` e `docs/llm_7b_especificacao.md`. Os itens abaixo seguem a legenda do início deste arquivo.

Decisões registradas:

- Home, "Get Started" e vídeo de abertura ficam para depois das funcionalidades, junto com a Fase 10 (Plano 3).
- Sazonalidade: janela de retorno do fechamento do mês de entrada ao fechamento do mês de saída, composta; setembro→outubro é o retorno de outubro. Recorte por anos **só na Análise Individual**; exibir também mediana e proporção de anos positivos.
- Simulação: manter apenas as janelas móveis históricas existentes; a janela sazonal por ano atende ao exemplo do orientador.
- Comparação: sem tabela com mais de 5 ativos; sem recorte por anos.
- Tendência: retorno móvel e razão de desempenho; sem regressão.
- Linguagem descritiva em toda a interface.
- LLM: componente de apoio à interpretação e à educação financeira no relatório da pergunta A, não núcleo metodológico. OpenAI, `gpt-5-mini` (principal) e `gpt-5-nano` (comparação). A 7B só começa depois que a 7A atingir todos os limiares; aprovação do orientador informada como condicional.
- Avaliação O6 só com adultos (18+), com TCLE.
- Relatórios do PIBITI registram a mudança de escopo (cronograma original, executado, alterações e justificativas, conexão com o objetivo geral).
- Datas: Relatório Parcial até 31/03/2027; Relatório Final e Resumo Expandido até 28/08/2027; defesa do TCC até 31/10/2027. SBBD: chamada de demos até abril/2027, evento em setembro/2027.
- Demonstração: ao vivo com dados salvos em cache; reserva obrigatória em screencast de até 5 min; reserva secundária em versão online pública.
- Trabalho colaborativo e autoria: nada confirmado; **não registrar em contribuições**; tratar no próximo plano.
- Não há defeitos de seleção de ativos ou logos.
- CEP: parecer favorável obrigatório antes da coleta da O6 (adultos, com TCLE).
- Limites de uso da LLM em três camadas (sessão, navegador, global persistente). Avaliação humana da 7A por três avaliadores independentes, com calibração e kappa ponderado ≥ 0,60.
- Evidência escrita das decisões do orientador: `docs/pibiti/decisoes_orientador.md`.
- Versão pública no Streamlit Community Cloud **sem** explicação assistida; explicação ativa só na demonstração ao vivo e no screencast (decidido por delegação).
- Revisão por pessoa da área de educação: depois do congelamento da versão.

### D. Plano 2 — tarefas por bloco

Bloco 1 — Consolidação e contribuições:
- [~] Executar o roteiro de navegador das 5 páginas e dos 4 downloads de CSV e converter os `[~]` em `[x]` — roteiro pronto em `docs/roteiro_conferencia_navegador.md`; falta executar
- [~] Verificar a versão do pandas e tratar o preenchimento de lacunas em `pct_change` — ajuste aplicado com `core/returns_utils.py` (`simple_returns`) em `comparison.py`, `analyzer.py`, `indicators_extra.py` e `analise_individual.py`; 8 testes novos; falta rodar o `pytest` (405 esperados) e o diagnóstico de versão
- [~] Criar `docs/contribuicoes.md` sem trabalho colaborativo não confirmado — criado; o autor revisa papéis e a declaração de uso de IA

Bloco 2 — Sazonalidade por anos, meses e janela (só Análise Individual):
- [ ] `core/seasonality.py`: filtro da matriz, resumo (média geral, média do recorte, diferença em p.p., mediana, proporção de anos positivos, N), retorno de janela composta
- [ ] Testes: regressão com todos os anos, subconjunto, N, janela de 1 mês = retorno mensal, janela de 3 meses = produto, virada de ano, fechamento ausente, mês em andamento, mediana e proporção de positivos
- [ ] Bloco "Recorte por anos e meses" com "Aplicar filtro" e texto metodológico

Bloco 3 — Comparação (apenas lacunas):
- [ ] Sazonalidade geral comparada entre ativos, com N por ativo
- [ ] Verificar legenda interativa e aviso de uso
- [ ] Verificar a hierarquia Classe → Subclasse → Mercado → Ativos na seleção
- [ ] Textos descritivos (sem "melhor/pior")

Bloco 4 — Simulação (revisão):
- [ ] Texto obrigatório presente; "teria ocorrido"; sem "previsão" ou "quanto investir"
- [ ] Renomear "pior/melhor janela" para rótulos descritivos
- [ ] Avisos de preço sem dividendos, custos não incluídos e moeda
- [ ] Teste de linguagem neutra na página

Bloco 5 — Educação:
- [ ] Inventário de gráficos sem texto e textos no roteiro (mede, mostra, cuidado, não permite concluir)
- [ ] Botão "Como ler este gráfico" com texto fixo
- [ ] Teste de linguagem neutra cobrindo todos os textos de `app/ui/`
- [ ] Revisão por pessoa da área de educação

Bloco 6 — Tendência:
- [ ] `core/trend.py`: retorno móvel (3, 6 e 12 meses), razão de desempenho e diferença de retorno móvel
- [ ] Janela visível, rótulo "tendência histórica" e aviso sobre a data inicial

Bloco 7 — LLM:
- [ ] 7A: avaliação humana por 3 avaliadores (leigo, técnico, neutralidade), calibração e kappa ponderado ≥ 0,60; aprovação registrada em `docs/pibiti/decisoes_orientador.md`
- [ ] 7A: `docs/protocolo_prompts_llm.md`; `core/llm_context.py` e `core/llm_validation.py` (puros, testados); ≥ 12 casos, 2 modelos, 3 repetições; script de experimento fora do app; rubrica; casos negativos
- [ ] 7A: confirmar na primeira chamada os parâmetros (temperatura, tokens de raciocínio) e verificar preços na página oficial
- [ ] 7A: relatório de validação e aprovação do orientador registrada por escrito
- [ ] 7B (só com todos os limiares atingidos): prompts versionados, cliente com timeout e retentativas, auditoria, limites de uso, botão "✨ Explicar esta análise", fallback, segredos fora do Git, documentação

Bloco 8 — Fechamento:
- [ ] Atualizar metodologia, arquitetura, checkpoint de qualidade, validação acadêmica (LLM como apoio; O6 só adultos) e este checklist
- [ ] Rodar a suíte com cobertura e registrar
- [ ] Quadro de escopo para o Relatório Parcial (até 31/03/2027)
- [ ] Registrar a versão (tag), preparar dados em cache, screencast de até 5 min e versão pública

Bloco 9 — Protocolo ético e avaliação com usuários (O6):
- [ ] Confirmar com o orientador e com o CEP da UFPI procedimento, documentos, prazo e pesquisador responsável
- [ ] Escrever o protocolo de pesquisa (objetivo, participantes adultos, recrutamento, procedimento, instrumentos, riscos e benefícios, dados)
- [ ] Escrever o TCLE e os instrumentos (questionário de interpretação, SUS, versões com e sem camada educativa)
- [ ] Submeter ao CEP; **nenhuma coleta antes do parecer favorável**
- [ ] Aplicar sobre a versão congelada e registrar versão e data

### E. Respostas e dúvidas

Respondidas em 09/10/2026:
- [x] N01 home e vídeo depois das funcionalidades · [x] N02 recorte só na Análise Individual · [x] N03 janela fechamento→fechamento · [x] N04 só janelas móveis · [x] N04b janela sazonal atende · [x] N05 mediana e proporção positiva · [x] N06 sem tabela > 5 · [x] N07 retorno móvel e razão · [x] N08 linguagem descritiva · [x] N09 LLM como apoio · [x] N10 SBBD · [x] N12 sem defeitos · [x] N13 relatórios registram escopo · [x] N14 só adultos com TCLE · [x] N15 datas · [x] N17 configuração da LLM · [x] N18 estratégia de demonstração

Respondidas na terceira rodada (09/10/2026):
- [x] N14b CEP exige parecer antes da coleta · [x] N16 trabalho colaborativo adiado · [x] N19 limites em três camadas · [x] N20 três avaliadores, calibração, kappa ≥ 0,60 · [x] N21 evidência em `docs/pibiti/decisoes_orientador.md` · [x] N22 versão pública sem explicação assistida (por delegação) · [x] N23 revisão da educação depois do congelamento · [x] N24 Streamlit Community Cloud (por delegação)

Em aberto:
- [ ] N16: trabalho colaborativo e autoria (Plano 3)
- [ ] N25: os avaliadores humanos da 7A exigem tratamento ético próprio?
- [ ] N26: quem são os três avaliadores; o técnico pode ser o desenvolvedor?
- [ ] N27: procedimento, prazo e pesquisador responsável no CEP da UFPI
- [ ] N28: como calcular o kappa ponderado com dimensões diferentes por avaliador (proposta: subconjunto de calibração avaliado por todos)
- [ ] N29: regra por resposta (100% factual) × limiar agregado (≥ 95%): vale o mais rígido?
- [ ] N30: confirmar que "depois" (N23) é depois do congelamento

---

## Andamento do Plano 2 — atualização de 09/10/2026

### Bloco 1 — Consolidação (código concluído)
- [x] Retorno por variação percentual sem preenchimento de lacunas (`core/returns_utils.py`, `simple_returns`; usado em `analyzer.py`, `indicators_extra.py`, `analise_individual.py`; `comparison.py` já usava fórmula equivalente) — 8 testes em `tests/test_returns_gap.py`
- [x] Alinhamento por `PeriodEnd` coberto por `tests/test_comparison_align.py` (4 testes)
- [x] `pytest`: 405 passando, 1081 instruções, `core/` em 100% (pandas 3.0.5)
- [~] Roteiro de conferência no navegador (`docs/roteiro_conferencia_navegador.md`, S01–S20) — executar e registrar
- [~] `docs/contribuicoes.md` — conferir o texto da seção de uso de IA ("a confirmar pelo autor")
- [ ] Commit do Bloco 1

### Bloco 2 — Sazonalidade por anos, meses e janela (código entregue)
- [~] `core/seasonality.py` (`filter_monthly_matrix`, `seasonal_summary`, `window_returns`, `window_summary`, `monthly_closes`, `exclude_month_in_progress`) — 20 testes em `tests/test_seasonality.py`; rodar a suíte real
- [~] Bloco "Recorte por anos e meses" na Análise Individual (anos, meses, janela, botão "Aplicar filtro", texto metodológico obrigatório) — conferir no navegador (cenários S21–S24)
- [~] Médias do gráfico "Média Consolidada por Mês" passam a excluir o mês em andamento (o mapa de calor continua mostrando o mês, com aviso)
- [ ] Conferir no navegador o caso do orientador: Bitcoin, setembro → outubro
- [ ] Commit do Bloco 2

### Bloco 3 — Comparação ampliada (código entregue em 09/10/2026)
- [~] 3.1 Sazonalidade comparada: `compare_monthly_averages` em `core/seasonality.py`, nova aba "Sazonalidade" em `comparacao_ativos.py` (gráfico por mês e ativo, tabela com média e N por ativo) — 4 testes em `tests/test_seasonality_compare.py`
- [~] 3.2 Legenda: o gráfico Base 100 usa a legenda padrão do Plotly (clicar oculta/exibe a série, dois cliques isolam); adicionada uma linha de ajuda (`LEGEND_HINT`) — confirmar no navegador (S25)
- [x] 3.3 Hierarquia do seletor — **achado:** a barra lateral oferece **Classe (13 grupos) → Ativos** (mais digitação livre de ticker). O catálogo (`core/assets.py`) já tem os campos `subcategory` e `market`, mas eles **não** são filtros na Comparação. A hierarquia completa Classe → Subclasse → Mercado → Ativos **não está presente**. Proposta (não implementada, depende de decisão): dois filtros opcionais "Mercado" e "Subclasse" abaixo da classe, que apenas reduzem a lista do `multiselect`. Fica como candidato do Plano 3, para não mexer nos callbacks do seletor agora
- [~] 3.4 Rótulos dos destaques em redação descritiva (`core/comparison_texts.py`): "Maior/Menor retorno acumulado no período analisado", "Menor queda máxima observada", "Maior Sharpe no período analisado"; teste de linguagem neutra
- [ ] Commit do Bloco 3

### Bloco 4 — Simulação histórica: revisão e texto (código entregue em 09/10/2026)
- [~] 4.1 Texto obrigatório palavra por palavra (`SIMULATION_MANDATORY_TEXT`), exibido no topo da página; o aviso anterior continua abaixo e no rodapé
- [~] 4.2 Redação no passado ("teria ocorrido"); sem "vai ocorrer", "quanto investir" (teste varre os textos literais da página)
- [~] 4.3 Rótulos da tabela de janelas: "Menor retorno histórico", "Maior retorno histórico", "Mediana" (antes: pior/melhor janela); a frase "terminou melhor" virou "terminou com maior valor final". Chaves internas de `core/simulation.py` não mudaram
- [~] 4.4 Premissas explícitas (`SIMULATION_ASSUMPTIONS`): preço de fechamento, sem ajuste por dividendos, sem corretagem, taxas e impostos, valores na moeda do ativo
- [x] 4.5 `^IRX`, `^FVX`, `^TNX`, `^TYX` seguem fora da simulação (teste novo)
- [~] 4.6 Teste de linguagem neutra estendido à página (`tests/test_simulation_texts.py`, 6 testes; total esperado 435)
- [ ] Commit do Bloco 4

### Bloco 5 — Educação: textos por gráfico (código entregue em 09/10/2026)
- [~] 5.1 Inventário dos gráficos: `docs/inventario_graficos.md` (22 gráficos/blocos; 24 com o Bloco 6)
- [~] 5.2 Roteiro padrão (mede · mostra · cuidado · não permite concluir) para os 22 gráficos: `core/chart_guides.py`
- [~] 5.3 Textos dos recursos novos: Blocos 2, 3 e 4 já incluídos (`recorte_anos`, `janela_retorno`, `sazonalidade_comparada`, `simulacao_*`); o Bloco 6 acrescenta os seus
- [~] 5.4 Os 10 termos no glossário: conferido por teste (`test_glossary_covers_the_ten_required_terms`); se falhar, ele lista os termos ausentes
- [~] 5.5 Botão "Como ler este gráfico" (`app/ui/chart_guide.py`) em todas as páginas com gráfico
- [ ] 5.6 Revisão por pessoa da área de educação — depois do congelamento (N23); registro em `docs/pibiti/revisao_textos_educativos.md`
- [~] 5.7 Teste de linguagem neutra em todos os textos de `app/ui/` e nos roteiros
- [ ] Commit do Bloco 5

### Bloco 6 — Tendência histórica: retorno móvel e razão de desempenho (código entregue em 09/10/2026)
- [~] `core/trend.py` (`rolling_return`, `rolling_return_gap`, `performance_ratio`, `rebase_common_start`, `monthly_close_table`), em decimal — 19 testes em `tests/test_trend.py` (inclui: série que dobra em 12 meses = 1,0; razão de séries idênticas = 0; históricos diferentes; janela maior que a série = vazio; dependência da data inicial)
- [~] Aba "📐 Tendência" na Comparação: janelas de 3, 6 e 12 meses, ativo de referência escolhido pelo usuário, gráfico de retorno móvel, gráfico de razão de desempenho e tabela com a diferença em pontos percentuais; roteiros `tendencia_retorno_movel` e `tendencia_razao`
- [~] Rótulo "tendência histórica"; janela no título; aviso de que a razão depende da data inicial e de que a tendência passada pode mudar
- [ ] Conferir no navegador com dois ativos (S38–S42)
- [ ] Commit do Bloco 6
- Decisões minhas por delegação (N25–N30 em aberto): retorno móvel sobre **fechamentos mensais**; mês em andamento fora; razão calculada por par com início na primeira data em que os dois têm dados; sem regressão e sem detecção de cruzamentos [D N07]

### Bloco 8 — Documentação, relatórios e congelamento (entregue em 10/10/2026, em parte aguardando decisões)
- [~] 8.1 Atualizados: `metodologia_de_calculo.md` (lacunas, sazonalidade 2.1, tendência 5.1, rótulos), `arquitetura.md` (módulos, páginas, decisões, testes, camada planejada), `checkpoint_qualidade.md` (487 testes, evolução por bloco) e este checklist
- [~] 8.2 `validacao_academica.md`: LLM como componente de apoio (5.5, N09); O6 só com adultos, TCLE e parecer favorável do CEP antes da coleta (5.3, N14/N14b); casos de referência do recorte e da tendência (5.1); protocolo de prompts na frente 4
- [x] 8.3 `python -m pytest` com cobertura: 487 passando, `core/` em 100% (1251 instruções), em 10/10/2026
- [~] 8.4 Quadro de escopo para o Relatório Parcial: `docs/pibiti/escopo_relatorios.md` — **falta colar o cronograma original aprovado** (coluna 1)
- [ ] 8.5 Congelamento da versão: procedimento e registro em `docs/versao_congelada.md`; a tag definitiva só depois dos Blocos 7 e 9 (previsão: fev/2027)
- [~] 8.6 Estratégia de demonstração: `docs/demonstracao.md` (camadas, roteiro do screencast, limites e ajustes do Streamlit Community Cloud, contingência)
- [~] 8.8 **Modo de demonstração com dados salvos — requisito obrigatório do congelamento** (`docs/demonstracao.md`, seção 2): `scripts/gerar_dados_demo.py`, manifesto com hash, `ARGOS_DEMO_MODE`, bloqueio de chamadas externas, aviso de versão congelada, respostas de LLM salvas e validadas, texto fixo de reserva, teste automatizado e execução uma vez sem internet
  - [x] Código: `core/demo_mode.py`, `data_loader`, `assets_logos`, aviso em `app/main.py`, `scripts/gerar_dados_demo.py`, `tests/test_demo_mode.py`
  - [ ] Gerar e versionar `data/demo/` (rodar o gerador com internet; `.gitattributes`: `data/demo/* -text`)
  - [ ] Rodar o pytest e corrigir o que a auditoria de recursos remotos apontar
  - [ ] Conferir o aviso e as 5 análises no navegador com `ARGOS_DEMO_MODE=true`
  - [ ] Executar a demo uma vez com a internet desativada
  - [ ] Teste de memória (Streamlit Cloud) e respostas de LLM salvas (após 7B)
- [x] 8.7 O que ficou fora, com motivo: `docs/fora_do_escopo.md`
- [ ] Commit do Bloco 8