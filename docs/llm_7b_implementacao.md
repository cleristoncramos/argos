# Etapa 7B — Explicação assistida por modelo de linguagem: implementação controlada

Documento técnico da implementação da 7B do Argos DataLab (projeto educativo e de pesquisa, PIBITI UFPI). Registra o que foi construído, como cada condição da liberação foi atendida, como operar e o que ainda está pendente.

**Base de decisão:** liberação da 7B pelo orientador em 12/10/2026, com condições (ver `docs/pibiti/decisoes_orientador.md`). A 7A foi concluída para progressão com **limitação metodológica registrada**: o kappa ponderado da avaliação humana ficou abaixo de 0,60 em clareza e neutralidade (ver `docs/relatorio_validacao_7a.md`). Esse resultado não foi reinterpretado como aprovação estatística da rubrica e continua valendo como limitação.

**Escopo:** o recurso explica, em linguagem simples, resultados que o Argos já calculou. Não calcula, não escolhe ativos, não recomenda e não prevê.

## 1. Arquitetura

```
tela do Argos (métricas já calculadas)
   └─ core/llm_builders.py     monta o contexto JSON (ids, rótulos e unidades da 7A)
        └─ core/llm_service.py explain(): fluxo fechado
             ├─ modo off     não chama nada (padrão)
             ├─ modo demo    resposta salva, sem rede e sem chave
             └─ modo live    core/llm_client.py → API → resposta bruta
                  └─ core/llm_validation.py  validador obrigatório (também no modo demo)
                       ├─ aprovada  → app/ui/llm_explain.py exibe, com aviso fixo
                       └─ reprovada / falha / indisponível → texto educativo fixo
```

| Arquivo | Função |
|---|---|
| `core/llm_prompts.py` | Prompt v0.6 congelado e esquema de saída (impressão digital `e3b3574b7430`). Não alterado na 7B. |
| `core/llm_validation.py` | Validador da 7A (8 verificações obrigatórias). Não alterado na 7B. |
| `core/llm_client.py` | Chamada à API: gpt-5-mini, 1.400 tokens, timeout de 20 s, até 2 retentativas. Único arquivo com o endereço da API. |
| `core/llm_service.py` | Pipeline `explain()`, limite de uso e custo, registro de uso, modo demonstração. |
| `core/llm_builders.py` | Contexto por tela (individual, risco e retorno, simulação, comparação de 2 ativos, janela sazonal). |
| `core/llm_render.py` | Formatação (padrão brasileiro) e escape do texto gerado antes de exibir. |
| `app/ui/llm_explain.py` | Seção "Explicação assistida por IA" nas telas (botão, aviso, resultado, registro). |
| `experiments/llm_7b/make_demo_store.py` | Gera `data/llm_demo.json` a partir das respostas validadas da 7A. |

## 2. Condições da liberação e como foram atendidas

| # | Condição | Situação | Como / onde |
|---|---|---|---|
| 1 | Usar o modelo principal gpt-5 mini | Atendida | `llm_client.MODEL = "gpt-5-mini"`; nenhum outro modelo é chamado. |
| 2 | gpt-5 nano fora da interface | Atendida | Não há seleção de modelo nem chamada ao nano no código da aplicação. |
| 3 | Prompt congelado v0.6 e impressão digital | Atendida | `explain()` confere versão e impressão digital em toda chamada (`prompt_divergente` bloqueia antes de qualquer envio). Teste: `test_prompt_divergence_blocks_before_any_call`. |
| 4 | Enviar só contexto JSON estruturado do Argos | Atendida | A mensagem é `build_messages(contexto)`, e o contexto vem de `llm_builders` com métricas já calculadas. |
| 5 | Sem entrada livre do usuário | Atendida | Não há campo de texto na interface; contexto com `user_request` é recusado antes da chamada (`entrada_livre_nao_permitida`). |
| 6 | Sem navegação, ferramentas externas ou execução de código pela LLM | Atendida | O corpo da requisição não tem `tools` nem `functions` (`test_payload_uses_frozen_prompt_and_fixed_params`). |
| 7 | JSON Schema estrito na saída | Atendida | `response_format` com `strict: true` e `additionalProperties: false`. |
| 8 | Validação automática antes de exibir | Atendida | `_finish()` valida toda resposta, inclusive a salva do modo demonstração. |
| 9 | Bloquear recomendação, previsão, inconsistência e termo proibido | Atendida | Verificações do validador; reprovação gera status `bloqueada` e o fallback. |
| 10 | Fallback educativo fixo em falha, bloqueio ou indisponibilidade | Atendida | `FALLBACK_TEXT` é exibido em todos os casos sem resposta validada, com o motivo técnico em letra pequena. |
| 11 | Limite de 1.400 tokens de saída | Atendida | `max_completion_tokens = 1400`; resposta com `finish_reason` diferente de `stop` é bloqueada (`resposta_incompleta`). |
| 12 | Timeout de 20 s e no máximo 2 retentativas | Atendida | 20 s por tentativa; retenta apenas em 429, 5xx e falha de rede, com espera de 1 s e 2 s. Erros 4xx não são repetidos. Pior caso: 3 tentativas. |
| 13 | Registrar modelo, versão do prompt, tokens, custo, status e motivo de bloqueio | Atendida | `logs/llm_uso.jsonl` (campos na seção 4). |
| 14 | Segredo da API fora do repositório | Atendida | A chave vem de `OPENAI_API_KEY` (variável de ambiente ou segredos do Streamlit). `logs/` está no `.gitignore`. O registro não guarda a chave (teste dedicado). |
| 15 | Limites de custo e uso aprovados | **Atendida com premissa** | `UsageLimiter` por sessão: 20 chamadas e US$ 0,50 (estimado). Os valores foram definidos pelo desenvolvedor por não constarem nos registros; **precisam de confirmação do orientador** (seção 6). |
| 16 | Não apresentar a LLM como recomendação ou previsão | Atendida | Aviso fixo em toda explicação; regras do prompt; validador. |
| 17 | Textos educativos fixos acessíveis sem LLM | Atendida | A explicação é um bloco adicional; os textos educativos das telas não dependem dela, e o padrão do app é `off`. |
| 18 | Modo demonstração com respostas salvas ou fallback offline | Atendida | `ARGOS_LLM_MODE=demo` usa `data/llm_demo.json`; sem resposta salva para o contexto, mostra o fallback. |

## 3. Telas e formatos cobertos

O recurso só aparece onde o formato do contexto foi validado na 7A.

| Tela | Quando aparece | Métricas enviadas |
|---|---|---|
| Análise Individual | Sempre que há análise carregada | retorno total, retorno médio, volatilidade |
| Análise Individual — janela sazonal | Após aplicar uma janela de entrada e saída | média, mediana e anos positivos, com N |
| Risco e Retorno | Sempre que há análise carregada | seis métricas da tela (Sharpe com a taxa livre de risco informada) |
| Simulação de Aportes | Sempre que há simulação carregada | totais, valores finais e retornos das duas estratégias |
| Comparação de Ativos | **Somente com exatamente 2 ativos** | retorno total de cada um e correlação |

Fora do escopo desta versão: comparação de 3 a 5 ativos, médias mensais do mapa sazonal inteiro, indicadores técnicos, qualquer pergunta livre.

## 4. Operação

**Configuração** (variáveis de ambiente ou `secrets.toml` do Streamlit):

| Nome | Valores | Efeito |
|---|---|---|
| `ARGOS_LLM_MODE` | `off` (padrão), `demo`, `live` | `off`: o botão não aparece. `demo`: respostas salvas. `live`: chama a API. |
| `OPENAI_API_KEY` | chave da API | Necessária só no modo `live`. Nunca vai ao repositório. |
| `ARGOS_LLM_RECORD` | `1` | No modo `live`, grava cada resposta aprovada em `data/llm_demo.json` (uso do pesquisador). |

**Preparar a demonstração:** rodar no modo `live` com `ARGOS_LLM_RECORD=1`, gerar as explicações das telas desejadas, conferir o conteúdo de `data/llm_demo.json` e fazer o commit. Depois, no modo `demo`, as mesmas análises reproduzem essas respostas sem rede e sem custo (e são validadas de novo antes de aparecer).

**Registro de uso** (`logs/llm_uso.jsonl`, uma linha por clique, fora do git): data e hora, modo, modelo, versão e impressão digital do prompt, tokens de entrada e saída, custo estimado (US$), tempo, tentativas, status (`ok`, `demo`, `bloqueada`, `indisponivel`, `desativada`), motivo, verificações que falharam, chave do contexto, hash da resposta e tela. O texto gerado e a chave não são gravados.

## 5. Custo e desempenho de referência (7A)

Execução oficial da v0.6 (gpt-5 mini, 78 respostas): custo médio de US$ 0,001484 por explicação (limite de US$ 0,002) e tempo médio de 3,35 s (limite de 8 s). Esses valores são de referência; o custo real em uso fica no registro de uso.

## 6. Limitações e pendências

1. **Limitação da avaliação humana (7A):** kappa ponderado abaixo de 0,60 em clareza e neutralidade; a 7B não elimina nem altera esse registro. Trabalho futuro: reancorar a escala com exemplos e ampliar o conjunto de itens.
2. **Falso positivo conhecido do validador:** o verbo "aplicar" em uso descritivo (por exemplo "ao aplicar um único aporte") é bloqueado em `sem_recomendacao`. Na tela, isso resulta no fallback. Qualquer ajuste exige nova versão, nova impressão digital e nova execução da 7A.
3. **Limites de uso e custo (condição 15):** valores de 20 chamadas e US$ 0,50 por sessão são premissa do desenvolvedor, **a confirmar com o orientador**. O limite é por sessão do navegador, não global: não impede o uso repetido em várias sessões. Recomenda-se também um teto de gasto na conta do provedor da API.
4. **Política de dados do provedor:** o contexto enviado contém apenas tickers, datas e métricas agregadas (sem dados pessoais). A política de retenção e de uso de dados da API deve ser conferida e citada no relatório.
5. **Evidência da liberação:** arquivar o original da mensagem do orientador com a decisão de 12/10/2026 (data e remetente) fora do repositório.
6. **Testes de tela:** os testes automáticos cobrem `core/` (100%), mas não executam o Streamlit. A verificação das telas é manual (modo `off`, `demo` e `live` em cada tela com botão). Registrar o resultado.
7. **O6 (compreensão e usabilidade):** continua condicionada à Plataforma Brasil e ao parecer do CEP/UFPI. A 7B não inicia coleta com participantes.

## 7. Lista de verificação antes de ligar o modo `live` em ambiente público

- [ ] Original da decisão do orientador arquivado.
- [ ] Limites de uso e custo confirmados (ou ajustados em `DEFAULT_MAX_CALLS` e `DEFAULT_MAX_COST_USD`).
- [ ] Teto de gasto configurado na conta do provedor.
- [ ] Chave guardada nos segredos do ambiente de execução, nunca no repositório.
- [ ] `logs/` ignorado pelo git; plano de guarda do registro de uso.
- [ ] Cada tela com botão testada nos três modos.
- [ ] `data/llm_demo.json` conferido (somente respostas aprovadas, sem texto inadequado).
- [ ] `python -m pytest -q` sem falhas e com 100% de cobertura em `core/`.

**Gravação realizada:** em 12/10/2026, no modo `live` com `ARGOS_LLM_RECORD=1`, foram gravadas as respostas das 5 telas com período fixo (04/01/2021 a 31/12/2025, frequência diária), totalizando 38 respostas em `data/llm_demo.json` (26 derivadas dos casos da 7A e 12 gravadas em telas reais). Alterar ativo, período, frequência ou parâmetros muda a chave do contexto e faz a tela mostrar o texto fixo com o motivo `demo_sem_resposta_salva`.
**Teste do modo demonstração:** em 12/10/2026, sem chave e sem acesso à API, as 5 telas exibiram as respostas gravadas, com status `demo` e custo zero (ver seção 8).


## 8. Verificação manual das telas

Os testes automáticos cobrem `core/` (730 testes, 100% de cobertura em 12/10/2026) mas não executam o Streamlit. Esta tabela registra a verificação manual das telas. Parâmetros usados na demonstração: período de 04/01/2021 a 31/12/2025, frequência diária, taxa livre de risco 0%, ativo AAPL (comparação: AAPL e ^GSPC; janela sazonal: entrada em setembro, saída em outubro).

| Tela | Modo `off` | Modo `live` | Modo `demo` | Observação |
|---|---|---|---|---|
| Análise Individual | pendente | OK (12/10/2026) | OK (12/10/2026) | |
| Janela sazonal | pendente | OK (12/10/2026) | OK (12/10/2026) | |
| Risco e Retorno | pendente | OK (12/10/2026) | OK (12/10/2026) | |
| Simulação de Aportes | pendente | OK (12/10/2026) | OK (12/10/2026) | |
| Comparação de 2 ativos | pendente | OK (12/10/2026) | OK (12/10/2026) | |

Critérios de aprovação por tela e modo:
- `off`: o botão "Explicar com IA" não aparece e o restante da tela funciona normalmente.
- `live`: a explicação aparece com o aviso educativo, o registro de uso mostra `status: ok` e `logs/llm_uso.jsonl` não contém a chave nem o texto gerado.
- `demo`: a explicação aparece igual à gravada, o registro mostra `status: demo`, `input_tokens: 0` e `cost_usd: 0.0`, sem rede e sem chave.

Falha de qualquer critério, ou texto fixo de contingência, é registrada na coluna Observação com o `reason` do registro de uso.