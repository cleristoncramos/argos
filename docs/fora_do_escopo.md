# O que ficou fora do escopo, com motivo

Plano 2, item 8.7. Atualizado em 10/10/2026. Itens "fora" não serão feitos neste plano; "adiado" vai para o Plano 3 ou para depois do congelamento; "condicionado" depende de uma aprovação.

| Item | Situação | Motivo |
| --- | --- | --- |
| Previsão de preços, modelos preditivos e validação temporal fora da amostra | Fora (trabalho futuro) | A pergunta de pesquisa A é sobre interpretação por pessoas sem formação em finanças; ver `docs/validacao_academica.md`, seção 8 |
| Regressão de tendência e detecção automática de cruzamentos | Fora | Decisão N07: só retorno móvel e razão de desempenho |
| Recorte por anos na página de Comparação | Fora | Decisão N02: o recorte fica só na Análise Individual. A lógica de `core/seasonality.py` já comporta a extensão, se o orientador pedir |
| Tabela comparativa com mais de 5 ativos | Fora | Decisão N06 |
| Simulação com datas livres ou novas modalidades | Fora | Decisão N04: manter as janelas móveis existentes; o exemplo "depositar em setembro e retirar em outubro" é atendido pela janela sazonal (N04b) |
| Dividendos, câmbio, inflação, custos e impostos nos cálculos | Fora | O escopo usa preço de fechamento; os avisos informam isso |
| Câmbio (valores em reais) e dividendos/inflação (A5 e A6 do plano de ampliação) | Adiado (Plano 3) | Parecer de 24/10/2026: mudam premissas de cálculo e comunicação; exigem especificação própria depois do congelamento |
| Valuation, preço justo, preço teto, pontuação de ativos e grupo "Criptomoedas recentes" | Fora | Parecer de 24/10/2026 sobre `docs/plano_ampliacao_catalogo_e_analises.md`; criptomoedas recentes seguem pelo "Digitar ticker" |
| Perfil, renda ou objetivos do usuário | Fora | Evita configurar recomendação individual |
| Frequências semestral e anual | **Implementado em 24/10/2026** | Semestres de janeiro a junho e de julho a dezembro; ano civil |
| Filtros de Mercado e Subclasse no seletor da Comparação | **Implementado em 24/10/2026** | Grupo → Subclasse e Mercado → Ativos, com opções encadeadas |
| Nome do projeto, identidade visual, página inicial, "Get Started" e vídeo curto da home | Adiado (Plano 3) | Decisão de 09/10/2026: mudanças visuais depois das melhorias de conteúdo |
| Trabalho colaborativo e autoria compartilhada | Adiado (Plano 3) | Decisão N16: nada confirmado; fora de `docs/contribuicoes.md` por enquanto |
| Chamadas ao modelo de linguagem na versão pública | Fora | Decisão N22: evita custo e abuso de chave exposta; a versão pública usa respostas salvas e validadas ou o texto fixo |
| Revisão dos textos por pessoa da área de educação | Adiado (depois do congelamento) | Decisão N23; entra em versão posterior de correção de textos |
| Integração com a API de modelo de linguagem (7B) | Condicionado | Só se a validação de prompts (7A) cumprir todos os limiares e o orientador aprovar |
| Coleta de dados com usuários (O6) | Condicionado | Exige parecer favorável do CEP antes de começar; apenas adultos, com TCLE |
| Testes automatizados de renderização da interface | Fora | Verificação visual manual por roteiro; há testes estruturais do código das páginas |

## Itens deste plano ainda por fazer

| Item | Situação |
| --- | --- |
| Bloco 7A (validação de prompts) | Não iniciado |
| Bloco 7B (integração com a API) | Condicionado à 7A |
| Bloco 9 (protocolo do CEP e TCLE) | Não iniciado; deve começar cedo por causa do prazo externo |
| **Modo de demonstração com dados salvos** (`ARGOS_DEMO_MODE`) | **Obrigatório antes do congelamento** (decisão de 10/10/2026); `docs/demonstracao.md`, seção 2 |
| Congelamento da versão | Previsto para fev/2027; só depois do modo demo validado |
| Cronograma original no quadro do Relatório Parcial | Aguardando o autor colar o plano aprovado |