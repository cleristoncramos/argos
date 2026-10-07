# Ata de Reunião — Orientação do Projeto Argos DataLab

**Data:** 06/10/2026
**Participantes:** Clériston de Castro Ramos (discente), Prof. Dr. Arlino Henrique Magalhães de Araújo (orientador)
**Contexto:** Apresentação do protótipo atual do Argos DataLab e definição de diretrizes de avanço.

## Direcionamento geral aprovado

O orientador aprovou a direção geral do projeto, com uma mudança de foco central:

> O sistema deve ser apresentado como uma ferramenta de **pesquisa, educação financeira e apoio à interpretação de dados**, e não como uma ferramenta de **recomendação de investimentos**.

Decisões de base:
- Manter o Argos como plataforma de análise de dados do mercado financeiro.
- Reforçar o caráter de iniciação tecnológica e pesquisa aplicada (PIBITI UFPI 2026–2027).
- Preservar Python, Streamlit, Plotly e yfinance como base tecnológica.
- Não ampliar o escopo antes de consolidar o núcleo do sistema.
- Tratar as funcionalidades atuais como um protótipo evolutivo.
- Nome e identidade visual ("Argos DataLab") permanecem em aberto, a revisar com o orientador — **prioridade baixa**.

## Síntese das deliberações

A ata completa, item por item, está registrada em `docs/checklist_pendencias.md`. Os eixos principais discutidos:

1. Seleção e catálogo de ativos — manter seleção hierárquica, documentar critério de escolha dos ativos atuais como amostra inicial.
2. Período e frequência — diferenciar período solicitado de período efetivamente disponível.
3. Página de Análise Individual — adicionar metadados de fonte/atualização e explicações metodológicas.
4. Indicadores técnicos — revisar, documentar e reduzir ao conjunto essencial (ver decisão abaixo).
5. Relação entre indicadores e modelos futuros — separar camada de features, sem prometer capacidade preditiva.
6. Página de Risco e Retorno — adicionar textos educativos a cada métrica.
7. Educação financeira — criar camada explicativa, glossário, linguagem neutra em toda a interface.
8. Simulação de aportes — implementar como simulação histórica neutra, não como recomendação personalizada.
9. Página de Comparação — manter estrutura atual, adicionar metadados e avisos de período divergente.
10. Visualizações e interface — manter Streamlit, padronizar componentes, reduzir poluição visual.
11. Reutilização de componentes — extrair cards, tooltips, seleção de ativos e tabelas para módulos comuns.
12. Documentação técnica e validação acadêmica — base para o próximo ciclo de pesquisa.
13. Qualidade e testes — manter cobertura ≥ 95%, hoje já alcançada.

## Decisão: indicadores técnicos da primeira versão

Conjunto fechado para esta fase do projeto:

| Indicador | Categoria |
|---|---|
| SMA (médias móveis simples) | Tendência |
| EMA (médias móveis exponenciais) | Tendência |
| Bandas de Bollinger | Volatilidade |
| RSI | Momentum |
| MACD | Momentum/Tendência |
| ATR | Volatilidade |
| Volatilidade móvel | Volatilidade |
| Volume | Volume |

Demais indicadores atualmente implementados (se houver) ficam fora da primeira versão até serem justificados metodologicamente.

## Pergunta de pesquisa (rascunho — opções a validar com o orientador)

> Em que medida indicadores técnicos clássicos (tendência, momentum, volatilidade e volume), calculados sobre dados históricos de múltiplas classes de ativos, podem ser organizados em uma ferramenta de apoio à interpretação de dados financeiros que seja compreensível para usuários sem formação em finanças, preservando rigor metodológico e sem configurar recomendação de investimento?

> Como uma plataforma computacional orientada à educação financeira pode integrar dados históricos, indicadores técnicos e métricas de risco para apoiar a análise exploratória e a investigação de séries temporais de ativos financeiros?

> Como a organização e o tratamento de dados financeiros, combinados à geração de indicadores técnicos e métricas de risco, podem constituir uma base reprodutível para futuras aplicações de métodos de análise de dados na investigação e previsão de mercados financeiros?

A pergunta principal define o escopo do protótipo atual (análise exploratória e educação financeira). O desdobramento justifica, desde já, decisões de arquitetura como a separação entre camada de visualização e camada de features (Seção 6 do checklist), sem comprometer o projeto com entregas de modelos preditivos nesta fase.

Possíveis desdobramentos para formalização posterior (Sprint 5):
- Hipótese secundária sobre uso futuro dos indicadores como variáveis preditivas (regressão/classificação simples, com validação temporal fora da amostra).
- Delimitação clara entre o que é "análise descritiva histórica" e o que seria "modelo preditivo" — o projeto atual cobre o primeiro; o segundo é trabalho futuro.

## Decisões adicionais de escopo (confirmadas em 30/09/2026)

- **Catálogo de ativos:** as 13 classes atuais são mantidas na primeira versão. Não há redução de escopo nesse eixo — o trabalho da Fase 5 passa a ser documentar o critério de seleção dentro de cada classe, não reduzir classes.
- **Digitação livre de ticker:** entra no escopo desta fase (não fica para depois). Usuários avançados poderão digitar um ticker diretamente, além do fluxo hierárquico guiado. Implicações técnicas:
  - A seleção hierárquica continua como fluxo **principal e padrão** para iniciantes.
  - A digitação livre é um modo alternativo, não substitui o catálogo.
  - Exige validação do ticker digitado (existe no yfinance? retorna dados?) e mensagem de erro clara quando o ticker não existir ou não tiver dados.
  - Isso move um item de "Prioridade média/baixa" para dentro do trabalho ativo da Fase 5 (Análise Individual) — ver checklist atualizado abaixo.

## Síntese final

A reunião validou o potencial do Argos e a qualidade do protótipo visual. As mudanças necessárias não são de infraestrutura, mas de **interpretação, educação financeira, documentação e delimitação científica**. O próximo ciclo prioriza explicações para usuários leigos, revisão dos indicadores técnicos, preparação dos indicadores como possíveis features futuras, e criação de simulações históricas neutras. Expansão para recomendação personalizada ou previsão avançada fica para uma etapa posterior, após consolidação metodológica e validação acadêmica.