# Registro de escopo para os relatórios do PIBITI

**Finalidade.** Atender à decisão N13 (09/10/2026): os relatórios do PIBITI registram a mudança de escopo em relação ao cronograma formal, com (1) cronograma original, (2) cronograma efetivamente executado, (3) alterações e justificativas e (4) conexão com o objetivo geral do plano aprovado. Primeira entrega: **Relatório Parcial (até 31/03/2027)**. Depois: Relatório Final e Resumo Expandido (até 28/08/2027).

**Contexto.** O orientador informou em 07/10/2026 que o cronograma do plano de trabalho é formal e pode ser alterado durante a execução. Confirmar com ele o modelo oficial do relatório (campos, tamanho) antes de transcrever este quadro.

> **Pendência de confirmação.** O cronograma original abaixo foi reconstruído a partir da vigência do PIBITI 2026–2027 (01/09/2026 a 31/08/2027) e das etapas previstas antes das alterações registradas em outubro de 2026. Antes da submissão dos relatórios, conferir o texto exato do plano de trabalho aprovado no edital e ajustar denominações e períodos, se necessário.

---

## 1. Cronograma original (plano de trabalho aprovado)

| Etapa | Período | Descrição |
|---|---|---|
| 1. Estudo teórico e levantamento de requisitos | set/2026 a out/2026 | Revisão de literatura sobre séries temporais financeiras, análise técnica, indicadores, métricas de risco e retorno, visualização de dados e educação financeira. Levantamento de requisitos funcionais e não funcionais da plataforma. |
| 2. Preparação e estruturação dos dados | out/2026 a nov/2026 | Definição das fontes de dados, tratamento de séries temporais, validação de dados, tratamento de lacunas, padronização de períodos e frequências. |
| 3. Desenvolvimento da plataforma | nov/2026 a jan/2027 | Desenvolvimento da aplicação, páginas de análise, seleção de ativos, filtros de período e frequência, visualizações e navegação. |
| 4. Implementação de indicadores técnicos | dez/2026 a jan/2027 | Implementação de indicadores técnicos, incluindo médias móveis, Bandas de Bollinger, RSI, MACD, ATR, volatilidade móvel e volume. |
| 5. Implementação de métricas de risco e retorno | jan/2027 a fev/2027 | Implementação de métricas de retorno, volatilidade, Sharpe, drawdown e correlação, com visualizações e explicações. |
| 6. Comparação de ativos e análise exploratória | fev/2027 a mar/2027 | Desenvolvimento da comparação entre ativos, análise de desempenho, risco, correlação e organização dos resultados para interpretação. |
| 7. Recursos educativos e validação inicial | mar/2027 a abr/2027 | Elaboração de textos explicativos, glossário, avisos metodológicos e validação inicial da plataforma. |
| 8. Consolidação, testes e documentação | abr/2027 a jun/2027 | Consolidação das funcionalidades, testes automatizados, documentação técnica, revisão de qualidade e preparação da versão para avaliação. |
| 9. Avaliação e análise dos resultados | jun/2027 a jul/2027 | Avaliação da compreensão e usabilidade da plataforma, análise dos resultados e ajustes finais. |
| 10. Consolidação final e relatório | jul/2027 a ago/2027 | Consolidação dos resultados, redação do relatório final, preparação do resumo expandido e encerramento do plano de trabalho. |

> **Observação.** Este cronograma representa a organização inicial do plano de trabalho, compatível com a vigência do PIBITI 2026–2027. Ele deve ser confrontado com o documento original aprovado antes da submissão dos relatórios.

---

## 2. Cronograma efetivamente executado

| Período | O que foi executado | Evidência no repositório |
| --- | --- | --- |
| Até 06/10/2026 | Protótipo evolutivo (Plano 1, fases 1 a 9): análise individual, indicadores técnicos, risco e retorno, comparação, simulação, camada educativa, documentação técnica | `docs/checklist_pendencias.md`, `docs/arquitetura.md` |
| 06/10/2026 | Reunião de planejamento; escolha da pergunta de pesquisa A (interpretação por pessoas sem formação em finanças) | `docs/validacao_academica.md` |
| 07 a 09/10/2026 | Reunião com o orientador; decisões registradas; Plano 2 elaborado | `docs/ata_reuniao_2026-10-07.md`, `docs/plano_de_ajustes_2.md`, `docs/pibiti/decisoes_orientador.md` |
| 09 e 10/10/2026 | Plano 2, blocos 1 a 6: consolidação; sazonalidade por anos, meses e janela; comparação ampliada; revisão da simulação; roteiros de leitura por gráfico; tendência histórica | 487 testes, `core/` a 100%; `docs/checkpoint_qualidade.md` |
| 10/10/2026 | Modo de demonstração com dados salvos implementado e validado sem internet; minutas do protocolo, TCLE e instrumentos para o CEP (Bloco 9) | 518 testes, `core/` a 100%; `docs/pibiti/cep/` |
| Previsto: out/2026 a fev/2027 | Blocos 7A/7B (explicação assistida, condicionada à validação), 9 (protocolo do CEP); congelamento da versão | `docs/plano_de_ajustes_2.md`, seção 5.3 |
| Previsto: até o congelamento da versão | Implementação e validação do modo de demonstração com dados salvos (`demo mode`), conforme `demonstracao.md`, seção 2.1. O modo deve permitir executar análises, gráficos, filtros e explicações sem dependência de internet. | `demonstracao.md`, seção 2.1; `docs/plano_de_ajustes_2.md` |
| Previsto: mar/2027 | Relatório Parcial | — |
| Previsto: mai a jul/2027 | Avaliação com usuários (O6), **somente com parecer favorável do CEP** | `docs/plano_de_ajustes_2.md`, Bloco 9 |
| Previsto: até 28/08/2027 | Relatório Final e Resumo Expandido | — |

Atualizar a coluna "Evidência" a cada entrega e registrar aqui qualquer atraso.

---

## 3. Alterações em relação ao plano original e justificativas

| # | Alteração | Justificativa | Origem |
| --- | --- | --- | --- |
| A1 | Pergunta de pesquisa centrada na **compreensão por pessoas sem formação em finanças** (pergunta A); previsão e validação temporal passam a **trabalho futuro** | Foco no que o projeto entrega e consegue avaliar no prazo; mantém o rigor e evita afirmar capacidade preditiva | Decisão de 07/10/2026 |
| A2 | Inclusão de **sazonalidade por anos, meses e janela de retorno** (caso: depositar em setembro e retirar em outubro) | Pedido do orientador na reunião de 07/10; ajuda a interpretar a média histórica frente a anos específicos | Reunião de 07/10/2026 (N02, N03, N05) |
| A3 | **Comparação ampliada** com sazonalidade por ativo e textos descritivos | Pedido do orientador; mantém a neutralidade da linguagem | Reunião de 07/10/2026 (N06, N08) |
| A4 | Revisão da **simulação histórica** (rótulos e texto obrigatório) | Neutralidade: evitar "melhor" e "pior" | Reunião de 07/10/2026 (N04) |
| A5 | **Textos fixos por gráfico** ("Como ler este gráfico") | Reforça o objetivo O3 (camada educativa) e serve de reserva da camada assistida | Reunião de 07/10/2026 |
| A6 | **Tendência histórica** (retorno móvel e razão de desempenho), sem regressão | Pedido do orientador, em versão mínima | Reunião de 07/10/2026 (N07) |
| A7 | **Explicação assistida por modelo de linguagem**, como componente de apoio e condicionada à validação (7A) e à aprovação | Apoio à interpretação; não é núcleo metodológico | Reunião de 07/10/2026 (N09, N17) |
| A8 | **Avaliação com usuários** somente com adultos e com parecer favorável do CEP antes da coleta | Requisito ético; evita coleta antes da apreciação | N14, N14b |
| A9 | **Nome do projeto e identidade visual** (fase 10) passam para o Plano 3 | Mudanças visuais devem vir depois das melhorias de conteúdo | Decisão do autor, 09/10/2026 |
| A10 | Produção de **artigo para a trilha de demos do SBBD** e preparação de demonstração | Divulgação dos resultados | Orientação de 09/10/2026 |
| A11 | Implementação do **modo de demonstração com dados salvos** antes do congelamento da versão | Garantir estabilidade, reprodutibilidade e disponibilidade da demonstração do SBBD, mesmo sem acesso à internet ou às fontes externas de dados | `demonstracao.md`, seção 2.1; decisão de 10/10/2026 |

---

## 4. Conexão com o objetivo geral do plano aprovado

Objetivo geral (ver `docs/validacao_academica.md`, seção 1.2): desenvolver e avaliar uma ferramenta de apoio à interpretação de dados históricos do mercado financeiro, compreensível para pessoas sem formação em finanças, com rigor metodológico e sem configurar recomendação de investimento.

| Alteração | Objetivo específico que reforça | Como se conecta |
| --- | --- | --- |
| A1 | Todos | Delimita o eixo da validação |
| A2, A3, A6 | O1, O2 | Novas formas de organizar o histórico para interpretação, com cálculos documentados e testados |
| A4, A5 | O3, O4 | Linguagem neutra e explicação por gráfico |
| A7 | O3, O4 | Apoio educativo, auditável, com validação humana e texto fixo de reserva |
| A8 | O6 | Avaliação da compreensão, com ética |
| A9, A10 | — | Organização do trabalho e divulgação; sem alterar o objetivo geral |
| A11 | O2, O5 | Reprodutibilidade: a mesma versão, com os mesmos dados salvos, produz os mesmos resultados em qualquer ambiente, o que também documenta os dados usados |

---

## 5. Para o texto do relatório

Sugestão de redação (ajustar ao modelo oficial):

> O plano de trabalho formal foi mantido como referência. Durante a execução, e com o acordo do orientador, o escopo foi ampliado e reorganizado conforme o quadro acima, sem alterar o objetivo geral: as novas funcionalidades servem à interpretação por pessoas sem formação em finanças, com rigor e sem recomendação.