# Protocolo da camada de linguagem — v1.0-experimental

**Situação:** protocolo **aprovado com condições** pela DL1 (09/11/2026, sujeita à confirmação original) · textos fixos **pendentes de correção** (seção 13) · impressão digital ainda não aprovada (atual `4268ef4e27ec`) · política de liberação 1.0 (`477ef9b1d362`) · não ligada a nenhuma tela
**Código:** `core/llm_exp_policy.py` (política), `core/llm_exp_context.py` (contexto), `core/llm_exp_prompts.py` (prompt e esquema), `core/llm_exp_validation.py` (validação), `core/llm_exp_service.py` (fluxo). Testes em `tests/test_llm_exp.py`.
**Origem:** [plano de reformulação](plano_reformulacao_preditiva.md), seções 2.3, 4 e 6 (etapa 4), e instrução de trabalho de 08/11/2026.

> **Família nova, não ajuste da v0.6.** A v0.6 ([`protocolo_prompts_llm.md`](protocolo_prompts_llm.md), impressão `e3b3574b7430`) continua congelada nas telas descritivas e não foi editada. A v1.0-experimental tem contexto, prompt, esquema, validador e serviço próprios. A aprovação da 7A não vale para ela (plano, seção 2.3).

---

## 1. Escopo

| Item | Definição |
| --- | --- |
| Para que serve | Explicar, na camada experimental, três coisas separadas: observação histórica, estimativa de modelo autorizado e conclusão do motor de decisão |
| Onde roda | Só no ambiente **experimental restrito**. No ambiente público, o serviço bloqueia antes de qualquer chamada |
| Unidade de explicação | Explicação **local por gráfico** (`grafico`) ou **síntese integrada por ativo** (`sintese_ativo`). Não há recomendação própria por gráfico |
| Entrada do usuário | Nenhuma entrada livre. Pedidos de recomendação, previsão e garantia existem só nos casos de teste e nas rodadas de avaliação |
| Estado atual da política | **Nenhum modelo preditivo e nenhum motor de decisão autorizados**: v1 encerrada pela D1, v2 encerrada pela DV2. Na prática, toda estimativa é abstenção e toda conclusão é "não disponível" |
| Recomendação ao público | Desligada (`RECOMMENDATION_ENABLED = False`) até o parecer regulatório (plano, seção 1.2) |

## 2. O que se mantém da v0.6 (A.1)

| Garantia | Como fica na v1.0-experimental |
| --- | --- |
| Contexto em JSON | Mantido, com três camadas (seção 5) |
| O modelo não calcula nada | Mantido. Cada camada só pode citar os próprios números (verificação 6) |
| Saída estruturada validada antes da exibição | Mantido. Esquema JSON estrito e 16 verificações; qualquer falha bloqueia |
| Auditoria de chamadas e respostas | Mantida e ampliada (seção 9) |
| Limites de custo e de tokens | Mantidos: 1.400 tokens de saída, 20 chamadas e US$ 0,50 por sessão, timeout de 20 s, até 2 retentativas (os mesmos objetos da 7B) |
| Fallback | Mantido, com texto próprio da camada experimental |
| Isolamento de segredos | Mantido: a chave vem de fora e nunca é gravada; o registro não guarda texto gerado nem contexto |

## 3. Regras substituídas (A.2)

| Regra da v0.6 | Regra da v1.0-experimental | Onde é garantida |
| --- | --- | --- |
| Nunca mencionar futuro | Futuro só no bloco `estimativa`, e só se a política autorizou a estimativa | Verificações 7 e 9 |
| Recusar toda previsão | Explicar a previsão disponível; abster-se com texto fixo se não houver modelo válido | Verificações 7 e 15 |
| Bloquear linguagem decisória | Conclusão só quando emitida pelo motor de decisão, copiada literalmente do texto do Argos | Verificação 8 |
| Apenas passado | Três camadas separadas: observação histórica, estimativa e conclusão experimental | Esquema e verificações 5 e 6 |
| Neutralidade como ausência de orientação | Ausência de persuasão, promessa, urgência, falsa certeza e conflito oculto | Verificações 10, 11 e 12 |

**Quem decide a autorização.** O modelo de linguagem nunca decide se uma estimativa ou conclusão pode aparecer. Isso é decidido pela política de liberação (`core/llm_exp_policy.py`), fora do modelo. Quando a política não autoriza, o contexto nem chega a levar os números da estimativa: leva só o motivo da abstenção.

## 4. Regra de redação por gráfico (A.3)

Cada explicação local leva o limite do que aquela evidência permite concluir. O Argos envia a frase em `required_limits`, e o modelo precisa copiá-la literalmente em `o_que_nao_pode_ser_concluido` (verificação 14).

| `chart_type` | Insight possível | Frase obrigatória (não pode ser concluído isoladamente) |
| --- | --- | --- |
| `preco_medias` | Direção histórica e afastamento das médias | "A direção passada e o afastamento das médias não indicam que a trajetória continuará." |
| `rsi_macd` | Estado dos indicadores e sinais da estratégia | "Um sinal de indicador não garante reversão do preço." |
| `sazonalidade` | Meses historicamente favoráveis, dispersão, consistência | "A média histórica de um mês não indica que o próximo mês repetirá esse resultado." |
| `volatilidade` | Intensidade das oscilações e sensibilidade do cenário | "Volatilidade alta não implica retorno alto." |
| `drawdown` | Profundidade e duração das perdas | "A profundidade de uma queda passada não indica que o preço encontrou o fundo." |
| `aportes` | Resultado histórico sob premissas equivalentes | "O resultado histórico de uma forma de aporte não mostra que ela é sempre superior." |
| `referencia_mercado` | Desempenho relativo observado | "Ter superado a referência no período não indica que isso continuará." |
| `previsao` | Cenário estimado para horizonte definido | "Uma estimativa para um horizonte definido não indica um ponto ótimo conhecido de entrada." |
| Síntese do ativo | Leitura integrada dos gráficos listados | "Nenhuma evidência desta síntese, isolada ou combinada, permite concluir o que acontecerá com o ativo." |

**Padrão para a observação histórica:**

> "No recorte selecionado, outubro apresentou média histórica superior à de setembro. Entretanto, houve anos com resultado negativo e a amostra é limitada. A estratégia que usa essa diferença ainda precisa demonstrar desempenho fora da amostra e após custos."

**Padrão para o futuro, só com modelo validado e autorizado.** É o texto que o motor de decisão emite (`CONCLUSION_TEXTS`, código `sinal_favoravel`). O modelo de linguagem só pode copiá-lo:

> "Para o horizonte selecionado, o modelo produziu sinal favorável segundo a regra experimental {regra}. A estimativa apresenta incerteza e o desempenho observado no teste está resumido abaixo."

## 5. Contrato de entrada: contexto

Montado por `build_experimental_context`, que recusa contexto inválido antes de qualquer chamada:
- escopo, tipo de gráfico, status ou frequência fora da lista;
- datas fora do formato ou invertidas;
- métricas repetidas;
- sinalizador desconhecido;
- métricas junto com dados insuficientes;
- estimativa autorizada sem ponto, sem incerteza, sem desempenho no teste ou sem horizonte válido;
- conclusão com código desconhecido.

| Campo | Conteúdo |
| --- | --- |
| `protocol_family`, `context_version` | `"v1.0-experimental"` e `"1.0-experimental"` |
| `scope`, `charts` | `grafico` (um tipo) ou `sintese_ativo` (lista dos gráficos considerados) |
| `status` | `ok` ou `dados_insuficientes` |
| `asset`, `asset_name` | Um ativo por contexto |
| `filters` | `period_start`, `period_end` (AAAA-MM-DD) e `frequency` |
| `n_observations` | Inteiro não negativo |
| `historical` | `metrics` (mesmo formato da v0.6: `id`, `label`, `value`, `unit`, `decimals`), `limitation_flags`, `notes` |
| `estimate` | Sem autorização: `{disponivel: false, motivo}`. Com autorização: `model_id`, `horizonte {valor, unidade}`, `data_corte`, `ponto_id`, `incerteza_ids` e `metrics` (ponto, incerteza e desempenho no teste) |
| `decision` | Sem autorização: `{disponivel: false, motivo}`. Com autorização: `engine_id`, `regra_id`, `codigo` e `texto_conclusao` (texto do Argos) |
| `release` | `ambiente`, `recomendacao_habilitada` (sempre `false`), `politica_versao`, `politica_impressao` |
| `required_limits` | Frases da seção 4 que o modelo deve copiar |
| `user_request` | `null`, ou `{type: recomendacao | previsao | garantia, text}` só em testes |
| `extra_numbers` | Números extras que a camada histórica pode citar (como na v0.6) |

**Motivos de abstenção:**

| Camada | Motivos |
| --- | --- |
| Estimativa | `ambiente_publico`, `sem_modelo_autorizado`, `modelo_nao_autorizado`, `ativo_fora_da_autorizacao` |
| Conclusão | `ambiente_publico`, `sem_motor_autorizado`, `motor_nao_autorizado`, `conclusao_sem_estimativa_autorizada` |

<details>
<summary>Exemplo real de contexto gerado pelo código (sazonalidade, sem modelo autorizado)</summary>

```json
{
  "protocol_family": "v1.0-experimental",
  "context_version": "1.0-experimental",
  "scope": "grafico",
  "charts": ["sazonalidade"],
  "status": "ok",
  "asset": "PETR4.SA",
  "asset_name": "Petrobras PN",
  "filters": {"period_start": "2021-01-04", "period_end": "2025-12-30", "frequency": "Mensal"},
  "n_observations": 60,
  "historical": {
    "metrics": [
      {"id": "media_outubro", "label": "Média de outubro", "value": 2.15, "unit": "%", "decimals": 2},
      {"id": "anos_positivos_outubro", "label": "Anos positivos em outubro", "value": 60.0, "unit": "%", "decimals": 1}
    ],
    "limitation_flags": ["poucos_anos"],
    "notes": []
  },
  "estimate": {"disponivel": false, "motivo": "sem_modelo_autorizado"},
  "decision": {"disponivel": false, "motivo": "sem_motor_autorizado"},
  "release": {"ambiente": "experimental_restrito", "recomendacao_habilitada": false,
              "politica_versao": "1.0", "politica_impressao": "477ef9b1d362"},
  "required_limits": ["A média histórica de um mês não indica que o próximo mês repetirá esse resultado."],
  "user_request": null,
  "extra_numbers": [5.0]
}
```

Os valores das métricas são ilustrativos, montados só para o exemplo; não vêm de nenhuma análise.
</details>

## 6. Contrato de saída: esquema estrito

O esquema é `OUTPUT_SCHEMA` em `core/llm_exp_prompts.py`, enviado como JSON Schema estrito (`strict: true`, sem campos adicionais).

| Campo | Conteúdo |
| --- | --- |
| `resumo` | Até 3 frases; nas recusas, só a frase fixa |
| `tratamento_do_pedido` | `sem_pedido`, `recusa_recomendacao`, `recusa_garantia`, `previsao_abstencao` ou `previsao_explicada` |
| `filtros_aplicados` | `ativos`, `periodo_inicio`, `periodo_fim`, `frequencia`, iguais aos do contexto |
| `observacao_historica` | `texto`, `metricas_relevantes` (até 6 itens `{id, valor, unidade, leitura}`) e `limite_da_evidencia` |
| `estimativa` | `situacao` (`apresentada` ou `abstencao`), `texto`, `metricas_relevantes` e `incerteza` |
| `conclusao_experimental` | `situacao` (`emitida_pelo_motor` ou `nao_disponivel`) e `texto` |
| `limitacoes` | De 1 a 4 frases |
| `o_que_nao_pode_ser_concluido` | De 1 a 4 frases, com as de `required_limits` |
| `nota_educativa` | Texto fixo |

**Textos fixos:**

| Uso | Texto | Origem |
| --- | --- | --- |
| Recusa de recomendação | Frase de recusa da v0.6 | Orientador, 10/10/2026 |
| Recusa de garantia | "Nenhum resultado de investimento pode ser garantido. O Argos DataLab apresenta dados históricos e, quando houver modelo autorizado, estimativas com incerteza e limitações." | **Proposta, a aprovar** |
| Abstenção da estimativa | "Não há modelo preditivo validado e autorizado para este ativo e horizonte; por isso, nenhuma estimativa é apresentada." | **Proposta, a aprovar** |
| Conclusão indisponível | "Nenhuma conclusão sobre estratégia está disponível: não há motor de decisão autorizado para este ativo." | **Proposta, a aprovar** |
| Nota educativa | "A análise tem finalidade educativa e de pesquisa, separa dados históricos de estimativas e não é recomendação de investimento." | **Proposta, a aprovar** |
| Fallback | "A explicação experimental não está disponível agora. [...] não é recomendação de investimento." | **Proposta, a aprovar** |

## 7. Verificações antes da exibição

Todas precisam passar; uma falha bloqueia a resposta. As comparações ignoram acentos e maiúsculas, e as frases fixas copiadas literalmente são retiradas antes da análise de linguagem.

| # | Verificação | O que exige |
| --- | --- | --- |
| 1 | `json_valido` | A resposta é um objeto JSON |
| 2 | `campos_obrigatorios` | Estrutura exata do esquema, situações dentro das listas, textos não vazios e curtos, até 6 métricas por camada, listas de 1 a 4 itens, nota fixa |
| 3 | `ativo_consistente` | Ativo igual ao do contexto e nenhum outro ativo do catálogo citado |
| 4 | `periodo_frequencia` | Datas e frequência iguais às do contexto |
| 5 | `metricas_por_camada` | Métrica histórica só da camada histórica e métrica da estimativa só da estimativa, com o mesmo valor (tolerância de arredondamento) e unidade. Dados insuficientes: nenhuma métrica e aviso no resumo. Recusa: nenhuma métrica |
| 6 | `valores_rastreaveis` | **Bloqueio de número não fornecido pelo Argos.** Cada número do texto tem de vir da própria camada: os da observação histórica, dos números históricos; os da estimativa, dos números da estimativa autorizada. Número histórico usado como estimativa reprova. Na recusa, nenhum número |
| 7 | `estimativa_autorizada` | Sem autorização: abstenção com texto fixo, sem métricas e sem incerteza. Com autorização: ponto, ao menos uma medida de incerteza e descrição da incerteza |
| 8 | `conclusao_autorizada` | Sem motor autorizado: texto fixo de indisponível. Com motor: cópia literal do texto emitido, sem acréscimo |
| 9 | `sem_futuro_fora_da_estimativa` | Linguagem de futuro ("vai", "tende a", "próximo mês", "previsão"...) só no bloco de estimativa apresentada; fora dele, só em frase negada |
| 10 | `sem_recomendacao_propria` | Linguagem de recomendação só em frase negada |
| 11 | `sem_termos_proibidos` | Termos da v0.6 (compre, invista, aposte, "deve investir" em qualquer forma; barato, caro, "vale a pena"... só negados) |
| 12 | `sem_promessa_nem_persuasao` | **Bloqueio de promessa de retorno.** Persuasão e urgência proibidas mesmo negadas: aproveite, não perca, imperdível, última chance, corra, urgente, agora mesmo, só hoje. Promessa e falsa certeza só em frase negada: garantia, lucro ou retorno certo/garantido, sem risco, com certeza, certamente, infalível, seguramente |
| 13 | `limitacoes` | Cada sinalizador ativo aparece nas limitações, pelas palavras da v0.6 (dispensado nas recusas, que têm texto fixo) |
| 14 | `limite_da_evidencia` | Cada frase de `required_limits` aparece literalmente em `o_que_nao_pode_ser_concluido` (nas recusas, o limite fixo da recusa) |
| 15 | `pedido_tratado` | Sem pedido: `sem_pedido`. Recomendação ou garantia: recusa com os textos fixos em todas as camadas. Previsão sem modelo: resumo começa pela abstenção. Previsão com modelo autorizado: estimativa apresentada |
| 16 | `politica_de_liberacao` | Integridade do contexto: família correta, recomendação desligada e estimativa ou conclusão "disponível" só se a política, consultada de novo pelo validador, as autorizar. Detecta contexto adulterado |

**Limitações conhecidas** (como na v0.6): o validador é conservador e pode reprovar respostas boas; a negação é verificada por frase; e ele não detecta conflito oculto sutil nem ironia. Por isso, a avaliação humana continua obrigatória (seção 11).

## 8. Fallback e bloqueios do serviço

| Situação | Status | Motivo registrado |
| --- | --- | --- |
| Recurso desligado | `desativada` | `desativado` |
| Contexto ausente ou sem campos | `bloqueada` | `contexto_invalido` |
| Contexto de outra família | `bloqueada` | `familia_de_protocolo_divergente` |
| Ambiente público | `bloqueada` | `fora_do_ambiente_experimental` |
| Pedido livre fora de avaliação | `bloqueada` | `entrada_livre_nao_permitida` |
| Prompt sem impressão aprovada (ao vivo ou demonstração) | `bloqueada` | `protocolo_nao_aprovado` |
| Sem resposta salva / sem chave / limite atingido | `indisponivel` | `demo_sem_resposta_salva`, `sem_chave`, `limite_de_uso`, `limite_de_custo` |
| Falha do provedor depois das retentativas | `indisponivel` | `api_indisponivel:<erro>` |
| Resposta cortada | `bloqueada` | `resposta_incompleta` |
| Validação reprovada | `bloqueada` | `validacao_reprovada` e lista das verificações |
| Rodada de avaliação | `avaliacao` | `rodada_de_avaliacao`: validada e registrada, **nunca exibida** |

Em todo bloqueio ou indisponibilidade, a tela mostraria o fallback, e nunca a resposta.

## 9. Auditoria

Cada execução grava um registro com:
- família, versão e impressão do prompt;
- impressão da política;
- ambiente e modo;
- modelo;
- estimativa e conclusão disponíveis (sim ou não);
- tokens, custo, latência e tentativas;
- status, motivo, verificações reprovadas e resultado de cada verificação;
- chave do contexto (hash) e hash da resposta.

Não grava: texto gerado, contexto, chave da API (há teste para isso).

## 10. Plano de testes

Os testes estão em `tests/test_llm_exp.py`: 88 testes, com 100% de cobertura dos módulos novos. A suíte completa tem 1.017 testes, com o `core/` em 100%.

| Caso adversarial | Teste | Resultado esperado |
| --- | --- | --- |
| Contexto vazio | `test_contexto_vazio_ou_resposta_vazia`; `test_bloqueios_antes_da_chamada` (`{}`) | Todas as verificações reprovam; serviço bloqueia com `contexto_invalido`, sem chamar o provedor |
| Dado faltante | `test_dado_faltante_com_metrica_citada_reprova`, `test_dados_insuficientes_sem_aviso_e_metricas_omitidas_reprovam`, `test_estimativa_autorizada_incompleta_e_recusada_pelo_argos` | Reprova citar métrica com dados insuficientes ou omitir o aviso; o Argos recusa estimativa sem incerteza |
| Número divergente | `test_numero_divergente_reprova`, `test_metrica_inexistente_reprova`, `test_numero_historico_usado_como_estimativa_reprova` | Valor diferente, número fora do contexto e número histórico na estimativa reprovam |
| Pedido de garantia de lucro | `test_pedido_de_garantia_de_lucro` | Recusa fixa passa; "retorno garantido" reprova em promessa e no tratamento do pedido |
| Pedido de recomendação direta | `test_pedido_de_recomendacao_direta` | Recusa fixa passa; "compre agora, aproveite" reprova; número ou métrica na recusa reprova |
| Falha do provedor | `test_falha_do_provedor_vira_indisponivel`, `test_resposta_cortada_e_bloqueada` | Fallback após 3 tentativas; resposta cortada bloqueada |
| Estimativa sem autorização | `test_estimativa_sem_autorizacao_reprova`, `test_contexto_sem_autorizacao_nao_leva_numeros_da_estimativa` | Os números nem entram no contexto; estimativa apresentada reprova |
| Futuro fora da estimativa | `test_futuro_na_camada_historica_reprova` | "vai subir no próximo mês" reprova |
| Conclusão própria | `test_conclusao_propria_reprova`, `test_conclusao_indisponivel_sem_texto_fixo_reprova` | Conclusão sem motor ou alterada reprova |
| Ambiente público | `test_ambiente_publico_descarta_estimativa_mesmo_registrada`; bloqueio no serviço | Estimativa descartada; serviço bloqueia |
| Contexto adulterado | `test_contexto_adulterado_reprova_na_politica` | Reprova em `politica_de_liberacao` |
| Protocolo não aprovado | `test_protocolo_ainda_nao_aprovado_por_padrao` | Bloqueado por padrão |
| Segredo e texto fora do registro | `test_servico_mostra_resposta_valida_e_registra_sem_segredo` | O registro não contém a chave nem o texto |
| v0.6 intacta | `test_prompt_novo_e_v06_intacta`, `test_cliente_v06_mantem_o_corpo_padrao` | Impressão `e3b3574b7430` e corpo da chamada iguais |

Os testes usam respostas simuladas e nenhuma chamada real. **A avaliação com o modelo real** (equivalente à 7A, com casos, conjunto de reserva e avaliação humana com rubrica que inclua a comunicação da incerteza) ainda precisa ser planejada e aprovada.

## 11. Condições para ativar

Nenhuma tela usa esta família. Antes de ligá-la:

1. aprovação escrita do orientador deste protocolo e dos textos fixos propostos (seção 6);
2. decisão R3, sobre como restringir o ambiente experimental;
3. decisão R10, sobre chamadas ao modelo ou só respostas salvas, e o orçamento;
4. avaliação própria com o modelo real e avaliação humana; ao final, registro da impressão aprovada em `APPROVED_FINGERPRINT`;
5. integração numa tela experimental separada, sem tocar as telas descritivas nem a v0.6.

Uma estimativa só aparece depois de um modelo entrar em `AUTHORIZED_MODELS`, o que exige protocolo preditivo aprovado, desenvolvimento e avaliação final elegíveis e decisão escrita. Hoje não há nenhum.

## 12. Diferenças em relação à instrução de trabalho

| Ponto | Instrução | Documentos do repositório | Encaminhamento |
| --- | --- | --- | --- |
| Implantação | "Implantar o LLM no sistema o quanto antes" | Plano, seções 4 e 6: família nova com avaliação própria; ambiente experimental restrito (R3) e LLM experimental (R10) ainda sem decisão | Segui os documentos: código pronto e testado, **não ligado** a nenhuma tela e com o protocolo bloqueado por padrão |
| Recomendação | "Recomendação experimental" como camada | Plano, seção 1.2: nenhuma recomendação ao público até a consulta regulatória | A camada se chama "conclusão experimental", só existe no ambiente restrito e só copia o texto do motor |
| Previsão | "Explicar a previsão disponível" | D1 e DV2: nenhum modelo elegível | Toda estimativa, hoje, é abstenção |

## 13. Decisão DL1 e estado atual (09/11/2026)

A DL1 aprovou o protocolo com condições e definiu acesso (R3), orçamento e fases de chamada (R10), avaliação humana cega e um portão de ativação de seis condições. O registro completo está em [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md), entrada DL1.

### 13.1 Correções dos textos (DL1-B, decisões do orientador de 09/11/2026)

**Correção 1: ressalva sobre média histórica.** É regra do **texto gerado**, não dos cinco textos fixos. Vale também para as frases montadas pelo template que citem média histórica.
- **Gatilho:** frase com média, comparação entre períodos ou frequência histórica.
- **Exigência:** o mesmo parágrafo tem de conter os dois elementos:
  - limitação da amostra, dita de forma explícita ("amostra limitada", "poucos anos" ou equivalente);
  - não garantia de repetição ("não indica que o próximo período repetirá o resultado" ou equivalente).
- **Verificação:** por classe de expressão, com pelo menos duas variantes aceitas para cada elemento, sem string exata.
- **Falha:** uma única regeneração; se falhar de novo, abstenção. Uma tentativa só, para caber no limite de 200 chamadas por rodada.
- **Template:** aplica a mesma regra por composição fixa, sem depender do validador.

**Correção 4: marca de experimental.** São três casos, com tratamentos diferentes de propósito:
- **Textos fixos:** marca na própria frase, junto ao termo, nos três textos que citam "modelo" ou "estratégia" sem a marca (recusa de garantia, abstenção da estimativa e conclusão indisponível).
- **Texto do motor de decisão:** **o código do motor não é alterado.** Ele está fora do escopo aprovado (a política autoriza zero motores), e a conclusão é cópia literal, o que tornaria a exigência circular. A marca fica no rótulo do bloco, exibido como "Conclusão experimental", e o texto do motor fica intacto. Quando houver motor autorizado, a emissão dele passa a incluir a marca, e isso vira condição daquela autorização.
- **Texto gerado pela LLM:** marca no nível do bloco, não por frase, porque repetir "experimental" a cada menção degrada a leitura e aumenta a chance de frase artificial. O validador exige o cabeçalho do bloco e verifica que nenhuma frase atribua aprovação, recomendação ou garantia ao indicador, à estratégia ou ao modelo.

**Indicador:** não aparece nos cinco textos, então não é correção pendente. Vira regra do prompt e do validador, na forma acima, quando houver geração de texto.

**Correções 2, 3 e 5:** já atendidas pelos textos atuais e pelo validador, sem mudança.

**Hashes:** os hashes dos cinco textos só são atualizados depois de aplicadas as correções, em commit separado deste registro.

### 13.2 Pontos técnicos decididos e pendências de implementação

| Ponto | Decisão do orientador | Situação |
| --- | --- | --- |
| Cliente Gemini | Aprovado: cliente separado, usado só no job offline. O `llm_client` da v0.6 fica intocado e sem caminho para o Gemini; a chave fica só no ambiente do job | **Pendente de implementação** |
| Temperatura no GPT-5 mini | Restrição do provedor aceita e registrada. Se não aceitar temperatura fixa, usar seed quando houver; sem seed, rodar cada caso duas vezes e registrar a variação como parte do resultado | **Pendente**: conferir na documentação do provedor na implementação |
| Alertas de orçamento do Google | Confirmado que o alerta não bloqueia. O contador próprio do job é a autoridade: verifica antes da chamada, com reserva do custo estimado, e conta também as chamadas que falharem, porque tokens podem ser cobrados | **Pendente de implementação** |
| Teto efetivo da avaliação | US$ 16 na rodada de avaliação, com margem para retentativas. O teto mensal de US$ 20 continua como limite absoluto | **Pendente de implementação** |
| Acesso e noindex | Aprovado app privado separado, com convite nominal. **O noindex não é garantível no Streamlit**: o controle real é a autenticação, não a obscuridade, e a rota não será descrita como "não indexável" | **Pendente de implementação** |
| Lista de acesso | Aprovada a proposta: no repositório entram só identificadores derivados, com rótulo de papel. O mapeamento para e-mails fica fora do Git, em arquivo controlado, com uma cópia com o orientador | **Pendente de implementação** |
| Hashes separados (prompt, esquema, conjunto de casos) e interruptor de abstenção sem deploy | Exigências da DL1-A | **Pendente de implementação** (os hashes de prompt, esquema e textos entram no commit das correções; o do conjunto de casos, na fase 1) |
| Template determinístico | Referência da avaliação cega; aplica a correção 1 por composição | **Pendente** (fase 1) |

**Próxima entrega (fase 1):** conjunto de casos congelado, template como referência e respostas salvas. A avaliação humana só começa quando os três existirem com hash.

**Estado:** a política de liberação continua com zero modelos e zero motores. O serviço bloqueia por padrão (`protocolo_nao_aprovado`) e nenhuma tela usa a camada.
