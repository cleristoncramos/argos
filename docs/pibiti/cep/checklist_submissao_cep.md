# Submissão ao CEP — checklist, prazos e perguntas (Bloco 9)

**Status em 10/10/2026:** documentos-base redigidos (minutas); falta confirmar o procedimento com o orientador e com a secretaria do CEP/UFPI. Itens `[?]` dependem dessa confirmação; não os preenchi por suposição.

## 1. Perguntas para o orientador e para a secretaria do CEP/UFPI (tarefa 9.1)

**Ao orientador**
1. O senhor pode figurar como **pesquisador responsável** e o aluno como pesquisador participante?
2. Aprova o delineamento (dois grupos, 20 participantes, sessão presencial de ~60 min, modo demo)?
3. Aprova os instrumentos (questionário de 10 questões, SUS, clareza, pergunta aberta)? Há itens a trocar?
4. Aprova incluir os avaliadores especialistas da 7A neste mesmo protocolo?
5. Há convidados que o senhor não deve recrutar (seus alunos diretos)?

**À secretaria do CEP/UFPI**
1. A pesquisa deve ser submetida pela **Plataforma Brasil**? Quais documentos o CEP exige para projetos de bolsistas PIBITI?
2. Qual a **frequência das reuniões**, o prazo médio de apreciação e o calendário de recesso?
3. Como proceder com o **registro do consentimento** (via impressa assinada é aceita)?
4. A pesquisa pode ser dispensada de apreciação por alguma regra (por exemplo, pesquisa de opinião sem identificação)? Se sim, **exigir declaração por escrito**; a decisão do grupo (N14b) é pedir o parecer.
5. Qual o prazo mínimo de guarda dos dados exigido?
6. Há modelo de TCLE ou de folha de rosto da UFPI?
7. É permitido o **pré-teste** dos instrumentos, e deve ser descrito no protocolo?

## 2. Documentos (conferir contra a lista oficial do CEP) `[S]`

| Documento | Arquivo / responsável | Situação |
| --- | --- | --- |
| Folha de rosto (Plataforma Brasil) | Gerada no sistema; assinada pelo responsável e pela instituição | Pendente |
| Projeto detalhado / protocolo | `protocolo_pesquisa.md` | Minuta |
| TCLE dos participantes | `tcle_participantes.md` | Minuta |
| TCLE dos avaliadores | `tcle_avaliadores.md` | Minuta |
| Instrumentos | `instrumentos.md` | Minuta |
| Roteiro de aplicação | `roteiro_aplicacao.md` | Minuta |
| Cronograma e orçamento | Seções 12 e 13 do protocolo | Minuta |
| Currículos Lattes dos pesquisadores | Pesquisadores | Pendente |
| Declaração de ciência da instituição / anuência | Secretaria / chefia `[?]` | Pendente |
| Declaração de não início da coleta | CEP / pesquisadores `[?]` | Pendente |
| Arquivos finais em **PDF** (e .docx para edição) | Converter após aprovação do orientador | Pendente |

## 3. Datas-alvo `[D]`

| Meta | Data |
| --- | --- |
| Contato com orientador e CEP (9.1) | até **17/10/2026** |
| Minuta revisada pelo orientador | até **14/11/2026** |
| Documentos finais completos | até **05/12/2026** |
| **Submissão na Plataforma Brasil** | até **15/12/2026** |
| Parecer esperado | jan–fev/2027 `[S]` |
| Pré-teste e coleta | só após o parecer favorável |

## 4. Itens técnicos para a coleta

| ID | Item | Estado |
| --- | --- | --- |
| T1 | **Interruptor da condição "sem camada educativa"** (oculta explicações, roteiro "Como ler este gráfico", glossário e documentação dos indicadores; mantém os avisos obrigatórios e o texto da simulação). Proposta: variável `ARGOS_EDU_LAYER=off`, lida em `app/ui/` | **A implementar antes do congelamento**; preciso dos arquivos `app/ui/education.py`, `indicator_docs.py` e do `sidebar` atuais |
| T2 | Teste automatizado: com a camada desligada, nenhum texto educativo aparece e os avisos obrigatórios permanecem | A implementar com T1 |
| T3 | Gabarito de eventuais itens de leitura da tela, calculado sobre a versão congelada | Opcional |
| T4 | Lista de aleatorização (blocos de 4) com semente registrada | Antes da coleta |
| T5 | Planilha de respostas (colunas: código, condição, Q1–Q10, neutralidade, SUS1–10, clareza1–5, tempos, comentário) | Antes da coleta |

## 5. Regras de ouro

1. **Nenhuma coleta, nem de pré-teste, antes do parecer favorável.**
2. O TCLE não substitui a apreciação ética.
3. Registrar o parecer (número, data) em `docs/pibiti/decisoes_orientador.md` e na ficha de `versao_congelada.md`.
4. Qualquer mudança no protocolo depois da aprovação exige **emenda** ao CEP.