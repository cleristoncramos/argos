# Plano de implantação: orientações da reunião de 10/11/2026

**Origem:**
- transcrição automática da reunião de 10/11/2026 com o Prof. Arlino (arquivo `Argos - 10-11-2026.docx`, fora do repositório);
- mensagens do orientador por WhatsApp em 11/11 e 13/11/2026, anexadas ao mesmo arquivo.

**Situação:** plano **aprovado** pelo orientador na DL2 (13/11/2026), com os seis conflitos resolvidos (seção 5) · etapas 1 e 2 concluídas (seção 6) · etapa 3 concluída (seção 7) · **eventos históricos** antecipados da etapa 5 (seção 8), aguardando commit

> **Sobre a transcrição.** O reconhecimento automático trocou vários termos: "Grock" e "Glock" são o **Grok**; "LNM" e "LLMM" são **LLM**; "Lorana" é a **Lorena**. Num trecho, o orientador diz que a ferramenta "é determinística", mas o contexto deixa claro que ele quis dizer **não determinística**. As orientações abaixo seguem o sentido evidente da conversa; onde houve dúvida, o item está marcado "a confirmar".

---

## 1. Inventário das orientações

Na coluna "Hoje no Argos", ✔ indica que já existe, ◐ que existe em parte e ✘ que não existe.

### A. Interface e usabilidade

| # | Orientação | Origem | Hoje no Argos | O que fazer |
| --- | --- | --- | --- | --- |
| A1 | Ao escolher um ativo no menu lateral, carregar logo o período disponível, para o usuário não conseguir escolher um intervalo errado | WhatsApp 11/11 | ✘ As datas são livres; o recorte só é ajustado depois de carregar | Consultar a disponibilidade do ativo ao selecioná-lo e limitar as datas (mínima e máxima) ao período existente |
| A2 | Quando o histórico disponível for menor que o pedido, mostrar um alerta visual: "um vermelhinho", "um iconezinho" | Reunião | ◐ O aviso existe só em texto ("Histórico menor que o solicitado…") | Pôr ícone de atenção e destaque de cor no aviso e no campo "Período disponível" |
| A3 | Na variação por prazo, trocar "No ano" por "Neste ano", que deixa mais claro | Reunião | ◐ O rótulo é "No ano" | Trocar o rótulo e conferir o texto de ajuda |
| A4 | Rodapé com explicações para quem não é da área: variação acumulada, taxa equivalente ao ano etc. | Reunião | ◐ Há explicações em outros pontos; a tabela de variação por prazo não tem glossário | Pôr um rodapé curto de termos sob a tabela, no padrão "Como ler" |
| A5 | Reescrever o texto da página inicial: a ferramenta acessa **milhares** de ativos (o catálogo de 148 é uma seleção) e é melhor dizer "análise de ativos financeiros" em vez de "histórico" | WhatsApp 11/11 | ✘ O texto diz "Consulte o histórico de 148 ativos do catálogo…" | Reescrever o parágrafo, mantendo os números corretos e sem prometer além do que existe |
| A6 | Vídeo da página inicial: o usuário deve poder pausar, avançar e voltar | Reunião | ◐ `st.video` com reprodução automática, sem som e em repetição | **A confirmar** se os controles nativos aparecem para o orientador; se não aparecem, expor os controles e manter a reprodução automática |
| A7 | Mosaico de logos: só os principais, para não poluir; talvez com alguma função ao clicar | Reunião | ◐ O mosaico existe e não é clicável | Manter só os principais; avaliar o clique levando à análise do ativo (opcional) |
| A8 | Num cantinho de "Sobre", contar por que o nome é **Argos** | Reunião | ✘ | Acrescentar um parágrafo curto sobre a origem do nome e a relação com a análise de ativos |
| A9 | No gráfico de evolução temporal, marcar as datas importantes (circuit breaker, covid) | Reunião | ✘ | Marcar eventos de uma **lista curada e com fonte**, nunca gerada pelo modelo (ver D5) |

### B. Página de configurações (nova)

| # | Orientação | Origem | Hoje no Argos | O que fazer |
| --- | --- | --- | --- | --- |
| B1 | O ativo de referência da comparação pode ser escolhido pelo usuário; o padrão continua o atual | WhatsApp 13/11 ("mais um item pra aba configurações") | ◐ As referências são fixas (Ibovespa, S&P 500, Bitcoin e ouro), com escolha automática pela classe | Configuração da referência padrão (qualquer ativo do catálogo ou ticker), mantendo a escolha automática atual como padrão |
| B2 | Catálogo configurável: listar grupos e ativos, acrescentar um ativo a um grupo e criar grupo novo. Sugestão de SQLite (grupos 1 para N tickers) ou arquivo; "faz com calma" | Reunião | ◐ Ticker fora do catálogo já é carregado, mas o catálogo é fixo no código | Catálogo com camada editável (SQLite) por cima do catálogo base, que não muda; página de configurações para gerenciar |

### C. Resultados de destaque e educação financeira

| # | Orientação | Origem | Hoje no Argos | O que fazer |
| --- | --- | --- | --- | --- |
| C1 | Os gráficos de sazonalidade (setembro × outubro e comparação de anos) são "ótimos resultados para vender": mostrar juntos, com zoom, e pôr embaixo de cada um uma dica de como ler | Reunião | ◐ Os gráficos existem; o de comparação de anos não ficou claro ("Não entendi") | Dica de leitura sob cada gráfico, revisão do gráfico de comparação de anos e uma vista que mostre os dois juntos |
| C2 | Deixar claro que os resultados **não são determinísticos**. Exemplo: o padrão setembro → outubro falhou nos dois últimos anos. A ferramenta é **de apoio à decisão, não de investimento** | Reunião | ◐ Há avisos educativos gerais | Aviso específico nos resultados de sazonalidade, com o exemplo dos anos que fugiram do padrão, e reforço no "Sobre" e no texto acadêmico |
| C3 | Vender a ferramenta como **educação financeira**: quadros, explicações de termos e a LLM | Reunião | ✔ Base existente ("Como ler", guias) | Usar como eixo da apresentação e do texto (ver E1) |

### D. Explicação por LLM

| # | Orientação | Origem | Hoje no Argos | O que fazer |
| --- | --- | --- | --- | --- |
| D1 | O botão de explicação deve explicar **o gráfico**, e não só os conceitos | Reunião | ◐ A camada v1.0-experimental tem explicação local por gráfico, mas ainda não está ligada | Seguir a camada v1.0 (explicação por gráfico e síntese por ativo) |
| D2 | Testar os prompts primeiro no chat ("pega essas imagens e vai colocando no chat"), depois integrar | Reunião | — | Usar como etapa exploratória. **Conflito:** o protocolo diz que a LLM recebe só o contexto JSON, nunca imagens (ver seção 3) |
| D3 | Provedor: começar pelo **Grok** (custo baixo ou gratuito), fazer a primeira versão nele e, se der tempo, passar a outros (Gemini, GPT, Claude) | Reunião | ✘ A DL1-D definiu Gemini Tier 1 como primário e GPT-5 mini como secundário | **Conflito com a DL1-D** (seção 3). Criar uma camada de provedores, para trocar sem mudar o protocolo |
| D4 | O usuário escolhe o provedor (configuração básica), com um **prompt o mais universal possível**: começar com um e chegar a três ou quatro se der tempo | Reunião | ✘ | Interface comum de provedor, prompt único e validação comum. A escolha fica na página de configurações, só no ambiente experimental |
| D5 | Nas maiores altas e quedas, a LLM poderia explicar por que aconteceram (covid, circuit breaker) | Reunião | ✘ | **Conflito** com a regra "não inventar causas, notícias ou eventos" do protocolo v1.0. Caminho seguro: lista curada de eventos com fonte, enviada no contexto, que a LLM só pode citar |
| D6 | O cronograma da LLM não tem prazo rígido ("à vontade") | Reunião | — | Registrar; seguir a fase 1 sem pressa artificial |

### E. Escrita acadêmica e acompanhamento da bolsa

| # | Orientação | Origem | O que fazer |
| --- | --- | --- | --- |
| E1 | Na apresentação e no texto, não explicar todos os resultados: escolher **um exemplo** significativo (por exemplo, Bitcoin), explicá-lo bem e citar o resto rapidamente, de forma didática. Resumir as funcionalidades em cerca de dois parágrafos e dizer que cada gráfico ou tabela terá explicação por LLM | Reunião | Roteiro do texto e da demonstração com um exemplo-âncora |
| E2 | A Lorena fica com a escrita do texto do trabalho, para a submissão "entre os melhores" (que vai para banca), separado do relatório final, e com o nome dela no texto | Reunião | Combinar com a Lorena o roteiro, o exemplo-âncora e a limitação de não determinismo (C2) |
| E3 | Ler os artigos indicados. A revisão do Giovanni tem citações para cada indicador técnico. Cobrar do professor os dois artigos que ele ainda vai enviar | Reunião | Separar as citações por indicador para o texto |
| E4 | Relatório parcial: acompanhar a data de abertura no SIGAA, porque perder o prazo pode custar a bolsa | Reunião | Lembrete no checklist e conferência periódica no SIGAA e no e-mail |

### F. Identidade visual

| # | Orientação | Origem | O que fazer |
| --- | --- | --- | --- |
| F1 | Logo que lembre finanças ($, dinheiro, investimento), simples ("menos é mais"). Sem pressa e não é obrigatório ("perfumaria"), mas o visual conta na trilha de submissão | WhatsApp 11/11 | Criar três ou quatro opções e decidir com o orientador |

**Para a próxima reunião:** o orientador avisou em 13/11 que há "outras coisas que podem mudar também". Levar a lista deste plano para confirmação.

---

## 2. Plano de implantação por etapas

Ordem pensada por valor visível, risco e dependências. Cada item recebe testes e entra num commit próprio, com aprovação.

| Etapa | Itens | Esforço estimado | Critério de aceite |
| --- | --- | --- | --- |
| **1. Ajustes rápidos de interface** | A2, A3, A4, A5, A6, A8 | 1 a 2 dias | Aviso com ícone e cor; "Neste ano"; rodapé de termos; novo texto da página inicial; vídeo com controles; origem do nome em "Sobre". Testes de texto e de interface atualizados |
| **2. Período por ativo no menu** | A1 | 1 a 2 dias | Ao trocar de ativo, as datas ficam limitadas ao disponível; teste com ativo de histórico curto (por exemplo, Avalanche); desempenho aceitável (a disponibilidade é consultada com cache) |
| **3. Não determinismo e resultados de destaque** | C2, C1 | 2 a 3 dias | Aviso específico nos resultados de sazonalidade, com os anos que fugiram do padrão; dica de leitura sob cada gráfico; gráfico de comparação de anos revisto e testado com um leitor leigo |
| **4. Página de configurações** | B1, depois B2 | 3 a 5 dias | B1: referência configurável, com o padrão atual preservado. B2: catálogo base fixo e camada editável em SQLite (grupos e tickers), com validação do ticker antes de salvar e sem alterar os dados do modo de demonstração |
| **5. Eventos históricos curados** | A9 (e base para D5) | 2 a 3 dias | Lista versionada de eventos (data, nome, fonte), marcada no gráfico de evolução temporal; nenhum evento sem fonte |
| **6. LLM: provedores e explicação por gráfico** | D1–D5 | Etapas da fase 1 da v1.0 | Ver a seção 4. Cliente Grok primeiro, depois a camada de provedores; tudo passa pelo validador de 17 verificações |
| **Paralelo** | E1–E4, F1, A7 | Contínuo | Roteiro do texto com a Lorena; lembretes do relatório parcial; opções de logo; mosaico revisado |

---

## 3. Pontos que precisam de decisão do orientador

As orientações da reunião foram dadas oralmente e algumas conflitam com decisões já registradas.

| # | Ponto | Decisão registrada | Orientação da reunião | Proposta |
| --- | --- | --- | --- | --- |
| P1 | **Provedor da LLM** | DL1-D: Gemini Tier 1 (Flash) primário, GPT-5 mini secundário, teto de US$ 20 por mês | Começar pelo Grok, pelo custo; outros depois | Registrar uma revisão da DL1-D com o Grok como primário. O conjunto de casos e o template congelados **não dependem do provedor** e continuam válidos. Conferir os termos do plano gratuito do Grok (uso dos dados, limites, versão fixável do modelo) antes de usá-lo |
| P2 | **Imagens dos gráficos** | O protocolo v1.0 diz que a LLM recebe só o contexto JSON calculado pelo Argos | Testar os prompts no chat com as imagens dos gráficos | Imagens só na exploração do prompt, fora do sistema. No sistema, continua só o JSON, que é o que garante que o modelo não "lê" números do gráfico |
| P3 | **Causas das maiores altas e quedas** | O protocolo proíbe o modelo de inventar causas ou eventos | A LLM poderia explicar (covid, circuit breaker) | Lista curada de eventos com fonte (etapa 5), enviada no contexto; o modelo só cita o que estiver nela. Isso muda contexto e prompt, então exige nova versão e nova ratificação |
| P4 | **Escolha do provedor pelo usuário** | DL1-C: só ambiente experimental, com acesso nominal; nada público | O usuário escolhe a LLM nas configurações | Escolha só no ambiente experimental; a versão pública continua sem chamadas ao modelo. Avaliar com cuidado a chave fornecida pelo próprio usuário (segredo) |
| P5 | **Persistência do catálogo editável** | — | SQLite, por instalação | No Streamlit Community Cloud o disco não persiste entre reinícios. Proposta: alterações persistem em instalação local; na versão publicada, valem só durante a sessão, ou ficam desligadas |
| P6 | **Novas funcionalidades neste ciclo** | Parecer de 25/10/2026: sem novas funcionalidades neste ciclo, com congelamento da versão histórica | Várias funcionalidades novas (configurações, catálogo editável, eventos) | Confirmar que a reunião de 10/11 atualiza o parecer de 25/10, e qual versão será congelada para a submissão |

---

## 4. LLM: sequência compatível com a fase 1 já aprovada

1. Registrar a revisão da DL1-D (P1) e a decisão sobre imagens (P2).
2. Criar o cliente Grok no job offline, com versão do modelo fixada, contador de orçamento e registro de tokens e custo, e sem tocar o `llm_client` da v0.6.
3. Explorar o prompt com imagens no chat (P2), anotando o que melhora. Mudanças no prompt geram hash novo e passam por ratificação.
4. Fazer o aquecimento em 3 casos e gerar as respostas salvas sobre o conjunto congelado (`18e5eeee…`).
5. Fazer a avaliação cega com template, Grok e, se houver tempo, um segundo provedor, e emitir o relatório completo.
6. Criar a camada de provedores, para a escolha nas configurações (D4, P4), com o mesmo prompt e o mesmo validador.
7. Fazer a explicação de altas e quedas com a lista curada de eventos (D5, P3), como versão nova do protocolo.

A versão pública não muda até o portão de ativação e a decisão regulatória.

---

## 5. Decisões do orientador (DL2, 13/11/2026)

O registro completo está em [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md), entrada DL2.

| Ponto | Decisão |
| --- | --- |
| Plano | As 27 orientações aprovadas, nas seis etapas, na ordem proposta; escrita, bolsa e logo em paralelo |
| Etapa 1 | Início imediato, **incluindo o limite de datas por ativo** (A1), que a DL2-B pôs nesta etapa |
| P1, provedor | **Grok primeiro**, por custo; Gemini como alternativa registrada. A troca é de configuração. Valem as mesmas regras: política antes da chamada, contexto só em JSON, saída validada, auditoria, orçamento (US$ 16 na rodada) e nenhuma chamada do navegador. Temperatura ou saída estrita indisponíveis ficam registradas como restrição do provedor |
| P2, imagens | Só para explorar no chat; o sistema recebe apenas o JSON |
| P3, causas | Lista curada de eventos, com data e fonte, enviada no contexto. Sem evento curado, o texto diz que não há explicação curada disponível |
| P4, escolha de provedor | Só no ambiente experimental, com acesso nominal; na versão pública, o provedor é fixo |
| P5, catálogo editável | Só na instalação local; na versão pública, fixo e somente leitura |
| P6, parecer de 25/10 | Atualizado pela reunião de 10/11. As funcionalidades são de interface e informação, não de sinal preditivo |
| Aviso de não determinismo | Obrigatório: "Os resultados podem variar entre execuções. O padrão histórico não garante repetição." A ferramenta é de apoio à decisão, não de investimento |
| Escrita e bolsa | A Lorena escreve o texto da submissão; o SIGAA tem prioridade de calendário |

**Fora do aprovado:**
- recomendação;
- mudança no protocolo da LLM sem ratificação;
- período reservado;
- chamadas ao vivo a partir do navegador.

**Observações registradas na DL2:**
- a ordem do item A1;
- a precisão da frase "podem variar entre execuções";
- a página inicial sem número de ativos não comprovado.

---

## 6. Execução da etapa 1 (13/11/2026)

| Item | O que foi feito | Verificação |
| --- | --- | --- |
| A1, datas limitadas ao período do ativo | Novo `core/asset_range.py`. No modo de demonstração, as datas vêm do manifesto; fora dele, uma busca mensal e duas diárias, pequenas, acham o primeiro e o último pregão, com cache de 1 hora. No menu: legenda "📅 Dados disponíveis de … a …" assim que o ativo é escolhido; em "Personalizado", as datas ficam limitadas ao período disponível; num período predefinido que começa antes do primeiro dado, o início é ajustado e um aviso explica o ajuste. Se a consulta falhar, o menu segue sem limite | Testes em `tests/test_asset_range.py`. Na tela, com AVAX-USD e 10 anos, aparecem "Dados disponíveis de 13/07/2020 a 13/11/2026" e o aviso de ajuste. Defeito achado e corrigido na verificação: o fim saía como 01/11/2026, o rótulo da barra mensal, e passou a usar o último pregão |
| A2, aviso visual de histórico menor | "Período disponível" em vermelho, com ⚠️ e "menor que o solicitado", quando o histórico é menor que o pedido; ícone de atenção nos avisos | Testes em `tests/test_data_info_periodo.py`. Na prática, o aviso aparece menos, porque o menu já ajusta o período (A1); continua valendo para consulta sem período conhecido |
| A3, "Neste ano" | Rótulo trocado em `core/trailing_returns.py`, nos testes e na metodologia | Conferido na tabela de variação por prazo |
| A4, rodapé de termos | Bloco "📘 Termos desta tabela", com variação acumulada, taxa equivalente ao ano, "Neste ano", início ajustado e valor no início e no fim, em linguagem simples | Conferido na tela. Defeito achado e corrigido: o "R$" do exemplo virava fórmula; o cifrão foi escapado, com teste |
| A5, página inicial | "Analise ativos financeiros com dados do Yahoo Finance: escolha um dos 148 ativos do catálogo, … ou digite o código de outro ativo disponível na fonte." Não cita "milhares", porque não há contagem comprovável (observação 3 da DL2). O subtítulo "Plataforma de Análise Histórica" foi mantido porque deixa claro que não há previsão. **Atualizado em 13/11/2026**, por mensagem do orientador (complemento da DL2): o texto passa a dizer "Analise **milhares de ativos financeiros** com dados do Yahoo Finance. Comece pelos 148 ativos do catálogo…", e o número do quadro passa a ser "ativos no catálogo" | Conferido na tela |
| A6, controles do vídeo | **Sem mudança necessária**: o vídeo já tem os controles nativos (`controls = true`), com pausa, avanço e retrocesso ao passar o mouse | Conferido no navegador |
| A8, origem do nome | Seção "Por que Argos" no "Sobre": Argos Panoptes, o vigia de cem olhos, e a relação com a proposta da plataforma | Teste em `tests/test_about.py` e conferência na tela |

**Testes:** 1.137, com 100% de cobertura do `core/`.

**Observação para a etapa 4:** o menu lateral das páginas de análise já tem um cabeçalho "CONFIGURAÇÕES" (escolha de ativo, período e frequência). A página "Configurações" nova (referência e catálogo) precisa de outro nome, ou o cabeçalho atual passa a "Consulta", para não confundir.

**Decisão do desenvolvedor (13/11/2026):** o cabeçalho do menu lateral passa a se chamar **"Parâmetros"** em todas as páginas, no lugar de "Configurações" (Análise Individual), "Parâmetros da Comparação", "Parâmetros da Análise" (Indicadores Técnicos), "Parâmetros de Risco e Retorno", "Parâmetros da Simulação" e "Parâmetros do Panorama". O nome "Configurações" fica livre para a página nova da etapa 4.

---

## 7. Execução da etapa 3 (13/11/2026)

| Item | O que foi feito | Verificação |
| --- | --- | --- |
| DL2-G, aviso obrigatório | Texto fixo `NON_DETERMINISM_WARNING` em `core/disclaimers.py`, com a redação aprovada: "Os resultados podem variar entre execuções. O padrão histórico não garante repetição." Aparece sempre, fora da camada educativa: no início da sazonalidade da Análise Individual, junto com a frase "ferramenta de apoio à decisão e de educação financeira, não de investimento", e na sazonalidade da Comparação de Ativos | Teste da redação exata. Conferido na tela com PETR4.SA |
| C2, anos fora do padrão | `pattern_breaks` (em `core/seasonality.py`) acha o sentido da maioria na variação entre dois meses e os anos que não o seguiram, com destaque para os dois anos mais recentes. Embaixo do gráfico, um aviso diz, por exemplo: "Do fechamento de setembro ao fechamento de outubro, o preço subiu em 3 de 5 anos, mas não seguiu esse sentido em 2024 e 2025. Nos 2 anos mais recentes (2025 e 2026), fugiu do padrão em 2025.", seguido do aviso da DL2-G | Testes com o exemplo da reunião (padrão que falhou nos dois últimos anos), com padrão de queda, sem exceção, com empate e com poucos anos. Texto ajustado na verificação para dizer quais são os anos mais recentes |
| C1, dica sob cada gráfico | Frase "💡 Como ler:" sempre visível embaixo dos quatro gráficos de sazonalidade (mapa de calor, média por mês, anos comparados à média e variação entre dois meses), além do roteiro "Como ler este gráfico", que continua no expansor. As dicas seguem a camada educativa | Teste das dicas (tamanho e vocabulário proibido). Conferido na tela |
| C1, gráfico de comparação de anos revisto | O orientador não entendeu as barras pareadas. A forma padrão agora é uma única barra por mês, com a diferença para a média em p.p.: verde acima e vermelho abaixo da linha do zero, que é a média de todos os anos. As barras pareadas continuam disponíveis em "Valores lado a lado", com dica própria | Conferido na tela nos dois modos. Defeito achado e corrigido: o rótulo da média cobria a barra de março e foi movido para fora da área das barras |
| C1, vista conjunta e zoom | "Anos comparados à média" e "Variação entre dois meses" deixaram de ser abas e aparecem um embaixo do outro, com setembro → outubro como padrão. Uma legenda explica o zoom: tela cheia ou seleção de área | Conferido na tela |

**Testes:** 1.142, com 100% de cobertura do `core/`.

**Pendente:** testar o gráfico revisto com um leitor leigo (previsto no plano), de preferência com a Lorena, que não participou da revisão.

**Observação sobre a suíte:** com `-W error`, 7 testes de `tests/test_llm_experiment.py` falham por arquivos não fechados em `experiments/llm_7a`. A falha já existia antes desta etapa (conferida no commit `ccd9aae`) e fica numa área que não pode ser alterada. Na configuração padrão da suíte, todos os testes passam.

---

## 8. Eventos históricos, antecipado da etapa 5 (13/11/2026)

**Origem:** pedido do desenvolvedor em 13/11/2026, antes da etapa 4: trazer para o Argos o recurso "Período e eventos históricos" do projeto Previsão Financial Risk, idêntico ao de lá. O recurso atende o item A9 da reunião (marcar datas importantes, como circuit breaker e COVID, no gráfico de evolução temporal) e adianta a base da etapa 5.

**Ajuste do desenvolvedor (13/11/2026):** o seletor de trecho do projeto Previsão (1 ano, 2 anos, 5 anos, Tudo, Personalizado) **não existe no Argos**. O período é sempre o escolhido na barra lateral, e os eventos são os que caem nesse período.

**O que o usuário vê** (Análise Individual, acima do gráfico de evolução temporal):

| Parte | Como funciona |
| --- | --- |
| Eventos do sistema | 27 eventos de 2016 a 2026, em `data/eventos_historicos.csv` (cópia do `assets/eventos.csv` do projeto Previsão), aparecem como linhas pontilhadas nos dois gráficos, com título, data e descrição ao passar o mouse. São quatro categorias, que ligam e desligam pela legenda do gráfico e pelo filtro "Eventos históricos nos gráficos": **Mercado e crises** (Joesley Day, greve dos caminhoneiros e os seis circuit breakers de março de 2020, registrados em cinco linhas porque dois foram no mesmo pregão), **Saúde** (primeiro caso de COVID no Brasil, pandemia, vacina da Pfizer, início da vacinação), **Política** (eleições de 2018, 2022 e 2026, impeachment, reforma da Previdência, 8 de janeiro) e **Mundo** (Brexit, eleições nos EUA, invasão da Ucrânia, alta de juros do Fed, quebra do SVB, tarifas de 2025) |
| Eventos do usuário | Botão "Adicionar evento próprio": data, título e descrição. Os eventos ficam na sessão do navegador, na categoria "Seus eventos"; a lista pode ser baixada em CSV (`data;titulo;descricao`, datas dd/mm/aaaa) e carregada de novo numa próxima visita. Há também "Remover meus eventos" |
| Aviso | "As linhas pontilhadas marcam acontecimentos que mexeram com o mercado, para dar contexto ao período analisado. Elas não indicam que o evento causou a variação do ativo." Mantém a regra da DL2-D: evento é contexto, não causa |

**Código:** lógica pura em `core/historical_events.py` (10 testes em `tests/test_historical_events.py`, 100% de cobertura) e painel em `app/ui/events_panel.py`. Duas diferenças em relação ao projeto Previsão, ambas sem efeito para o usuário: a lógica saiu da página para o `core/`, como é regra no Argos; e o filtro de categorias passa a marcar "Seus eventos" antes de ser desenhado, porque, na versão do Streamlit usada no Argos, apagar o estado do filtro deixava a tela e o gráfico desencontrados.

**Verificação na tela** (PETR4.SA, 10 anos, frequência mensal): linhas e legenda nos dois gráficos, com os eventos de 01/12/2016 em diante. Evento próprio adicionado e removido, com o filtro e os gráficos de acordo. Defeito achado e corrigido na verificação: depois de incluir um evento próprio, o filtro de categorias não mostrava "Seus eventos", embora o gráfico mostrasse.

**Pendente para fechar a etapa 5 (DL2-D):** a DL2-D e o plano pedem lista curada **com data e fonte**, "nenhum evento sem fonte". A base trazida do projeto Previsão tem data, categoria, título e descrição, mas não tem fonte. Falta acrescentar uma coluna `fonte` com a referência de cada um dos 27 eventos (órgão oficial ou veículo de imprensa) e mostrá-la ao passar o mouse. As fontes não foram inventadas: precisam ser levantadas e conferidas. Os eventos do usuário ficam fora dessa regra, porque são dele e não do sistema.
