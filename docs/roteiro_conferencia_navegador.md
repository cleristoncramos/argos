# Roteiro de Conferência no Navegador — Argos DataLab

**Criado em:** 09/10/2026 · **Plano 2, Bloco 1 (tarefas 1.1 e 1.2)** · **Quem executa:** o autor do projeto · **Tempo estimado:** 45 a 60 minutos

**Finalidade:** conferir na interface o que foi entregue em 07/10/2026 e que está marcado `[~]` no `docs/checklist_pendencias.md`. Cada cenário tem um resultado esperado. Marque **OK** ou **Falhou** e anote o que viu. Quando o cenário passa, o item correspondente do checklist pode virar `[x]`.

---

## 0. Preparação

1. No PowerShell, na pasta do projeto, rode a aplicação com o ambiente virtual ativo (`streamlit run app/main.py`, ou o comando que você já usa).
2. Rode `python -m pytest` antes de começar e anote o resultado (esperado após o Bloco 1: **405 passando**, `core/` em 100%).
3. **Diagnóstico do pandas** (tarefa 1.3). Rode:

```powershell
python -c "import pandas as pd; print(pd.__version__); print(pd.Series([100, None, 121]).pct_change().tolist())"
```

| Resultado | Significado |
| --- | --- |
| Versão 3.x e `[nan, nan, nan]` | O `pct_change` já não preenche lacunas. O ajuste do Bloco 1 só protege contra mudança de versão |
| Versão 2.x e `[nan, 0.0, 0.21]` (pode vir com `FutureWarning`) | O pandas preenchia lacunas: antes do ajuste, uma lacuna virava retorno 0. O ajuste do Bloco 1 corrige isso |

Anote a versão: **______**

---

## 1. Cenários

Registre o resultado em cada linha. "Esperado" descreve o comportamento correto; qualquer diferença deve ser anotada como **Falhou**, com o que apareceu.

| ID | Página | Passos | Esperado | Resultado |
| --- | --- | --- | --- | --- |
| S01 | Análise Individual | `BTC-USD`, período de 5 anos, frequência **diária**. Clicar em analisar | A página carrega sem erro. O mapa de calor "Variação Mensal Histórica" aparece, com anos nas linhas e meses nas colunas; células sem dado ficam vazias. A legenda sob o gráfico descreve o cálculo | ☐ OK ☐ Falhou |
| S02 | Análise Individual | Mesmo ativo, frequência **mensal** | O mapa de calor continua coerente (mesma leitura de variação mensal) e sem erro | ☐ OK ☐ Falhou |
| S03 | Análise Individual | Frequência **semanal** | Sem erro; mapa de calor presente | ☐ OK ☐ Falhou |
| S04 | Sidebar | "Personalizado": data inicial **igual ou posterior** à final | Mensagem de erro e botão de análise **desabilitado** | ☐ OK ☐ Falhou |
| S05 | Sidebar | "Personalizado": data final **no futuro** | Mensagem de erro e botão desabilitado | ☐ OK ☐ Falhou |
| S06 | Sidebar | "Personalizado": datas válidas (ex.: 01/01/2023 a 31/12/2023) | Botão habilitado; análise roda | ☐ OK ☐ Falhou |
| S07 | Análise Individual | Período muito curto (ex.: 15 dias) em frequência mensal | Mensagem de dados insuficientes ou aviso; **sem traceback** e sem mapa de calor quebrado | ☐ OK ☐ Falhou |
| S08 | Análise Individual | `BTC-USD`: verificar o gráfico de sazonalidade e a volatilidade mensal | Sem erro; valores plausíveis; textos "O que significa?" presentes | ☐ OK ☐ Falhou |
| S09 | Risco e Retorno | `BTC-USD`, 5 anos | Página carrega. A **data do pior drawdown** aparece junto da métrica | ☐ OK ☐ Falhou |
| S10 | Risco e Retorno | `CL=F` com período que inclui **abril de 2020** (ex.: 01/01/2020 a 31/12/2020) | Mensagem **clara** dizendo que há preço zero ou negativo e que retorno percentual e drawdown não podem ser calculados. **Sem traceback** e sem texto cru de exceção | ☐ OK ☐ Falhou |
| S11 | Risco e Retorno | `CL=F` em período sem preço negativo (ex.: 2023) | Funciona normalmente | ☐ OK ☐ Falhou |
| S12 | Comparação | `CL=F` + `BTC-USD`, período de 2020 | `CL=F` é **excluído com aviso** (preço ≤ 0); a comparação segue sem erro com os demais; Base 100 e correlação aparecem | ☐ OK ☐ Falhou |
| S13 | Comparação | Dois ativos com históricos de início diferentes (ex.: `BTC-USD` e um ativo de IPO recente), 10 anos | Aviso de **períodos divergentes**. Com "Comparar apenas o período comum" marcado, os dois são cortados no intervalo comum | ☐ OK ☐ Falhou |
| S14 | Comparação | Frequência **mensal** e depois **semanal** com 3 ativos de calendários diferentes (ex.: `BTC-USD`, `PETR4.SA`, `^GSPC`) | Tabela de dados **sem datas duplicadas** nem linhas quebradas (alinhamento por fim de período) | ☐ OK ☐ Falhou |
| S15 | Comparação | Selecionar 5 ativos | Aceita 5 e não permite o sexto | ☐ OK ☐ Falhou |
| S16 | Indicadores Técnicos | Ativo em **R$** (ex.: `PETR4.SA`) e depois em **US$** (ex.: `AAPL`) | O rótulo do eixo/legenda de preço mostra a moeda correta (R$ e US$) | ☐ OK ☐ Falhou |
| S17 | Simulação de Aportes | Abrir pelo menu; rodar com `BTC-USD` | A página aparece no menu e roda sem erro. Anote se o texto da simulação histórica e os rótulos "pior/mediana/melhor" estão presentes (serão revisados no Bloco 4) | ☐ OK ☐ Falhou |
| S18 | Downloads CSV | Em cada uma das 4 páginas (Análise Individual, Risco e Retorno, Indicadores Técnicos, Comparação), clicar em baixar CSV | O arquivo baixa. O nome não tem acento, espaço nem `^` (ex.: `^BVSP` vira um nome limpo). Abre no Excel com colunas separadas e acentos corretos. Anote o separador usado | ☐ OK ☐ Falhou |
| S19 | Sidebar | Digitar um ticker **inexistente** | Mensagem clara de ticker não encontrado | ☐ OK ☐ Falhou |
| S20 | Sidebar | Digitar um ticker **válido fora do catálogo** | Funciona e avisa que o ativo não tem metadados do catálogo | ☐ OK ☐ Falhou |

---

## 2. Registro dos problemas

Para cada cenário que falhou, preencher:

| ID do cenário | O que apareceu | Mensagem de erro (copiar) | Prints / arquivo | Gravidade (bloqueia / incomoda / cosmético) |
| --- | --- | --- | --- | --- |
| | | | | |

---

## 3. Depois da execução

1. Cenários **OK** → converter os itens correspondentes de `[~]` para `[x]` em `docs/checklist_pendencias.md`:
   - S01–S03: mapa de calor com `create_monthly_return_matrix` (frequência diária e mensal)
   - S09: data do pior drawdown
   - S10–S12: tratamento de `ValueError` com `CL=F`
   - S14: `PeriodEnd` na página de comparação
   - S16: rótulo da moeda (`price_label`)
   - S17: página "Simulação de Aportes" registrada em `app/main.py`
   - S18: os 4 downloads de CSV
   - S04–S07: validação de datas e filtro vazio
2. Cenários **Falhou** → enviar o registro da seção 2 para correção.
3. Anotar versão do pandas, data e resultado do `pytest` no `docs/checkpoint_qualidade.md`.

---

## Anexo — Bloco 2 (sazonalidade por anos, meses e janela)

Página: **Análise Individual**, seção "Padrões Sazonais", bloco "Recorte por anos e meses". Use `BTC-USD`, período longo (5 anos ou mais), frequência diária.

| ID | Passos | Resultado esperado |
| --- | --- | --- |
| S21 | Escolher 1 ano, deixar meses e janela vazios, clicar "Aplicar filtro" | Gráfico com duas barras por mês (média de todos os anos × média do recorte), tabela com média, diferença em p.p., mediana, % de anos positivos e N; texto metodológico visível acima do formulário |
| S22 | Escolher entrada = Set e saída = Out, sem anos, "Aplicar filtro" | Janela "fechamento de Set → fechamento de Out"; para cada ano, o retorno da janela é igual à célula de outubro do mapa de calor do mesmo ano |
| S23 | Escolher entrada = Nov e saída = Fev | Anos rotulados pelo ano da entrada; o último ano só aparece se houver fechamento de fevereiro seguinte |
| S24 | Aplicar sem ano e sem janela; depois só a entrada sem a saída; depois entrada igual à saída | Aviso claro em cada caso, sem erro na tela; trocar de ativo não mantém o filtro do ativo anterior |

Conferências adicionais: (a) o mês em andamento não entra nas médias e há uma linha de aviso; (b) com todos os anos selecionados, a "média do recorte" é igual à "média de todos os anos"; (c) nenhum texto novo usa "melhor mês", "pior mês", recomendação ou previsão.

## Anexo — Bloco 3 (Comparação)

Página: **Comparação de Ativos**. Use `BTC-USD`, `AAPL`, `GC=F` (ou 5 ativos de classes diferentes), período de 5 anos, frequência Diária.

| ID | Passos | Resultado esperado |
| --- | --- | --- |
| S25 | Aba "Desempenho": clicar uma vez no nome de um ativo na legenda; depois dois cliques em outro | O primeiro some/volta; o segundo isola; a linha "Dica: clique no nome de um ativo..." aparece abaixo do gráfico |
| S26 | Aba "Sazonalidade" | Gráfico de barras agrupadas (12 meses × ativos), tabela com "média (N=...)" por ativo e mês, textos metodológicos visíveis; ativo de histórico curto mostra N menor |
| S27 | Comparar com "Comparar apenas o período comum" ligado e desligado | N por ativo na aba Sazonalidade muda coerentemente; nenhum erro |
| S28 | Frequência Mensal e Semanal | A aba Sazonalidade continua funcionando (médias iguais às de frequência diária, salvo diferenças de fechamento) |
| S29 | "Destaques do Período" | Rótulos: "Maior retorno acumulado no período analisado", "Menor retorno acumulado no período analisado", "Menor queda máxima observada", "Maior Sharpe no período analisado" |
| S30 | 5 ativos de classes diferentes em tela padrão | Todas as abas legíveis, sem corte horizontal |

## Anexo — Bloco 4 (Simulação Histórica)

| ID | Passos | Resultado esperado |
| --- | --- | --- |
| S31 | Abrir a página "Simulação Histórica de Aportes" | No topo, o aviso com o texto exato: "Esta é uma simulação histórica hipotética. Ela mostra como um valor teria evoluído no período selecionado, sem representar previsão, recomendação ou garantia de resultado futuro." |
| S32 | Carregar `BTC-USD`, 5 anos, mensal; abrir "Histórico carregado" | Premissas: preço de fechamento, sem ajuste por dividendos, sem corretagem, taxas ou impostos, valores na moeda do ativo |
| S33 | Seção "Como terminaram as diferentes janelas" | Colunas: Menor retorno histórico, Início da janela de menor retorno, Mediana, Maior retorno histórico, Início da janela de maior retorno, Janelas com retorno positivo; nenhuma palavra "pior" ou "melhor" |
| S34 | Tentar `^TNX` | Mensagem de que é uma taxa de juros e não pode ser simulada |