# Verificação manual das telas — Argos DataLab

**Finalidade:** registrar a conferência manual das interfaces do Argos DataLab nos modos offline, demonstração e live, incluindo o recurso "Explicar com IA" (etapa 7B).

**Data da verificação:** 12/10/2026 (preenchimento parcial; itens `PENDENTE` serão concluídos em nova verificação)  
**Responsável:** Clériston de Castro Ramos  
**Versão/commit:** e7a5777 (código); documentos posteriores não alteram o comportamento  
**Branch/tag:** main  
**Ambiente:** Windows (Streamlit local)  
**Navegador e versão:** Google Chrome - Versão 154.0.8037.98  

## Regras de execução

- Registrar o resultado imediatamente após cada teste.
- Usar `OK`, `FALHOU`, `NÃO APLICÁVEL` ou `PENDENTE`.
- Anotar passos para reproduzir qualquer falha.
- Anexar captura de tela quando houver erro visual, erro de dados ou falha de funcionalidade.
- Não marcar `OK` se a funcionalidade só funcionar parcialmente.
- Repetir a verificação depois de qualquer mudança relevante na interface, no modo demo, no provedor de dados ou na integração da LLM.

## Legenda dos modos

Há duas chaves independentes. Não confundi-las:

- **Modo demo dos dados** (`core/demo_mode.py`): usa dados locais congelados, sem consultar a fonte externa de preços.
- **Modo da explicação por IA** (`ARGOS_LLM_MODE`): `off` (padrão, botão não aparece), `demo` (respostas salvas em `data/llm_demo.json`, sem chave e sem API) e `live` (chama a API após o clique, com validação).

| Modo | Configuração | Fonte de dados esperada | IA esperada |
|---|---|---|---|
| Offline | Sem internet; modo demo dos dados ativo; `ARGOS_LLM_MODE=demo` | Dados locais salvos | Resposta salva ou texto educativo fixo |
| Demonstração | Modo demo dos dados ativo; `ARGOS_LLM_MODE=demo` | Dados locais congelados | Resposta salva aprovada ou texto fixo (`demo_sem_resposta_salva`) |
| Live | Modo demo dos dados desativado; `ARGOS_LLM_MODE=live`; chave em `OPENAI_API_KEY` | Cache e fonte externa, quando necessária | API somente após clique, com validação |

Parâmetros das respostas gravadas: período de 04/01/2021 a 31/12/2025, frequência diária, taxa livre de risco 0%, ativo AAPL (comparação: AAPL e ^GSPC; janela sazonal: setembro → outubro). Mudar qualquer parâmetro leva ao texto fixo no modo demo.

## Tabela de verificação

| ID | Tela / funcionalidade | Cenário de teste | Offline | Demo | Live | Resultado | Evidência / observação |
|---|---|---|---|---|---|---|---|
| V01 | Inicialização | Aplicação inicia sem erro | PENDENTE | PENDENTE | OK | PENDENTE | Live: app iniciou em 12/10/2026. |
| V02 | Navegação | Todas as páginas do menu abrem | PENDENTE | PENDENTE | PENDENTE | PENDENTE | |
| V03 | Análise individual | Selecionar um ativo e gerar análise | PENDENTE | PENDENTE | OK | PENDENTE | Live: AAPL, 04/01/2021 a 31/12/2025. |
| V04 | Análise individual | Alterar período e frequência | PENDENTE | PENDENTE | PENDENTE | PENDENTE | |
| V05 | Análise individual | Verificar preço, retorno e gráficos | PENDENTE | PENDENTE | PENDENTE | PENDENTE | |
| V06 | Indicadores técnicos | Gerar e visualizar indicadores | PENDENTE | PENDENTE | PENDENTE | PENDENTE | Sem botão "Explicar com IA" nesta tela (fora do escopo da 7B). |
| V07 | Risco e retorno | Exibir volatilidade, drawdown, Sharpe e retorno | PENDENTE | PENDENTE | OK | PENDENTE | Live: explicação gerada com as seis métricas. |
| V08 | Sazonalidade | Selecionar anos, meses e janela de retorno | PENDENTE | PENDENTE | OK | PENDENTE | Live: janela setembro → outubro. |
| V09 | Sazonalidade | Confirmar N, média, mediana e anos positivos, quando aplicável | PENDENTE | PENDENTE | PENDENTE | PENDENTE | Conferir N = 5 na tela e na explicação. |
| V10 | Comparação | Comparar dois ativos | PENDENTE | PENDENTE | OK | PENDENTE | Live: AAPL e ^GSPC. |
| V11 | Comparação | Comparar três a cinco ativos | PENDENTE | PENDENTE | PENDENTE | PENDENTE | Sem botão "Explicar com IA" por desenho: só há explicação com exatamente 2 ativos. Confirmar que o botão não aparece. |
| V12 | Comparação | Verificar Base 100, risco e correlação | PENDENTE | PENDENTE | PENDENTE | PENDENTE | |
| V13 | Simulação | Simular aporte único em período histórico | PENDENTE | PENDENTE | OK | PENDENTE | Live: simulação com aporte periódico e aporte único. |
| V14 | Simulação | Conferir rótulos, aviso histórico e neutralidade | PENDENTE | PENDENTE | PENDENTE | PENDENTE | Atenção a ativos de índice (^IXIC): a tela rotula pontos como moeda. |
| V15 | Textos educativos | Abrir "Como ler este gráfico" | PENDENTE | PENDENTE | PENDENTE | PENDENTE | Devem funcionar sem a IA. |
| V16 | Glossário | Consultar termos e explicações | PENDENTE | PENDENTE | PENDENTE | PENDENTE | |
| V17 | Explicação assistida | Botão "Explicar com IA" aparece somente quando aplicável | PENDENTE | PENDENTE | PENDENTE | PENDENTE | Com `ARGOS_LLM_MODE` ausente (`off`), o botão não deve aparecer em nenhuma tela. |
| V18 | Explicação assistida | Resposta salva é exibida no modo offline/demo | PENDENTE | OK | NÃO APLICÁVEL | PENDENTE | Demo: 5 telas exibiram a resposta gravada em 12/10/2026 (`status: demo`). Offline sem internet: PENDENTE. |
| V19 | Explicação assistida | API é chamada somente após clique no modo live | NÃO APLICÁVEL | NÃO APLICÁVEL | PENDENTE | PENDENTE | Indício: uma linha por clique em `logs/llm_uso.jsonl`. Confirmar que carregar a tela não gera linha. |
| V20 | Explicação assistida | Falha da API ativa fallback educativo | NÃO APLICÁVEL | NÃO APLICÁVEL | OK | OK | 12/10/2026: `sem_chave` e `api_indisponivel:HTTP 401` exibiram o texto educativo fixo. |
| V21 | Explicação assistida | Resposta inválida ou bloqueada ativa fallback seguro | NÃO APLICÁVEL | NÃO APLICÁVEL | PENDENTE | PENDENTE | Coberto por testes automáticos (`tests/test_llm_service.py`). Não provocado na interface. |
| V22 | Explicação assistida | Pedido de previsão ou recomendação aciona frase de recusa correta | NÃO APLICÁVEL | NÃO APLICÁVEL | NÃO APLICÁVEL | NÃO APLICÁVEL | A versão 1 não tem entrada livre; o comportamento de recusa foi avaliado na 7A (casos T009 e T010). |
| V23 | Modo demo | Nenhuma chamada à fonte externa ocorre | PENDENTE | PENDENTE | NÃO APLICÁVEL | PENDENTE | Diz respeito ao modo demo dos dados. |
| V24 | Modo demo | Nenhuma chamada externa à API é necessária | PENDENTE | OK | NÃO APLICÁVEL | PENDENTE | Demo: `input_tokens: 0`, `cost_usd: 0.0`, `attempts: 0`. Offline: PENDENTE. |
| V25 | Limites de uso | Limite de sessão bloqueia chamadas adicionais e exibe mensagem | NÃO APLICÁVEL | NÃO APLICÁVEL | PENDENTE | PENDENTE | Limites: 20 chamadas e US$ 0,50 por sessão (premissa a confirmar com o orientador). Coberto por testes automáticos. |
| V26 | Limites de uso | Limite global bloqueia chamadas adicionais e preserva recursos fixos | NÃO APLICÁVEL | NÃO APLICÁVEL | NÃO APLICÁVEL | NÃO APLICÁVEL | Não há limite global nesta versão; apenas por sessão. Recomenda-se teto de gasto na conta do provedor. |
| V27 | Exportação | Downloads e exportações funcionam, quando disponíveis | PENDENTE | PENDENTE | PENDENTE | PENDENTE | |
| V28 | Mensagens | Mensagens de erro são claras e não expõem chaves, stack trace ou dados internos | PENDENTE | PENDENTE | PENDENTE | PENDENTE | Em 12/10/2026 o texto de contingência não exibiu a chave. Conferir os demais erros. |
| V29 | Neutralidade | Nenhum texto de interface recomenda compra, venda ou aporte | PENDENTE | PENDENTE | PENDENTE | PENDENTE | Incluir as 38 respostas de `data/llm_demo.json`. |
| V30 | Acessibilidade visual | Textos, gráficos, cores e avisos permanecem legíveis | PENDENTE | PENDENTE | PENDENTE | PENDENTE | |

## Registro de falhas

| Falha | Tela | Modo | Passos para reproduzir | Resultado esperado | Resultado observado | Prioridade | Status |
|---|---|---|---|---|---|---|---|
| F01 | Todas com botão | Live | Definir `OPENAI_API_KEY` com valor inválido e clicar em "Explicar com IA" | Texto educativo fixo | Texto educativo fixo exibido (comportamento correto); causa: variável com o texto do comando em vez da chave | Baixa | Resolvida (erro de configuração, não do app) |
| F02 |  |  |  |  |  | Alta / Média / Baixa | Aberta |

## Encerramento

| Item | Registro |
|---|---|
| Itens verificados | ____ de 30 |
| Itens aprovados | ____ |
| Itens com falha | ____ |
| Itens pendentes | ____ |
| Aplicação apta para demo offline | Sim / Não / Condicionada |
| Aplicação apta para publicação live | Sim / Não / Condicionada |
| Próxima ação | Concluir os itens `PENDENTE` e preencher o encerramento. |
