# Decisões do orientador — registro

Registro das decisões e aprovações do Prof. Dr. Arlino Henrique Magalhães de Araújo que condicionam o andamento do projeto. Cada entrada guarda **data, forma da evidência e texto/resumo**.

| Data | Assunto | Decisão | Evidência |
|---|---|---|---|
| 07/10/2026 | Transição 7A → 7B (LLM) | Aprovada **condicionalmente**: só depois que a 7A atingir todos os limiares, condições e limites | Ata `docs/ata_reuniao_2026-10-07.md` |
| 10/10/2026 | Critério de 100% na 7A | Vale para a **resposta bruta** do modelo, antes de qualquer correção do validador. Resposta que o validador bloqueia ou troca por texto fixo conta como **reprovada** na 7A. Na 7B, o usuário vê sempre a saída pós-validação (resposta aprovada ou texto educativo fixo) | Mensagem do orientador (arquivar o texto original) |
| 10/10/2026 | Limite de saída | **Aprovado** 1.400 tokens como teto, não como meta; respostas típicas de 400 a 800 tokens. Se o consumo médio subir muito, reduzir o limite ou usar o gpt-5-nano nos casos simples | Mensagem do orientador |
| 10/10/2026 | Termos em frase negada | **Aprovado** aceitar termos como compra, venda, investir, barato/caro quando a negação for clara, explícita e próxima, e a frase não orientar o usuário a agir. Continuam proibidos usos prescritivos ("compre", "venda", "invista", "é um bom momento para comprar", "o ativo está barato"). Em caso de dúvida: revisão humana ou texto fixo | Mensagem do orientador |
| 10/10/2026 | Um modelo basta? | **Sim**: basta um modelo aprovado para liberar a 7B. O gpt-5 mini é o principal e o único habilitado inicialmente; o gpt-5 nano fica como alternativa de menor custo ou para testes, e só entra na interface se for ajustado e validado separadamente | Mensagem do orientador (arquivar o texto original) |
| 10/10/2026 | Frases de recusa | Aprovadas três frases (geral, previsão, recomendação) e a regra de responder **exclusivamente** com a frase, sem atender parcialmente nem indicar ativo, momento, valor ou decisão. Texto no `docs/protocolo_prompts_llm.md` (prompt v0.5) | Mensagem do orientador |
| 11/10/2026 | Congelamento do protocolo v0.5 | **Aprovado** o congelamento do Protocolo de prompts v0.5 (impressão digital `122195ceb320`) para a execução da 7A. A transição para a 7B segue condicionada aos limiares da 7A. O gpt-5 mini é o modelo principal; o gpt-5 nano só poderá ser habilitado após validação própria. Qualquer mudança no prompt, no esquema, nas instruções ou nas regras do validador exige nova versão, nova impressão digital e nova execução da 7A | Mensagem do orientador de 11/10/2026 (arquivar o texto original) |
| 11/10/2026 | Avaliadores humanos (N26) | Confirmados o avaliador leigo e o técnico; avaliador de neutralidade **pendente**. Detalhes em `docs/pibiti/avaliadores_7a.md` | Ata (texto em `avaliadores_7a.md`) |
| _(a preencher)_ | Aprovação do relatório da 7A e início da 7B | | Mensagem ou ata arquivada |
