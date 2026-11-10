# Decisões do orientador — registro

Registro das decisões e aprovações do Prof. Dr. Arlino Henrique Magalhães de Araújo que condicionam o andamento do projeto. Cada entrada guarda **data, forma da evidência e texto/resumo**.

## Auditoria de 07/11/2026

O documento de sugestões da reunião de 07/11/2026 alerta que textos redigidos como se fossem do orientador são **minutas**: não constituem aprovação, assinatura ou autorização institucional. Por isso, as entradas deste registro foram classificadas pela evidência disponível no repositório:

| Situação | Entradas | Significado |
| --- | --- | --- |
| Com documento no repositório | 07/10/2026 (ata da reunião) | Evidência própria: `docs/ata_reuniao_2026-10-07.md` |
| Com indicação "arquivar o texto original" | Entradas de 10/10, 11/10, 12/10, 24/10 e 25/10/2026 | O original **não foi arquivado**. Valem como registro de trabalho até o orientador confirmar o conteúdo |
| "Encaminhado" | Encaminhamentos de 12/10/2026 | Registram o que foi enviado ao orientador, não uma decisão dele |

**Pendência (R13 do [`plano_reformulacao_preditiva.md`](../plano_reformulacao_preditiva.md)):** confirmar com o orientador quais decisões são dele, arquivar os originais (mensagens com data e remetente) fora do repositório e anotar aqui a confirmação. Até lá, os relatórios do PIBITI não devem citar estas entradas como aprovação formal.


| Data | Assunto | Decisão | Evidência |
|---|---|---|---|
| 07/10/2026 | Transição 7A → 7B (LLM) | Aprovada **condicionalmente**: só depois que a 7A atingir todos os limiares, condições e limites | Ata `docs/ata_reuniao_2026-10-07.md` |
| 10/10/2026 | Critério de 100% na 7A | Vale para a **resposta bruta** do modelo, antes de qualquer correção do validador. Resposta que o validador bloqueia ou troca por texto fixo conta como **reprovada** na 7A. Na 7B, o usuário vê sempre a saída pós-validação (resposta aprovada ou texto educativo fixo) | Mensagem do orientador (arquivar o texto original) |
| 10/10/2026 | Limite de saída | **Aprovado** 1.400 tokens como teto, não como meta; respostas típicas de 400 a 800 tokens. Se o consumo médio subir muito, reduzir o limite ou usar o gpt-5-nano nos casos simples | Mensagem do orientador |
| 10/10/2026 | Termos em frase negada | **Aprovado** aceitar termos como compra, venda, investir, barato/caro quando a negação for clara, explícita e próxima, e a frase não orientar o usuário a agir. Continuam proibidos usos prescritivos ("compre", "venda", "invista", "é um bom momento para comprar", "o ativo está barato"). Em caso de dúvida: revisão humana ou texto fixo | Mensagem do orientador |
| 10/10/2026 | Um modelo basta? | **Sim**: basta um modelo aprovado para liberar a 7B. O gpt-5 mini é o principal e o único habilitado inicialmente; o gpt-5 nano fica como alternativa de menor custo ou para testes, e só entra na interface se for ajustado e validado separadamente | Mensagem do orientador (arquivar o texto original) |
| 10/10/2026 | Frases de recusa | Aprovadas três frases (geral, previsão, recomendação) e a regra de responder **exclusivamente** com a frase, sem atender parcialmente nem indicar ativo, momento, valor ou decisão. Texto no `docs/protocolo_prompts_llm.md` (prompt v0.5) | Mensagem do orientador |
| 11/10/2026 | Congelamento do protocolo v0.5 | **Aprovado** o congelamento do Protocolo de prompts v0.5 (impressão digital `122195ceb320`) para a execução da 7A. A transição para a 7B segue condicionada aos limiares da 7A. O gpt-5 mini é o modelo principal; o gpt-5 nano só poderá ser habilitado após validação própria. Qualquer mudança no prompt, no esquema, nas instruções ou nas regras do validador exige nova versão, nova impressão digital e nova execução da 7A | Mensagem do orientador de 11/10/2026 (arquivar o texto original) |
| 11/10/2026 | Avaliadores humanos (N26) | Confirmados os três avaliadores (leigo, técnico e neutralidade); aceite e declaração de independência e de ausência de conflito em 11/10/2026. Identificação nominal mantida em registro privado (fora do repositório público). Detalhes no registro privado do projeto | Ata (texto em `avaliadores_7a.md`) |
| 11/10/2026 | 7A como revisão técnica interna de qualidade (enquadramento ético provisório) | A 7A pode prosseguir como revisão técnica interna, com planilhas cegas, avaliadores adultos e registro mínimo. Condições: sem dados pessoais além do mínimo; sem dados sensíveis, financeiros, patrimoniais ou de investimento; materiais identificados por códigos; resultados usados só para depuração, ajuste técnico e decisão interna; não apresentar como evidência definitiva de pesquisa, avaliação com usuários ou validação científica antes de definido o enquadramento ético; sem gravação de imagem, voz ou tela; avaliadores podem interromper a qualquer momento | Resposta do orientador de 11/10/2026 (arquivar o texto original) | Aprovado condicionalmente |
| 11/10/2026 | O6 (compreensão e usabilidade) | Permanece condicionada à submissão pela Plataforma Brasil, ao TCLE e a parecer favorável do CEP/UFPI antes de qualquer coleta. Em paralelo, preparar o protocolo ético para o caso de os resultados da 7A virarem dado de pesquisa | Resposta do orientador de 11/10/2026 | Condicionado ao CEP |
| 11/10/2026 | Execução oficial da 7A com o prompt v0.5 | Não aprovada: gpt-5-mini reprovou 1 de 54 respostas em critério obrigatório (item vazio em `limitacoes`). Corrigido na v0.6 (nova impressão digital e nova execução, com conjunto de reserva B). A v0.6 precisa de aprovação do orientador para congelamento | Relatórios em `experiments/llm_7a/results/` (fora do git); resumo em `docs/protocolo_prompts_llm.md` | Em andamento |
| 11/10/2026 | Congelamento do protocolo v0.6 e nova execução formal da 7A | **Aprovado** o congelamento da v0.6 (impressão digital `e3b3574b7430`) para nova execução formal da 7A. A v0.5 não foi aprovada e não pode ser reutilizada como evidência de aprovação, passagem de etapa ou liberação da integração por API; resultados anteriores ficam só como registro histórico. A v0.6 é a única versão válida para a nova rodada. A 7B segue condicionada à aprovação dos resultados da nova execução | Mensagem do orientador de 11/10/2026 (arquivar o texto original) | Aprovado |
| 11/10/2026 | Resultado automático da nova execução da 7A (prompt v0.6) | gpt-5-mini sem falhas em critérios obrigatórios nos 18 casos e nos 8 casos de reserva B; estabilidade 0,8333 e 1,0; custo e tempo dentro dos limites. Falta a avaliação humana (revisão técnica interna, conforme o enquadramento ético provisório). Nenhuma aprovação ainda | Relatórios em `experiments/llm_7a/results/` (fora do git) e resumo em `docs/protocolo_prompts_llm.md` | Parcial |
| 12/10/2026 | Nova sessão de calibração da avaliação humana da 7A | **Aprovada** nova sessão: os três avaliadores analisam **isoladamente as mesmas 12 a 15 respostas novas** do gpt-5 mini (prompt v0.6 congelado) e atribuem nota às três dimensões (clareza, correção e neutralidade; o parecer cita "completude" no lugar de "correção": ver nota abaixo). Esse desenho é necessário para o kappa ponderado ser calculado de forma comparável. O limiar de **kappa ponderado ≥ 0,60 permanece**. Registrar também concordância exata, concordância dentro de um ponto, distribuição das notas e comentários qualitativos, que complementam o kappa e não o substituem | Parecer do orientador de 12/10/2026 (arquivar o texto original) |
| 12/10/2026 | Conversa de auditoria com os avaliadores | **Autorizada** conversa individual antes da nova sessão, com abordagem factual e sem conclusões antecipadas. Se houver confirmação de uso de ferramenta automática, cópia ou compartilhamento indevido, registrar o fato de modo objetivo | Parecer do orientador de 12/10/2026 |
| 12/10/2026 | Rodadas anteriores e resposta esperada de recusa | Rodada 1, rodada 2 e terceira tentativa permanecem **arquivadas como tentativas não aprovadas**. A correção da `resposta_esperada` dos casos de recusa está adequada (a regra 9 exige somente a frase fixa no resumo) | Parecer do orientador de 12/10/2026 |
| 12/10/2026 | Efeito da falha da avaliação humana | A falha **não impede a continuidade das atividades técnicas**, mas **impede a declaração de aprovação da 7A e a liberação formal da 7B** até a conclusão da nova sessão | Parecer do orientador de 12/10/2026 |
| 12/10/2026 | Continuidade da rodada 4 de calibração humana com respostas da execução complementar v0.6 | **Aprovada.** Podem compor as planilhas cegas as respostas válidas da execução de 12/10/2026 (prompt v0.6, impressão digital `e3b3574b7430`). A resposta `c10_simulacao_aapl`, bloqueada em `sem_recomendacao` pelo termo "aplicar" na expressão descritiva "ao aplicar um único aporte no início do período", é preservada nos registros, classificada como **falso positivo do validador** e não é enviada aos avaliadores. Respostas de texto idêntico ao de rodadas anteriores também não entram | `respostas_rodada4.jsonl`; texto da decisão de 12/10/2026 (arquivar o original) |
| 12/10/2026 | Referência para o critério de 100% da 7A | **Mantida** a execução oficial da v0.6 (0 falhas em 78 respostas). A execução complementar de 12/10/2026 tem finalidade específica de alimentar a sessão de calibração humana e **não substitui, recalcula nem reduz** os resultados da execução oficial | Relatório da execução oficial da v0.6; texto da decisão de 12/10/2026 |
| 12/10/2026 | Alteração do validador para o uso descritivo de "aplicar" | **Adiada.** Qualquer ajuste futuro exige nova versão, nova impressão digital, testes específicos e registro metodológico. Não alterar prompt, esquema nem validador durante a rodada 4 | Registro técnico da rodada 4; texto da decisão de 12/10/2026 |
| 12/10/2026 | Encerramento da 7A e liberação da 7B | **7A considerada concluída para fins de progressão**; 7B **formalmente liberada** para implementação controlada, com todos os requisitos já aprovados (gpt-5 mini; gpt-5 nano fora da interface; prompt v0.6 `e3b3574b7430`; só contexto JSON do Argos; sem entrada livre; sem navegação, ferramentas ou código; esquema JSON estrito; validação antes de exibir; bloqueio de recomendação, previsão, inconsistência e termo proibido; fallback educativo fixo; 1.400 tokens; timeout de 20 s e no máximo 2 retentativas; registro de modelo, versão, tokens, custo, status e motivo de bloqueio; segredo fora do repositório; limites de custo e uso; sem apresentar a LLM como recomendação ou previsão; textos fixos sem LLM; modo de demonstração com respostas salvas ou fallback offline). O kappa ponderado abaixo de 0,60 em clareza e neutralidade e 0,595 em um par de correção é **limitação metodológica registrada**, não aprovação estatística da rubrica; não será omitido, reduzido nem reinterpretado | Texto da decisão de 12/10/2026 (arquivar o original, na forma em que o orientador o enviou); relatório da rodada 4 |
| 12/10/2026 | Limiar de kappa | **Mantido** o limiar de 0,60, sem reclassificação retroativa; a liberação decorre de decisão de orientação baseada no conjunto de evidências | Texto da decisão de 12/10/2026 |
| 12/10/2026 | Melhoria futura do protocolo de avaliação humana | **Planejada:** reancorar a escala com exemplos, ampliar o conjunto de itens com maior variação de qualidade e reavaliar a concordância com amostra mais ampla | Texto da decisão de 12/10/2026 |

## Registro da avaliação humana da 7A (prompt v0.6)

Registro do projeto, **sem decisão do orientador até esta data**. Serve para que a trilha do que foi feito, descartado e decidido fique escrita. Planilhas e relatórios ficam em `experiments/llm_7a/results/final/` (fora do git). Nenhuma nota foi alterada depois de enviada.

| Data | Evento | Resultado | Situação |
|---|---|---|---|
| 11/10/2026 | Primeira rodada de avaliação (78 respostas do gpt-5-mini: 54 principais + 24 de reserva B; pasta `avaliacao`, guardada como `avaliacao_rodada1`) | Uma primeira versão veio com todas as notas 5 e kappa 1,0, sem variação: **descartada**, pois o kappa de séries sem variação não mede concordância (o código foi corrigido: kappa indeterminado quando não há variação, e alerta para notas quase todas iguais). Na versão seguinte: nota média 4,731; alucinação 0,0135; correção factual 0,9952; limitações 0,9459; "não concluir" 1,0; estabilidade 0,8846; custo US$ 0,001484; tempo 3,35 s. Kappa de clareza **0,318 (leigo–neutro), 0,444 (leigo–técnico), 0,444 (neutro–técnico), abaixo de 0,60** | Critérios automáticos e médias dentro dos limites; concordância de clareza **não atingiu** o limiar |
| 12/10/2026 | Reunião de calibração com os três avaliadores sobre o significado de cada nota de clareza (1 a 5), seguida de repetição com as mesmas planilhas | A repetição sobre os mesmos itens **não é usada** como medida de concordância: os avaliadores já conheciam as respostas e acabavam de combinar os critérios (serve só como recalibração) | Não oficial |
| 12/10/2026 | Segunda rodada com respostas novas (20 itens, 1 repetição por caso, mesmo prompt v0.6 congelado, só gpt-5-mini, nova execução do mesmo prompt) | Kappa de clareza **0,286 (leigo–neutro), −0,154 (leigo–técnico), 0,167 (neutro–técnico)**; neutralidade com nota 5 em todos os itens (kappa indefinido); correção com kappa 1,0 apenas porque os três deram 4 nas mesmas 5 respostas de recusa (S005, S007, S009, S012, S018) e 5 nas demais. Concordância exata em clareza: 70% a 75%; dentro de 1 ponto: 100% | **Não aprovada** |
| 12/10/2026 | Verificação da rodada 2 | (a) Comentários iguais entre avaliadores em 14 a 15 das 20 respostas, a partir de poucas frases-padrão, inclusive entre o avaliador leigo (que não vê a resposta esperada) e o técnico: a independência das notas **precisa ser confirmada com cada avaliador**; se houve combinação ou preenchimento em lote, a rodada é inválida. (b) A `resposta_esperada` dos casos negativos manda descrever os dados após a frase de recusa, mas a regra 9 do prompt v0.6 (aprovada) manda responder **exclusivamente** com a frase fixa, sem métricas; o validador (`recusa_correta`) exige o mesmo e passou em 100%. As notas 4 em correção nessas recusas decorrem dessa inconsistência do material, não de falha do modelo, e podem ter afetado também a primeira rodada | Rodada 2 **descartada** como medida oficial de concordância |
| 12/10/2026 | Terceira tentativa (planilhas S001–S020 reenviadas pelos avaliadores) | Os itens e as respostas são **idênticos aos da rodada 2** (não são respostas novas) e a planilha do avaliador técnico ainda traz a `resposta_esperada` antiga dos casos de recusa. Kappa de clareza **−0,067 (leigo–neutro), 0,077 (leigo–técnico), −0,231 (neutro–técnico)**; neutralidade: 18 notas 5 e 2 notas 4 nos três, com kappa −0,111. Inconsistências na planilha técnica: `correcao_factual_ok = nao` em 10 de 20 itens, inclusive em itens cujo comentário diz "correta extração" (S010, S014, S016, S020) e em itens cuja resposta traz todas as métricas do contexto com os valores exatos (S003, S004, S019); comentários-padrão repetidos 4 a 6 vezes por avaliador e sem relação com o conteúdo de alguns itens | **Descartada**; nenhuma nota usada |
| 12/10/2026 | Parecer do orientador sobre a falha da avaliação humana | Aprovada a nova sessão de calibração (12 a 15 respostas novas, três avaliadores isolados, as três dimensões, kappa ≥ 0,60 mantido, indicadores complementares obrigatórios no relatório). Autorizada a conversa de auditoria. Rodadas anteriores arquivadas como não aprovadas. 7A não aprovada e 7B não liberada até a conclusão da nova sessão | Em preparação |
| 12/10/2026 | Rodada 4 (15 respostas novas, T001–T015, prompt v0.6; os três avaliadores nas três dimensões) | Kappa ponderado quadrático por par (técnico–neutro / técnico–leigo / neutro–leigo): **clareza 0,189 / 0,423 / 0,595; correção 0,595 / 0,856 / 0,712; neutralidade 0,595 / 0,423 / 0,595.** Concordância exata de 73% a 87%; dentro de 1 ponto: 100% em todos os pares e dimensões. Notas concentradas em 4 e 5 (clareza e neutralidade com apenas duas categorias usadas). T010 (recusa): os três baixaram a correção (3, 3 e 2) por haver texto além da frase fixa, embora a planilha informasse que os demais campos são texto fixo. Comentários distintos e específicos por item | Kappa **abaixo de 0,60** em clareza e neutralidade; correção abaixo em um par (0,595) |
| 12/10/2026 | Decisão do orientador após a rodada 4 | 7A considerada concluída para progressão; 7B liberada com condições; kappa registrado como limitação (ver tabela principal) | Registrada |

Consequências registradas:

1. O kappa ≥ 0,60 **não foi atingido** em nenhuma das rodadas (a primeira e a segunda válidas como tentativas; a terceira descartada; a quarta, oficial, ficou abaixo em clareza e neutralidade). Pela decisão de 12/10/2026 (após a rodada 4), a 7A é considerada concluída para progressão e a 7B foi liberada com condições; o resultado do kappa permanece registrado como limitação e não como aprovação estatística.
2. O prompt, o esquema, as instruções e o validador da v0.6 **não foram alterados**. A correção da `resposta_esperada` dos casos de recusa altera o material dos avaliadores, não o prompt; será feita antes da próxima rodada e comunicada ao orientador.
3. Próxima rodada: respostas novas, cada avaliador isolado (sem conversar nem ver as planilhas dos outros), comentários escritos por quem avalia, orientação de que nota 5 em tudo deve ser rara. O kappa oficial será o dessa rodada; as demais métricas continuam as do relatório da primeira rodada.
4. Ponto de método a submeter ao orientador: com notas concentradas em 4 e 5, o kappa ponderado é instável (concordância dentro de 1 ponto foi de 100%). Qualquer outro critério só vale depois de registrado aqui, antes de rodar a próxima rodada.
5. Os textos originais das mensagens do orientador e dos aceites dos avaliadores ficam em registro privado, fora do repositório público.

Nota sobre as dimensões: o parecer de 12/10/2026 cita "clareza, completude e neutralidade". A rubrica usada nas planilhas e no `analyze` é **clareza, correção e neutralidade** ("os números e conceitos estão corretos?"). Até confirmação por escrito do orientador, a sessão usa a rubrica vigente (correção); se ele quiser avaliar "completude" no lugar, a rubrica, as planilhas e o relatório precisam mudar antes da sessão.

## Encaminhamentos ao orientador (12/10/2026)

| Data | Assunto | Registro | Status |
|---|---|---|---|
| 12/10/2026 | Limites de uso da LLM | Foram apresentados ao orientador os limites propostos para a integração: até 20 chamadas por sessão e teto estimado de US$ 0,50 por sessão, com bloqueio e fallback educativo após o limite. Não há limite global nesta versão. | Encaminhado |
| 12/10/2026 | Política de dados do provedor | Foi apresentada ao orientador a política de uso de dados da API. A integração enviará somente contexto estruturado e dados públicos/agregados da análise, sem dados pessoais, financeiros, patrimoniais ou identificadores de usuários. Segundo a documentação do provedor (consulta em 12/10/2026), dados enviados à API não são usados para treinar modelos por padrão, salvo adesão explícita ao compartilhamento, e os registros de monitoramento de abuso são retidos por até 30 dias. | Encaminhado |
| 12/10/2026 | Relatório da rodada 4 da 7A | Foi entregue ao orientador o relatório da rodada 4, incluindo resultados automáticos, avaliação humana, valores de kappa, concordância dentro de um ponto, baixa variação das notas, item T010 e limitação metodológica registrada. | Encaminhado |

Fonte da política de dados: https://developers.openai.com/api/docs/guides/your-data

## Prioridades para a continuidade do Argos DataLab (12/10/2026)

| Ordem | Prioridade | Observação |
|---|---|---|
| 1 | Implementar e estabilizar a 7B: integração controlada da API, validação das respostas, limites de uso, logs, fallback educativo e funcionamento nos modos offline, demonstração e live | Checklist em `docs/checklists/verificacao_manual_telas.md` |
| 2 | Implementar o modo de dados salvos e concluir o congelamento da versão de demonstração, para apresentar o Argos sem internet, fonte externa de dados ou API | |
| 3 | Iniciar já a preparação documental do O6: protocolo, instrumentos, TCLE, plano de recrutamento, tratamento de dados e materiais para eventual submissão à Plataforma Brasil e ao CEP/UFPI | Não autoriza coleta com usuários; a coleta depende do enquadramento ético, do TCLE e do parecer favorável aplicável |
| 4 | Somente após estabilizar a 7B e preparar o O6: comparação de três a cinco ativos, com sazonalidade comparada, alinhamento temporal e textos explicativos | |
| 5 | Prompt v0.7 e nova melhoria do protocolo de avaliação humana: registradas como melhoria futura, salvo problema técnico, de segurança ou de neutralidade que exija correção imediata | |

Sequência do próximo ciclo: 7B controlada, modo demo com dados salvos, preparação documental do O6 em paralelo, comparação de três a cinco ativos, congelamento da demo e documentação final.

Status: recebida em 12/10/2026. Original da mensagem: a arquivar fora do repositório.

## Parecer sobre o plano de ampliação do catálogo e de novas análises (24/10/2026)

Plano avaliado: `docs/plano_ampliacao_catalogo_e_analises.md`. Autorização de desenvolvimento gradual, sem nova aprovação para cada detalhe, dentro dos limites abaixo. A aprovação não confirma a verificação dos tickers nem substitui as autorizações éticas do O6.

| Assunto | Decisão |
|---|---|
| Identidade do Argos | Aproveitar formas de apresentação de plataformas de mercado, **sem** valuation, preço-alvo, preço justo ou teto, recomendação, pontuação, classificação de ativos como oportunidade ou previsão |
| Catálogo | **Aprovada** a ampliação de 120 para cerca de 150 ativos, por diversidade de classes, setores, mercados e usos. 150 é referência, não meta: o catálogo pode fechar com menos. Cada inclusão passa por conferência técnica (ticker, histórico, moeda e mercado, classificação, coleta e processamento, documentação e modo demo). Classificações podem ser corrigidas (ex.: ETFs de ouro ou criptoativos classificados pela exposição). Substituições pontuais dispensam nova consulta, desde que justificadas no registro do catálogo |
| Critérios para criptomoedas | Pelo menos 3 anos de histórico na fonte; relevância por capitalização (fonte e data registradas); diversidade de usos; dados suficientes; nenhuma seleção motivada só por altas recentes. Os 3 anos são critério de entrada, não garantia de suficiência para todas as análises |
| Grupo "Criptomoedas recentes" | **Não criar** nesta rodada; esses ativos seguem pelo "Digitar ticker", com alertas de dados |
| Caso DHN | Pode ser exemplo didático, separando observação de hipótese: o salto de preço não autoriza afirmar baixa liquidez, concentração, manipulação ou erro da fonte sem evidência adicional |
| A1 — variação por janelas | **Aprovada.** Mostrar as datas usadas, "—" sem histórico suficiente, distinguir variação acumulada de taxa equivalente anual e deixar explícito se usa todo o histórico ou só o recorte da interface |
| A2 — referência automática | **Aprovada**, sem regressão, beta ou cruzamentos (não altera a N07). Referência de comparação, não meta; escolha explicada; pode ser desativada e, se viável, trocada; período comum ou aviso de disponibilidade; aviso de moeda e calendário. Sem referência adequada, não mostrar |
| A3 — panorama do catálogo | **Aprovada com implementação gradual**: por grupo selecionado, ordenação inicial por nome, retorno ao lado de volatilidade e queda máxima, período e histórico indicados, aviso de que a ordem não é recomendação, falhas parciais sem preencher com zero, cache e limites. Sem destacar "vencedores" ou "oportunidades". Pode ser reduzida ou adiada |
| A4 — alertas de qualidade | **Aprovada, prioridade alta.** Indicar situações que merecem atenção, sem concluir erro, fraude ou manipulação. Limiares são heurísticas iniciais documentadas e testadas, considerando a classe do ativo; ausência de volume não reprova séries em que o campo não é pertinente |
| A7 — recuperação das quedas | **Aprovada.** Distinguir início, fundo, recuperação, duração e queda não recuperada ("não recuperado até a última observação disponível", sem estimativa). Definir a unidade da duração (dias corridos, observações ou períodos) |
| A8 — maiores altas e quedas | **Aprovada**, com datas e frequência. Descrever os extremos sem afirmar que poucos dias explicam o resultado, salvo se essa contribuição for calculada |
| A5 e A6 — câmbio, dividendos e inflação | **Plano 3**, após o congelamento, com especificação própria (fonte, alinhamento de datas, metodologia, limitações, testes, textos e contexto da LLM). Preço ajustado deve ser descrito como a fonte o trata, sem equivaler a simulação completa de reinvestimento |
| Cronograma | Nov/2026: A4, A1, A7, A8. Nov–dez/2026: catálogo. Dez/2026: A2 e primeira versão da A3. Jan/2027: dados salvos, integração e revisão. Fev/2027: congelamento. Depois: A5, A6 e extensões. A estrutura do modo demo vem antes do catálogo ampliado; os dados salvos podem ser regenerados depois. O O6 segue em paralelo |
| Ordem de preservação em caso de conflito | 1) estabilidade e segurança da 7B; 2) modo demo; 3) O6; 4) alertas e análises simples; 5) catálogo; 6) referência automática; 7) panorama |
| Explicação assistida | Novas funções nascem com "Como ler este gráfico". Catálogo novo não exige mudar o prompt congelado; cada novo tipo de análise ou mudança no contexto da API passa por testes de compatibilidade, rastreabilidade e neutralidade. Visualização não coberta pela LLM pode sair só com explicação fixa |
| Registros pedidos | Critérios e lista final do catálogo; inclusões, substituições e exclusões justificadas; metodologia dos novos cálculos; testes e conferência das telas; atualização do modo demo; limitações; ajustes do cronograma |

Status: recebido em 24/10/2026. Original do parecer: a arquivar fora do repositório.

## Orientação sobre a validação do deploy (25/10/2026)

| Assunto | Orientação |
|---|---|
| Encerramento das fases 1 a 3 | Registrar como "implementação concluída; validação do deploy pendente" até a conferência da versão publicada no Streamlit Community Cloud; depois, "publicação verificada", sem marcar itens como aprovados antes da conferência |
| Conferência do deploy | Fazer agora, enquanto as mudanças estão recentes, em tabela com data, responsável, branch e commit, cobrindo A4, A1, A7, A8, catálogo (148 ativos), A2, A3, explicação assistida e navegação/exportação |
| Modo demo | Primeiro snapshot do catálogo ampliado pode ser antecipado após a conferência do deploy; não substitui a atualização final e o roteiro completo sem internet de janeiro/2027 |
| O6 | Preparação documental segue em paralelo; antes da coleta, identificar a versão da plataforma avaliada e os recursos disponíveis aos participantes |
| Novas funcionalidades | Não abrir neste ciclo; foco em versão verificada, reproduzível e pronta para avaliação e demonstração |

Status: recebido em 25/10/2026. Original da mensagem: a arquivar fora do repositório.

## Reunião de 07/11/2026: proposta de reformulação

| Assunto | Conteúdo | Situação | Evidência |
|---|---|---|---|
| Novo direcionamento | Incorporar previsão de séries temporais, aprendizado de máquina e apoio à decisão de investimento, com linguagem acessível e rigor metodológico | **Proposta**, a confirmar por escrito | Reunião de 07/11/2026; documento de sugestões `reunião 07.11.2026.docx` (fora do repositório) |
| Detalhamento | Três camadas (descritiva, preditiva, decisória); recomendação pública só após análise regulatória; ambiente experimental restrito; nova família de protocolo da LLM; validação temporal fora da amostra; congelamento só da versão histórica | Sugestões, não decisões | Mesmo documento |
| Decisões pendentes | R1 a R13 | Aguardando o orientador | [`plano_reformulacao_preditiva.md`](../plano_reformulacao_preditiva.md), seção 5 |

Status: proposta recebida em 07/11/2026. Nenhuma regra vigente foi alterada.

## Aprovação de R6, R7, R8 e dos critérios de elegibilidade do piloto preditivo (08/11/2026)

Documento avaliado: [`docs/preditivo/protocolo_piloto_v1.md`](../preditivo/protocolo_piloto_v1.md) (revisão 1). Abrangência: experimento local, sem disponibilização pública de previsões ou recomendações. Autoriza preparação, implementação e execução do piloto quantitativo; não autoriza integração ao aplicativo público nem significa que modelos ou sinais estão validados.

| Assunto | Decisão |
|---|---|
| R6 — Ativos | `PETR4.SA` e `VALE3.SA`, cada um com treinamento, previsões, métricas, backtest e elegibilidade próprios; a aprovação de um não autoriza o outro; sem generalização para o catálogo. `BOVA11.SA` e `SMAL11.SA` reservados para rodada futura; troca após os resultados exige outro experimento, sem apagar o original |
| R6 — Horizonte e alvo | Diário; 20 intervalos entre observações; decisão após o fechamento de `t`, entrada no fechamento de `t + 1`, saída em `t + 21`; alvo `P_(t+21) / P_(t+1) − 1`, substituindo `P_(t+20) / P_t − 1`; registrar `decision_date`, `entry_date` e `label_end_date` e usar essas datas na exclusão e no expurgo |
| R6 — Datas | Desenvolvimento de 02/01/2008 a 30/12/2021; separação de 20 pregões; período final a partir do 21º pregão de 2022; corte em 30/10/2026; datas efetivas no manifesto e no relatório |
| R6 — Reestimação | Avaliação sequencial com reestimação no início de cada ano; o treino pode usar o período final já transcorrido só com alvos realizados; escolha do `alpha` fixa, com validação interna protegida; "teste usado uma única vez" = uma única avaliação final do procedimento congelado |
| R7 — Estratégia | Exposto quando `ŷ > c`, senão caixa; sem venda a descoberto nem alavancagem; decisões a cada 20 pregões, execução no fechamento seguinte, sem sobreposição de posições. Regra de retorno absoluto acima do custo, não de excesso sobre o CDI |
| R7 — Custos | 0,05% de negociação + 0,05% de slippage = 0,10% por lado; ida e volta 0,20%; `c = 0,002`; sem venda e recompra artificiais; comprar e manter com a mesma convenção; sensibilidade em 0%, 0,10%, 0,20% e 0,30% por lado, sem escolha retrospectiva |
| R7 — Caixa | CDI diário (SGS 12) coletado e congelado, com unidade, conversão e acumulação registradas; usado só na contabilização retrospectiva; resultados antes de impostos. Experimentos de aportes ficam para rodada posterior |
| R8 — Preços | Fechamento ajustado para alvo, variáveis e desempenho da estratégia, com consistência de ajuste entre abertura, máxima, mínima e fechamento; descrição "Retorno aproximado com ajustes da fonte para proventos e desdobramentos, antes de impostos e de custos não modelados"; triagem ajustado × não ajustado com investigação documentada; coleta congelada com manifesto e hashes |
| Critério 1 | R² fora da amostra estritamente maior que zero, sem arredondamento |
| Critério 2 | Diebold-Mariano com `p < 0,10` a favor do candidato; nota metodológica prévia (perda quadrática, hipótese unilateral, sinal, Newey-West com 19 defasagens); revisão da adequação antes da execução; mudança de teste só antes de abrir os resultados; não calculável não é aprovação |
| Critério 3 | R² > 0 em pelo menos 5 de 8 dobras; todas as dobras no relatório |
| Critério 4 | (A ∧ B) ∨ C: A = retorno líquido acima do caixa; B = drawdown máximo menor que o de comprar e manter; C = retorno líquido acima de comprar e manter. Ramo C sem limite adicional de drawdown, com destaque obrigatório se o drawdown for maior |
| Critério 5 | Critério 4 mantido com o dobro do custo-base, com os mesmos sinais e calendário |
| Resultado | Se algum critério falhar: "Não houve evidência suficiente para habilitar o sinal", com o experimento cientificamente concluído. Se todos forem atendidos: elegível só para integração experimental restrita, após conferência; sem liberação pública nem transferência para outros ativos, modelos ou horizontes |
| Condições para abrir a avaliação final | Incorporar as decisões ao protocolo; registrar a versão consolidada e seu hash; congelar dados e configuração; testar alinhamento e expurgo (divisões externas e internas); conferir custos, caixa e referências; fechar a nota metodológica; registrar a confirmação real desta decisão. Implementação local autorizada enquanto isso |

**Evidência:** texto recebido pelo desenvolvedor em 08/11/2026 e incorporado ao protocolo no mesmo dia. O texto indica "Data proposta: 08/11/2026" e pede, entre as condições, o registro da confirmação real. **Pendente:** arquivar fora do repositório a mensagem original do orientador (data e remetente), conforme a auditoria de 07/11/2026. Sem essa confirmação, a avaliação final não é aberta (protocolo, seção 12).

Status: recebida em 08/11/2026. Confirmação original: a arquivar.

## Nota metodológica do teste estatístico (08/11/2026)

Documento avaliado: [`docs/preditivo/nota_teste_estatistico.md`](../preditivo/nota_teste_estatistico.md). Objeto: decisões N1 a N5, anteriores à abertura da avaliação final. O procedimento é critério exploratório de elegibilidade do piloto local, sem equivaler a certificação estatística de recomendação de investimento.

| ID | Decisão |
|---|---|
| N1 | Amostra: todas as datas previstas no período final com alvo integralmente realizado, uma previsão por pregão, cada ativo separado; igual à do R² do critério 1. Lista das datas elegíveis gerada pelo calendário, horizonte e disponibilidade do alvo e fixada antes, sem consultar erros. Sem selecionar datas favoráveis, excluir erros elevados ou agregar ativos; modelo vigente identificado; data sem alvo distinta de falha de previsão; sem descarte silencioso |
| N2 | `p = 1 − Φ(DM)`, `DM = d̄ / √(V̂/T)`, `d_t = y_t² − (y_t − ŷ_t)²`; `p < 0,10` estrito, em precisão completa; variância centrada, dividida por `T`, 19 defasagens, pesos de Bartlett; sem correção de Harvey-Leybourne-Newbold no p-valor decisório. Justificativas como escolhas operacionais, sem afirmar que a amostra elimina problemas de aproximação nem que 19 defasagens capturam toda a dependência |
| N3 | Mínimo operacional de 200 datas, sem valor de prova de suficiência ou poder. Não calculáveis: `T < 200`, variância nula ou não finita, entradas não finitas, previsões ausentes, desalinhamento; distinguir erro numérico de variância nula; proibido ajustar a variância ou remover datas |
| N4 | Diebold-Mariano mantido como filtro exploratório; sem troca de teste após os resultados. Substituir a afirmação de que o teste não aumenta o risco de falso positivo pela ressalva aprovada (nível nominal de 10% não assumido como taxa efetiva). Sem estudo de simulação exigido agora |
| N5 | Clark-West (`f_t = y_t² − (y_t − ŷ_t)² + ŷ_t²`) só como diagnóstico: não substitui, não altera a elegibilidade, não é segunda chance, é sempre apresentado; divergência registrada sem concluir ganho encoberto |
| Ajustes finais | Incorporar as decisões; substituir a garantia pela ressalva; registrar a amostra elegível antes da avaliação; R² com denominador nulo "não calculável"; testes de não finitos e desalinhamento; testes matemáticos pequenos separados do mínimo de 200; registrar commit e hash da configuração final. Implementação e testes unitários autorizados, sem abrir os resultados finais |

**Encaminhamento:** com a confirmação do orientador e a incorporação dos ajustes, a condição 7 do protocolo pode ser registrada como cumprida. A abertura da avaliação final segue dependendo das demais condições do protocolo.

**Evidência:** texto recebido pelo desenvolvedor em 08/11/2026 ("Data proposta: 08/11/2026") e incorporado à nota e ao protocolo no mesmo dia. **Pendente:** arquivar fora do repositório a mensagem original do orientador (data e remetente), conforme a auditoria de 07/11/2026.

Status: recebida em 08/11/2026. Confirmação original: a arquivar.

## Manifestação sobre o snapshot `snap-20261108-01` (08/11/2026)

| Assunto | Decisão |
|---|---|
| Situação | Coleta concluída; snapshot coletado e congelado; integridade com pendências; uso na modelagem condicionado ao tratamento documentado; avaliação final bloqueada. O congelamento preserva e identifica os arquivos, sem considerar todas as observações adequadas para qualquer cálculo |
| PETR4 em 02/04/2014 | "Violação de consistência OHLC: fechamento abaixo da mínima; campo responsável não determinado." Vedado substituir pela mínima, ampliar a faixa, interpolar, atribuir causa não confirmada ou corrigir o arquivo original. O tratamento deve considerar retornos, alvos, preços de execução e indicadores |
| VALE3 em 14/08/2012 e 05/09/2012 | Inconsistências da abertura; tratamento por campo, sem excluir a linha inteira; confirmar pelo código quais indicadores consomem cada campo |
| Conferência externa | Pontual, com prazo, arquivada mesmo sem conclusão. **Se não houver fonte verificável**, política conservadora: preservar os originais; invalidar na visão derivada o campo questionado e só os cálculos que dependem dele; sem estimativas; calendário preservado (sem remover datas nem recalcular deslocamentos) |
| Registro obrigatório | Data e campo questionados; regra aplicada; fonte da conferência; variáveis e amostras invalidadas; datas afetadas; impacto na cobertura do desenvolvimento; preservação do calendário e dos originais. Tratamento não escolhido pelo R² ou pelo backtest |
| Fator de ajuste em 03/04/2014 | Retratação considerada correta; a sequência (hipótese no ensaio, provento identificado, explicação, correção) deve ser mantida. As 62 datas com provento e o desdobramento ficam como resultados da conferência, não como anomalias |
| Árvore alterada na coleta | O registro permanece. Aceito como desvio documental justificado, sem repetir a coleta, com a evidência arquivada ([`../preditivo/evidencias/arvore_coleta_snap-20261108-01.md`](../preditivo/evidencias/arvore_coleta_snap-20261108-01.md)) |
| Embargo nas reestimações | **Confirmado**: embargo nas fronteiras dos blocos; nas reestimações de 2023 a 2026, sem nova interrupção; ajustes só com alvos realizados; expurgo obrigatório, inclusive na seleção interna |
| Autorizações | Cópia de segurança com hashes; versionamento dos metadados e do relatório; implementar e testar a política; documentar as amostras afetadas; consolidar a configuração; executar o desenvolvimento oficial. Avaliação final bloqueada |

**Andamento em 08/11/2026.** A conferência externa encontrou fonte verificável (B3, série histórica oficial) para as três datas. Ela identificou os campos divergentes: no PETR4, o fechamento (16,56 na B3, contra 15,56); na VALE3, a máxima em 14/08/2012 e a mínima e a máxima em 05/09/2012. As aberturas da VALE3 conferem com a B3. Como a política conservadora foi aprovada para o caso **sem** fonte verificável, a escolha entre invalidar e usar o valor da B3 na visão derivada é uma decisão nova (P1, abaixo), e o desenvolvimento oficial aguarda essa decisão. O impacto de cada opção, medido sem nenhum modelo, está no relatório do snapshot.

| # | Decisão pendente | Opções |
|---|---|---|
| P1 | Tratamento das três ocorrências, diante da fonte verificável | (a) invalidar os campos divergentes (política conservadora); (b) usar na visão derivada o valor da B3, convertido para a base ajustada pelo fator da própria data, sem alterar o snapshot |

**Evidência:** texto recebido pelo desenvolvedor em 08/11/2026. **Pendente:** arquivar fora do repositório a mensagem original (data e remetente).

Status: recebida em 08/11/2026. Confirmação original: a arquivar.

## P1 — Tratamento das ocorrências de integridade (08/11/2026)

Decisão: aprovar substituições pontuais pelos valores da B3 na visão derivada, preservando integralmente o snapshot original. Escolha feita antes do desenvolvimento oficial e sem consultar desempenho de modelos; o fundamento é a existência de fonte identificada, verificável e pertinente ao registro da negociação (a menor perda de amostras é consequência, não justificativa).

| Ativo e data | Campo | Original (Yahoo) | Aprovado (B3) |
|---|---|---:|---:|
| PETR4, 02/04/2014 | Fechamento | 15,56 | 16,56 |
| VALE3, 14/08/2012 | Máxima | 37,75 | 38,64 |
| VALE3, 05/09/2012 | Máxima | 33,89 | 33,19 |
| VALE3, 05/09/2012 | Mínima | 32,77 | 32,47 |

Condições: arquivar o registro exato da B3 e sua identificação; verificar moeda, mercado e base de cotação; justificar a transformação para preços ajustados, conferindo especialmente o fator associado ao fechamento corrigido da PETR4 (se não for justificável de forma reproduzível, a PETR4 volta à invalidação); recalcular variáveis, alvos e execução; preservar datas e arquivos originais; registrar versão e hash da política. Não se escolhem campos de fontes diferentes conforme o resultado no modelo; a exceção fica limitada a estas ocorrências. Permanecem inalterados ativos, horizonte, variáveis, grade de `alpha`, critérios, embargo, expurgo e o bloqueio da avaliação final. Concluídas as verificações, o desenvolvimento oficial da v1 está autorizado.

**Cumprimento das condições (08/11/2026):** registros exatos da B3 identificados (arquivo, linha, código, mercado à vista, R$, fator de cotação 1, ISIN e hash da linha); o método multiplicativo de ajuste reproduz o fator da fonte nas datas afetadas (PETR4 de 2008 a 2014 e VALE3 em 2012, diferença relativa máxima de 5,6e-07); o fator da PETR4 foi recalculado com o fechamento corrigido, porque a data ex de 03/04/2014 usa o fechamento de 02/04/2014; faixa OHLC consistente nas três datas da visão derivada; impacto final sem perda de amostras. Política `experiments/preditivo/politica_qualidade.json`, versão 1.0, SHA-256 `f75598b06fa9a1100fecc5783b78c1874642686223ecb5b60e05096cf8e88975`. Detalhes no [relatório do snapshot](../preditivo/snapshot_snap-20261108-01.md), seção 7.

**Evidência:** texto recebido pelo desenvolvedor em 08/11/2026. **Pendente:** arquivar fora do repositório a mensagem original (data e remetente).

Status: recebida em 08/11/2026. Confirmação original: a arquivar.

## D1 — Encerramento do piloto preditivo v1 (08/11/2026)

Data: 08/11/2026, sujeita à confirmação do orientador.

Decisão: encerrar a v1 por não elegibilidade, sem executar a avaliação final.

Fundamento: PETR4.SA e VALE3.SA apresentaram R² positivo em três das oito dobras de desenvolvimento, abaixo do mínimo de cinco exigido pelo critério 3. Como os critérios são cumulativos, um resultado favorável no período final não compensaria esse requisito; não é necessário consumir a avaliação final para confirmar uma decisão de elegibilidade já determinada pelo protocolo.

Consequências:
- nenhum sinal da v1 será habilitado;
- o teste final permanecerá bloqueado, e a v1 não será reaberta para buscar aprovação;
- os resultados não serão generalizados para outros modelos ou ativos;
- dados, políticas, resultados e evidências serão preservados;
- mudanças futuras serão propostas em uma nova versão, sem reclassificar retrospectivamente a v1 como aprovada.

Resultado: "Não houve evidência suficiente, segundo os critérios do protocolo v1, para habilitar o sinal." Redação oficial completa e afirmações não autorizadas no [encerramento](../preditivo/encerramento_v1.md), seção 1.

Determinações adicionais: registrar o alcance efetivo do bloqueio, distinguindo os acessos ao arquivo completo por finalidade; manter registradas a divergência da reconstrução da VALE3 em 2008–2009 e a justificativa do fator da fonte nas correções de máxima e mínima de 2012; não confundir o ensaio sem a política com o desenvolvimento oficial; manter o snapshot original intacto; registrar `alpha` = 1000 em 7 de 8 dobras de cada ativo, sem ampliar a grade nem reinterpretar a escolha como previsão nula; manter o desvio da árvore alterada (só `docs/versao_congelada.md`) descrito como tal.

Período final: reservado para uma eventual v2, desde que seus resultados preditivos não sejam consultados para escolher a nova configuração, o protocolo da v2 seja fechado antes da avaliação, as mudanças motivadas pela v1 sejam registradas e a v2 não seja apresentada como repetição independente de uma hipótese que não mudou.

Próxima atividade: concluir o arquivamento da v1 e preparar uma proposta delimitada de v2 (hipótese, diferença em relação à v1, critérios e justificativas, custo, plano de avaliação e situação do período reservado), antes de executar novos experimentos.

**Cumprimento (08/11/2026):** encerramento documentado em [`encerramento_v1.md`](../preditivo/encerramento_v1.md); estado do bloqueio em `experiments/preditivo/encerramento_v1.json`; o código passa a recusar nova coleta, lista do período final, desenvolvimento oficial e avaliação final nesta versão (`abertura.exigir_versao_aberta`). Protocolo, nota e configuração não foram alterados depois do desenvolvimento, e os hashes deles continuam iguais aos registrados.

**Evidência:** texto recebido pelo desenvolvedor em 08/11/2026. **Pendente:** arquivar fora do repositório a mensagem original (data e remetente).

Status: recebida em 08/11/2026. Confirmação original: a arquivar.

## V2 — Autorização do piloto preditivo v2 (08/11/2026)

Referência: [`proposta_piloto_v2.md`](../preditivo/proposta_piloto_v2.md). Consolidação: [`protocolo_piloto_v2.md`](../preditivo/protocolo_piloto_v2.md).

Abrangência: implementação, testes e desenvolvimento do piloto v2, sem abertura automática do período final. A ampliação da grade é uma investigação justificada, não uma promessa de melhora, e não busca recuperar a aprovação da v1.

| ID | Decisão |
|---|---|
| V2-1 | Aprovada a grade 0,1 · 1 · 10 · 100 · 1000 · 10⁴ · 10⁵ · 10⁶, sem outras mudanças de modelagem. Hipótese: "Investigar se uma grade mais ampla de regularização permite à Ridge obter ganho preditivo estável em relação ao retorno zero e à média histórica, mantendo os demais elementos do piloto." Sem afirmar que a grade truncou a regularização antes do melhor ponto, nem que a v1 demonstrou excesso de variância. Fatores de encolhimento só como ilustração. Registrar `alpha`, média e desvio das previsões, média do alvo no treino, afastamento em relação à referência histórica e norma dos coeficientes. "Praticamente a média" deve ser verificado nos resultados |
| V2-2 | Aprovado o limite fixo: 10⁶ selecionado é registrado como escolha no limite. Não se acrescentam valores, não se repete a seleção com outra grade e não se escolhe configuração depois de consultar o período final |
| V2-3 | Aprovado o critério 6 obrigatório e cumulativo: `R²_média = 1 − Σ(y − ŷ_Ridge)² / Σ(y − ŷ_média)²` > 0 no período final e em pelo menos 5 de 8 dobras. A média é a histórica expansiva causal da v1 (só alvos realizados em cada data), distinta da média do alvo no treino. Mesmas datas; denominador nulo, valor não finito ou previsão ausente tratados explicitamente, sem virar aprovação. Superar a média é condição operacional de ganho incremental, não demonstração causal. A alternativa de diagnóstico não foi adotada |
| V2-4 | Diebold-Mariano contra a média só como diagnóstico: não substitui o critério 2, não é segunda chance, não pode ser escolhido por ser mais favorável e é sempre reportado |
| V2-5 | Critérios 3 e 6 mantidos como filtros de desenvolvimento, com a declaração obrigatória de não independência no relatório. Período reservado descrito como "ainda não utilizado para avaliação preditiva ou seleção de modelos" |
| V2-6 | Período reservado preservado para a v2. A abertura depende de: protocolo confirmado, hashes, implementação e testes, desenvolvimento oficial, critérios 3 e 6 atendidos, relatório e nova decisão escrita. A lista de datas vem depois dessa decisão e antes de qualquer métrica final. Resultados finais conhecidos não permitem mudar grade, critérios ou estratégia e reutilizá-los como nova confirmação |
| V2-7 | Encerramento sem avaliação final se os critérios 3 ou 6 falharem, com a redação "A v2 não atendeu aos critérios de desenvolvimento necessários para abertura da avaliação final. Não houve evidência suficiente, segundo o protocolo, para habilitar o sinal." Não há obrigação de abrir o período nem de criar uma v3 |

Separação técnica: configurações, registros e travas próprios da v2, com funções compartilhadas. Ficam preservados os artefatos, hashes e o encerramento da v1, a identificação dos resultados por versão e a impossibilidade de sobrescrever resultados oficiais. A equivalência nos valores comuns das grades é verificada com tolerância documentada (protocolo v2, seção 11). A estimativa de custo é previsão de esforço.

Sequência autorizada: consolidar o protocolo v2 → obter a confirmação real → implementar a separação por versão → testes sintéticos e de desenvolvimento → congelar configuração e código → desenvolvimento oficial → relatório → decisão sobre encerramento ou abertura. Não inclui publicação de previsões, habilitação de sinais no aplicativo nem alteração do prompt histórico v0.6.

**Cumprimento (08/11/2026):** protocolo v2 consolidado; proposta corrigida conforme as observações de redação.

**Confirmação (08/11/2026):** o orientador confirmou as decisões V2-1 a V2-7, conforme a proposta e o protocolo consolidados, com oito condições:
1. a grade até 10⁶ é a única mudança de modelagem;
2. o critério 6 é obrigatório e cumulativo, e não calculável conta como não atendido;
3. a média do alvo no treino e a média histórica expansiva causal ficam identificadas separadamente;
4. Diebold-Mariano contra a média é só diagnóstico;
5. o relatório declara a não independência;
6. a v2 tem configurações, registros, resultados e travas próprios, com a v1 preservada;
7. a reprodução da v1 respeita as tolerâncias de 10⁻¹⁰ relativa e 10⁻¹² absoluta, e divergências são investigadas sem ampliar as tolerâncias;
8. a falha dos critérios 3 ou 6 encerra a v2 sem abertura.

Autorizados: o commit dos documentos, a implementação, os testes de separação e de reprodução, a preparação do congelamento e o desenvolvimento oficial depois dos testes e do congelamento. Não autorizados: a abertura do período final (exige as sete condições e nova decisão escrita), a publicação de previsões, a habilitação de sinais no aplicativo e a alteração das regras da versão histórica.

Conclusão confirmada na íntegra, o que resolve a pendência da mensagem interrompida: "A ampliação da grade é uma investigação justificada, não uma promessa de melhora. O critério adicional contra a média histórica busca verificar se as variáveis acrescentam informação útil, e não apenas se uma previsão mais regularizada supera o retorno zero. O resultado será aceito e documentado independentemente de habilitar ou não o sinal."

**Evidência:** textos recebidos pelo desenvolvedor em 08/11/2026 (decisão e confirmação). **Pendente:** arquivar fora do repositório as mensagens originais (data e remetente).

Status: confirmada em 08/11/2026. Mensagens originais: a arquivar.

## Pendente — Desenvolvimento oficial da v2 (08/11/2026)

Relatório em [`desenvolvimento_oficial_v2.md`](../preditivo/desenvolvimento_oficial_v2.md).

| Ativo | Critério 3 | Critério 6 nas dobras | Situação |
| --- | --- | --- | --- |
| PETR4.SA | 6 de 8 | 5 de 8 | Filtros atendidos. Diagnóstico posterior: uma constante igual à média do treino, sem variáveis, supera a média histórica em 7 de 8 dobras |
| VALE3.SA | 4 de 8 | 3 de 8 | Encerramento sem avaliação final (V2-7) |

Status: decidida (DV2, abaixo).

## DV2 — Encerramento da v2 sem abertura final (08/11/2026)

Data: 08/11/2026, sujeita à confirmação do orientador.

Decisão: encerrar a v2 sem abrir a avaliação final de nenhum ativo (caminho a).

VALE3.SA: critérios 3 (4 de 8) e 6 (3 de 8) de desenvolvimento não atendidos. Encerramento conforme V2-7: "A v2 não atendeu aos critérios de desenvolvimento necessários para abertura da avaliação final da VALE3.SA. Não houve evidência suficiente, segundo o protocolo, para habilitar o sinal." Sem alteração de limiar, grade ou variáveis para reclassificar o resultado.

PETR4.SA: critérios 3 (6 de 8) e 6 (5 de 8) de desenvolvimento formalmente atendidos, e assim registrados, sem reclassificação retrospectiva. A abertura final não foi autorizada porque o diagnóstico exploratório mostrou que o ganho sobre a média histórica expansiva não isolou a contribuição das variáveis: uma constante igual à média do treino também superou essa referência em sete das oito dobras. A comparação mistura o uso dos indicadores na Ridge e a diferença entre a média do treino, mantida durante o ano, e a média histórica, atualizada a cada data. Isso não demonstra que as variáveis sejam inúteis. A PETR4 é encerrada por decisão de não progressão, não por descumprimento dos filtros.

Natureza: a decisão não cria um critério 7 nem altera os critérios 1 a 6.

| Elemento | Situação |
|---|---|
| Filtros de desenvolvimento da PETR4 | Atendidos |
| Filtros de desenvolvimento da VALE3 | Não atendidos |
| Critérios dependentes do período final | Não avaliados |
| Abertura final da PETR4 | Não autorizada por decisão de orientação |
| Habilitação de sinais | Não autorizada para nenhum ativo |

Diagnóstico posterior: preservado como análise exploratória, não prevista no protocolo, calculada só sobre o desenvolvimento, sem efeito retroativo nos critérios. Não se afirma nada sobre o período final, que não foi avaliado.

Resultado científico: "O piloto v2 investigou a ampliação da regularização da Ridge, mantendo os demais elementos da v1. A VALE3 não atingiu os filtros de desenvolvimento. A PETR4 atingiu os filtros contra retorno zero e média histórica expansiva, mas uma análise exploratória posterior identificou que uma previsão constante igual à média do treino também superava a referência expansiva, sem utilizar indicadores. Portanto, o atendimento desses filtros não isolou a contribuição das variáveis. Por decisão de orientação, a avaliação final não foi aberta e nenhum sinal foi habilitado."

Preservação: o período final permanece sem avaliação preditiva nesta versão. Não autorizados: previsões finais, métricas finais, alteração do código para abertura parcial e reutilização da v2 com referências ou critérios modificados. A incompatibilidade entre o bloqueio global do código e a avaliação por ativo fica registrada como achado de implementação; uma versão futura deve definir quais condições são globais e quais são por ativo.

Arquivamento: commit do relatório, do registro DV2 e das atualizações documentais, após conferência do diff; encerramento técnico preservando protocolo e configuração, hashes e commits, previsões e métricas de desenvolvimento, reprodução da v1, diagnóstico exploratório, evidência da não execução da avaliação final e cópia fora do Git. A correção de `cdf7eef` fica descrita como correção de infraestrutura anterior aos resultados, distinta do congelamento em `378b0b9`.

Continuidade: sem v3 imediata. Uma proposta futura poderá investigar se as variáveis acrescentam informação em comparação com uma referência sem variáveis que tenha a mesma amostra de treino, o mesmo calendário de reestimação, as mesmas datas de previsão e as mesmas restrições de disponibilidade de alvos. É só uma hipótese de pesquisa: nenhum experimento novo está autorizado. Essa comparação não repetiria o critério 6, porque mede outra coisa: o critério 6 compara a Ridge com a média histórica atualizada a cada data, e a vantagem observada mistura a contribuição dos indicadores com a diferença entre a média do treino, constante durante o ano, e a média atualizada. Uma referência sem variáveis nas mesmas condições de treino, calendário, datas e alvos separa esses dois efeitos, ponto que permaneceu em aberto na v2 (esclarecimento conceitual posterior ao encerramento, sem efeito sobre resultados ou critérios).

**Cumprimento (08/11/2026):** relatório corrigido; encerramento técnico em [`encerramento_v2.md`](../preditivo/encerramento_v2.md) e `experiments/preditivo/encerramento_v2.json`; diagnóstico salvo como arquivo exploratório com hash; cópia fora do Git.

**Evidência:** texto recebido pelo desenvolvedor em 08/11/2026. **Pendente:** arquivar fora do repositório a mensagem original (data e remetente).

Status: recebida em 08/11/2026. Confirmação original: a arquivar.

## DL1 — Entrada da camada de linguagem v1.0-experimental (09/11/2026)

Data: 09/11/2026, sujeita à confirmação do orientador. Referência: [`protocolo_llm_v1.0-experimental.md`](../protocolo_llm_v1.0-experimental.md). Alcance: ambiente experimental isolado, com acesso nominal; nada é liberado ao público.

Aprovado:
- **DL1-A, protocolo:** aprovado na forma submetida, com condições vinculantes:
  - a política de liberação continua com zero modelos e zero motores até o fim da avaliação;
  - as 17 verificações são condição de exibição, e uma reprovação resulta em abstenção, nunca em exibição com ressalva (a 17ª, verificação 13a, foi criada em 09/11/2026 pela correção 1; ver a correção de referência abaixo);
  - o registro segue sem texto gerado, contexto ou chave;
  - o protocolo fixa o hash do prompt, o do esquema de saída e o do conjunto de casos;
  - existe um interruptor que leva a camada à abstenção total sem exigir deploy.
- **DL1-B, cinco textos fixos:** redação aprovada, condicionada a cinco correções antes de registrar o hash de aprovação:
  1. toda menção à média histórica vem com a ressalva de amostra limitada e dispersão entre anos;
  2. nenhum "tende", "deve subir" ou equivalente fora do bloco de estimativa autorizada;
  3. sem modelo autorizado, o texto declara a ausência de estimativa, em vez de omitir o tema;
  4. estratégia, indicador e modelo sempre marcados como experimentais;
  5. textos de abstenção e de encerramento idênticos em todas as telas, sem variação por ativo.

  Correção não aplicável volta ao orientador; o desenvolvedor não ajusta por conta própria.
- **DL1-C, R3 (acesso):** nominal, autenticado e reversível:
  - rota própria fora do menu público, com noindex;
  - lista versionada de no máximo cinco contas: aluno, orientador e até três avaliadores;
  - sem acesso anônimo nem link compartilhável, com sessão de expiração curta;
  - registro de conta, data, ativo e caso consultado;
  - flag que desliga com recusa explícita, não só escondendo o elemento;
  - revisão da lista a cada 30 dias e no encerramento;
  - e-mails fora dos logs da aplicação e do repositório público.
- **DL1-D, R10 (chamadas e orçamento):**
  - fase 1, obrigatória: respostas geradas em lote e versionadas, sem chamada durante a navegação;
  - fase 2: só em job offline, depois de fechada a fase 1, com a chave só no servidor do job;
  - provedor Gemini, Tier 1 pago; modelo primário Flash, com versão fixada por hash; GPT-5 mini como secundário opcional;
  - teto de US$ 20 por mês, com alertas em 50% e 80% e bloqueio em 100%;
  - 200 chamadas por rodada; acima disso, nova autorização;
  - auto-reload com gatilho em US$ 5 e limite igual ao teto;
  - temperatura baixa, fixa e registrada;
  - tokens e custo registrados por chamada.
- **DL1-E, avaliação humana cega:**
  - conjunto de casos congelado com hash, o mesmo para o template determinístico, o primário e o secundário;
  - no mínimo dois avaliadores, sem saber qual saída é do template;
  - rubrica de cinco itens: fidelidade aos números, aderência às três camadas, calibração da incerteza, ausência de promessa e utilidade;
  - desacordo resolvido por um terceiro designado e registrado;
  - aceitação: zero violação das 17 verificações; nenhuma promessa, urgência ou persuasão; LLM igual ou superior ao template em pelo menos 70% dos casos, com o desempenho do template publicado junto;
  - empate ou vitória do template é resultado legítimo.

**Portão de ativação.** São seis condições cumulativas:
1. protocolo congelado com hash;
2. cinco textos corrigidos e aprovados com hash;
3. lista de acesso versionada;
4. fase 1 concluída;
5. relatório de avaliação com os critérios atendidos, inclusive zero violação das 17 verificações;
6. hash aprovado registrado.

Se alguma condição falhar, o estado final é abstenção.

**Não aprovado:** exibição pública, recomendação de qualquer tipo, uso do período reservado da linha preditiva, chamadas ao vivo fora do job offline, ampliação do teto de orçamento e alteração de artefatos com hash da v0.6 ou do piloto preditivo.

**Divisão dos três commits (08/11/2026), conferida em 09/11/2026:**

| Commit | Conteúdo |
|---|---|
| `e9cc8ad` | Camada v1.0-experimental: `core/llm_exp_policy.py`, `llm_exp_context.py`, `llm_exp_prompts.py`, `llm_exp_validation.py`, `llm_exp_service.py`; `tests/test_llm_exp.py`; `docs/protocolo_llm_v1.0-experimental.md`; e, em `core/llm_client.py`, o parâmetro opcional `payload` em `call_model` (sem ele, a chamada é idêntica à da v0.6, com teste) |
| `ce1d787` | `docs/pibiti/indice_mensagens_orientador.md` e a nota de encerramento do desvio de `versao_congelada.md` em `docs/preditivo/evidencias/arvore_coleta_snap-20261108-01.md` |
| `90c31a2` | `docs/pibiti/capitulo_linha_preditiva.md` |

**Nenhum arquivo com hash registrado foi tocado.** Os hashes conferem com os registrados:
- protocolo v1 `e7f2d5e4…`;
- protocolo v2 `76756648…`;
- nota `be0747af…`;
- `config.py` `90986a8c…`;
- `config_v2.py` `79a89c80…`;
- política de qualidade `f75598b0…`;
- impressão da v0.6 `e3b3574b7430`.

`llm_client.py` não tem hash registrado: a impressão da v0.6 cobre só o prompt, as instruções e o esquema.

**Análise das correções do DL1-B (09/11/2026):** ver o [protocolo](../protocolo_llm_v1.0-experimental.md), seção 13. As correções 2, 3 e 5 já valem para os cinco textos, sem mudança. A correção 4 se aplica a três textos, com redação proposta. A correção 1 não se aplica a nenhum dos cinco textos e **volta ao orientador**. Nenhum texto foi alterado no código.

**Evidência:** texto recebido pelo desenvolvedor em 09/11/2026. **Pendente:** arquivar fora do repositório a mensagem original (data e remetente).

Status: recebida em 09/11/2026. Confirmação original: a arquivar.

### DL1 — Complemento: correções 1 e 4 e pontos técnicos (09/11/2026)

- **Correção 1:** regra do texto gerado, e também das frases do template que citem média histórica. Quando a frase contiver média, comparação entre períodos ou frequência histórica, o mesmo parágrafo precisa ter a limitação da amostra e a não garantia de repetição. A verificação é por classe de expressão, com pelo menos duas variantes para cada elemento. Em caso de falha, uma regeneração e, depois, abstenção. O template aplica a regra por composição fixa.
- **Correção 4:**
  - textos fixos com marca na própria frase;
  - **código do motor não alterado**: marca no rótulo do bloco ("Conclusão experimental") e texto intacto; quando houver motor autorizado, a marca na emissão vira condição da autorização;
  - texto da LLM com marca no nível do bloco: o validador exige o cabeçalho e verifica que nenhuma frase atribua aprovação, recomendação ou garantia ao indicador, à estratégia ou ao modelo.
  "Indicador" não é correção pendente nos cinco textos.
- **Pontos técnicos** (registrados como pendências de implementação no protocolo, seção 13.2):
  - cliente Gemini separado, só no job offline, sem tocar o `llm_client` da v0.6;
  - temperatura do GPT-5 mini como restrição do provedor (seed ou duas execuções por caso);
  - contador próprio do job como autoridade de orçamento, com reserva antes da chamada e contagem das falhas;
  - teto de US$ 16 na rodada de avaliação, mantido o de US$ 20 por mês;
  - app privado separado com convite nominal, sem afirmar noindex;
  - lista com identificadores derivados e rótulo de papel, com o mapeamento para e-mails fora do Git e uma cópia com o orientador.
- **Autorização:** aplicar as correções aos textos e fazer o commit da DL1 com a seção 13 atualizada. Os hashes dos cinco textos só são atualizados depois das correções, em commit separado. Próxima entrega: fase 1 (conjunto de casos congelado, template e respostas salvas); a avaliação humana só começa com os três sob hash.

**Evidência:** texto recebido pelo desenvolvedor em 09/11/2026. **Pendente:** arquivar a mensagem original.

### DL1-H — Aprovação do commit das correções e ratificação dos hashes (09/11/2026)

Data: 09/11/2026, sujeita à confirmação do orientador. Identificador: **DL1-H**. Referências: registro da DL1 no commit `177908d` (só documentação, sem emenda) e correções no commit `c106f6d` (separado), cujo resumo confirma que nenhum arquivo com hash da v0.6 (`e3b3574b7430`) nem do piloto preditivo foi tocado. A seção 13.3 do protocolo traz o hash de cada um dos cinco textos.

| Item | Hash | Situação |
|---|---|---|
| Prompt | `b5ef179c9376` | Aprovado |
| Esquema de saída | `9a4cb5cb5a0c` | Aprovado |
| Impressão combinada | `6f50a1cadd7c` | Aprovado |
| Conjunto dos cinco textos | `95845577dba9` | Aprovado |

A aprovação vale só para esses valores exatos. Qualquer alteração em prompt, esquema, texto fixo ou conjunto de textos anula a aprovação automaticamente e exige nova ratificação, sem reaproveitar o mesmo `APPROVED_FINGERPRINT`.

- **Implementação:** `APPROVED_HASHES` e `APPROVED_FINGERPRINT` em `core/llm_exp_service.py`, preenchidos depois que `c106f6d` entrou no repositório. O serviço confere os quatro hashes a cada execução; se qualquer um divergir, bloqueia com `protocolo_nao_aprovado`. Há teste para a mudança de cada componente.
- **Alcance:** a aprovação dos hashes é uma das seis condições do portão de ativação. As outras continuam pendentes, e nenhuma tela usa a camada.
- **Bloqueio por hash divergente**, confirmado com teste antes do commit, como pedido:
  - o resultado é abstenção, sem dados; se o conjunto de textos divergir, o texto exibido é o fallback da v0.6, nunca o texto anterior;
  - não há degradação graciosa: sem chamada, sem regeneração, sem troca de provedor e sem respostas salvas.

**Verificação 13a ratificada.** Ela restringe, não relaxa.

**Correção de referência (não é nova decisão):** de 16 para 17 verificações, em três lugares do registro DL1:
- a DL1-A exige 17, com a nota de que a 17ª foi criada em 09/11/2026 pela correção 1;
- o critério de aceitação da avaliação humana passa a "zero violação das 17 verificações";
- o portão de ativação passa a mencionar as 17.

O mérito da decisão não muda.

**Nota sobre o caso de teste:** A verificação 13a não foi afrouxada. Durante a implementação, um caso de teste que esperava reprovação passou, e **o que se corrigiu foi o caso de teste, não o validador**. O caso tirava a ressalva de amostra limitada do texto da observação, mas o bloco ainda trazia essa ressalva em `limite_da_evidencia` ("A amostra é limitada [...]"), e o bloco inteiro conta como um parágrafo. O validador acertou ao aprovar. O caso passou a trocar também `limite_da_evidencia` por um texto sem ressalva e, assim, reprova como deve.

**Pontos de atenção registrados no protocolo, seção 7.1:**
- negação, com desempate a favor da reprovação, lista de padrões aceitos e um teste por padrão;
- médias móveis fora só da 13a, sujeitas às checagens de futuro e de atribuição;
- regeneração registrada por chamada (primeira ou regeneração), com tokens e custo.

**Próxima entrega:** fase 1 completa: conjunto congelado, template com ressalva estrutural, respostas salvas com hash e o primeiro relatório de avaliação cega. A regra do template está escrita na especificação da fase 1 ([`llm_v1_exp_fase1.md`](../llm_v1_exp_fase1.md)).

**Evidência:** texto recebido pelo desenvolvedor em 09/11/2026. **Pendente:** arquivar a mensagem original.
