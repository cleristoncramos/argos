# Conferência da versão publicada (Streamlit Community Cloud)

Pedido do orientador em 25/10/2026: conferir a versão efetivamente publicada das fases 1 a 3 do plano de ampliação, por funcionalidade, antes de considerá-las encerradas. Este documento registra cada conferência, com os resultados observados e as evidências.

## Conferência 1 — 25/10/2026

| Campo | Valor |
| --- | --- |
| Data | 25/10/2026 |
| Responsável | Clériston de Castro Ramos (desenvolvedor) |
| Método | Roteiro automatizado de navegador (Playwright, Chromium) sobre o endereço público, com capturas de tela em [`evidencias/deploy_2026-10-25/`](evidencias/deploy_2026-10-25/), e conferência local no modo de demonstração para a explicação assistida |
| Endereço | https://argos-datalab.streamlit.app |
| Branch | `main` |
| Commit publicado | `6ab02d1` ("feat: página Panorama do Catálogo (A3, primeira versão) e conclusão da fase 3"), o último de `main` no momento da conferência |
| Como o commit foi identificado | Indiretamente: a versão publicada exibe a página "Panorama do Catálogo", criada nesse commit, e o catálogo de 148 ativos. A interface pública não mostra o commit; confirmar no painel "Manage app" do Streamlit Cloud |

| Bloco | Conferência mínima | Resultado observado | Situação |
| --- | --- | --- | --- |
| A4 — Qualidade dos dados | Alertas aparecem nos cenários previstos, sem impedir análises válidas | `XPML11.SA` pelo "Digitar ticker": quadro "Atenção aos dados" com a mudança de patamar de 14/01/2026, e a análise completa segue disponível (7 gráficos). `PETR4.SA`: nenhum quadro, como esperado | Conferido |
| A1 — Variação por prazo | Janelas, datas usadas e ausência de histórico corretas | `PETR4.SA`, 5 anos: base explícita (01/11/2021 a 23/10/2026); 1 mês +18,31% (23/09 → 23/10/2026); "1 ano" com taxa anual igual à acumulada (+94,37%); "5 anos" com início ajustado (01/11/2021\*); "10 anos" como "—" | Conferido |
| A7 — Quedas e recuperação | Datas e durações legíveis; quedas não recuperadas identificadas | `BTC-USD`, 5 anos, diário: -76,63% (08/11/2021 → 21/11/2022 → recuperação em 04/03/2024, 847 dias); -53,06% desde 06/10/2025 como "não recuperado até a última observação disponível" | Conferido |
| A8 — Extremos do período | Altas e quedas respeitam período e frequência | `PETR4.SA`, mensal: "33 de 59 variações mensais", "out/2026 (em andamento)"; diário: "666 de 1242 variações diárias" | Conferido |
| Catálogo | 148 ativos, seleção, classificação e descrições coerentes | Página Sobre e página inicial mostram 148. Panorama, grupo a grupo, soma 148 ativos nos 13 grupos (19, 22, 17, 8, 8, 14, 6, 5, 7, 12, 8, 15, 7). Inclusões presentes (ex.: `VISC11.SA`); `XPML11.SA` fora do catálogo | Conferido |
| A2 — Referência de mercado | Referência identificada, alinhamento temporal, avisos de moeda e período | `PETR4.SA`: sugestão Ibovespa com motivo; "Entre 30/11/2021 e 23/10/2026 (datas comuns aos dois)"; aviso de índice em pontos. `IVVB11.SA`: S&P 500 com aviso de câmbio. `MXRF11.SA`: sem sugestão, com o motivo (IFIX indisponível) | Conferido |
| A3 — Panorama | Ordem inicial por nome, métricas legíveis, falhas parciais tratadas | 13 grupos gerados sem erro (cerca de 8 s cada); ordem inicial por nome em todos; aviso "A ordem da tabela não é uma recomendação"; ordenação por queda máxima funcionando; taxas de juros com "—" e nota. Nenhuma falha parcial ocorreu na conferência, então esse caminho segue coberto só pelos testes automáticos | Conferido, com ressalva |
| Explicação assistida | Contexto corresponde à análise; fallback e limites funcionando | Na versão pública o recurso está desligado, conforme a decisão N22: nenhuma página exibe "Explicar com IA" e os roteiros fixos "Como ler este gráfico" estão presentes. No modo demo local, o fallback educativo aparece com o motivo técnico. **Achado:** no modo demo completo (`ARGOS_DEMO_MODE=true`), o cenário congelado não reproduz as respostas salvas (ver "Achados") | Conferido, com achado |
| Navegação e exportação | Páginas abrem sem erro; downloads funcionam | As 7 páginas do menu abrem sem erro. "Baixar CSV" da Análise Individual gerou `PETR4.SA_dados_tratados.csv` com 61 linhas. **A página inicial exibe `IndexError`** depois dos cartões de "Primeiros passos" (ver "Achados") | **Falha encontrada** |

### Achados

1. **Erro na página inicial (falha).**
   - **Sintoma.** A versão publicada mostra `IndexError` logo abaixo dos cartões "Primeiros passos" e não exibe o rodapé ([evidência](evidencias/deploy_2026-10-25/cloud_home_erro.png)).
   - **Causa.** A inclusão da sétima página (Panorama do Catálogo) deixou a última fileira da grade de 3 colunas incompleta, e o laço lia uma posição inexistente da lista de páginas.
   - **Por que os testes não pegaram.** A conferência local da A3 procurou só o texto do novo módulo, e os testes automáticos não executavam as páginas.
   - **Correção (local, ainda não publicada).** O laço agora para na última página (`app/views/home.py`).
   - **Prevenção.** Novo teste de fumaça (`tests/test_app_smoke.py`, Streamlit AppTest) abre a página inicial e o estado inicial das 7 páginas. Sem a correção, o teste falha com `tuple index out of range`.
   - **Pendente.** Publicar a correção e reconferir a página inicial.
2. **Modo demo completo e respostas de IA salvas (achado).**
   - **Por que não coincidem.** As respostas de `data/llm_demo.json` foram gravadas em 12/10/2026 com dados ao vivo, de 04/01/2021 a 31/12/2025. O pacote de dados salvos (`data/demo/`, gerado em 10/10/2026) cobre de 11/10/2021 a 09/10/2026.
   - **Efeito.** Com `ARGOS_DEMO_MODE=true`, o cenário congelado não pode ser reconstruído, e a explicação mostra o texto fixo (`demo_sem_resposta_salva`).
   - **O que não mudou.** Com os dados ao vivo e só a LLM em modo demo, a chave do contexto coincide com a salva. Ou seja, os recursos novos não alteraram o contexto da explicação.
   - **Encaminhamento.** Resolver no primeiro snapshot do catálogo ampliado: alinhar o período do pacote com o das respostas salvas, ou regravar as respostas sobre o pacote.
3. **Referência no modo demo (observação).** O pacote atual não inclui o Ibovespa (`^BVSP`). No modo demo, `PETR4.SA` mostra a mensagem de dados da referência indisponíveis, sem erro. Incluir `^BVSP` no próximo snapshot.

### Situação ao fim da conferência 1

**Implementação concluída; publicação conferida com pendência.** A correção da página inicial precisava ser publicada e reconferida (ver conferência 2).

## Conferência 2 — 25/10/2026 (reconferência após a correção)

| Campo | Valor |
| --- | --- |
| Data | 25/10/2026 |
| Responsável | Clériston de Castro Ramos (desenvolvedor) |
| Método | O mesmo roteiro automatizado da conferência 1, repetido por inteiro sobre o endereço público |
| Branch | `main` |
| Commit publicado | `958b729` ("fix: grade da página inicial com número de páginas não múltiplo de 3; teste de fumaça e registro da conferência do deploy") |
| Como o commit foi identificado | A página inicial publicada deixou de exibir o `IndexError` e passou a mostrar o rodapé, comportamento introduzido nesse commit. O novo deploy já estava ativo cerca de 25 s após o push |

| Bloco | Resultado observado | Situação |
| --- | --- | --- |
| Navegação | A página inicial abre sem exceção, com os 7 cartões e o rodapé ([evidência](evidencias/deploy_2026-10-25/cloud_home_corrigida.png)). As 7 páginas do menu abrem sem erro | Verificado |
| A4 | Igual à conferência 1: quadro para `XPML11.SA`, análise completa (7 gráficos); nenhum quadro para `PETR4.SA` | Verificado |
| A1 | Igual à conferência 1 (base explícita, datas usadas, início ajustado, "—" sem histórico) | Verificado |
| A7 | Igual à conferência 1 (quedas recuperadas e a de -53,06% como não recuperada) | Verificado |
| A8 | Igual à conferência 1 (mensal e diário, período em andamento marcado) | Verificado |
| Catálogo | 148 ativos somados pelo Panorama nos 13 grupos; 148 na página inicial e na página Sobre | Verificado |
| A2 | Igual à conferência 1 (`PETR4.SA` × Ibovespa, `IVVB11.SA` com aviso de câmbio, `MXRF11.SA` sem sugestão) | Verificado |
| A3 | 13 grupos sem erro, ordem inicial por nome em todos, aviso presente, taxas com "—" e nota | Verificado, com a ressalva da conferência 1 (falha parcial não ocorreu; coberta por testes) |
| Explicação assistida | Desligada na versão pública (decisão N22), com os roteiros fixos presentes. O ajuste entre o pacote de dados salvos e as respostas salvas segue para o primeiro snapshot (achado 2) | Verificado na versão pública; pendência no modo demo |
| Exportação | "Baixar CSV" gerou `PETR4.SA_dados_tratados.csv` com 61 linhas | Verificado |

### Situação

**Publicação verificada** das fases 1 a 3 (commit `958b729`). Ressalvas registradas:

- o caminho de falha parcial do panorama não ocorreu na conferência e segue coberto pelos testes automáticos;
- no modo demo completo, as respostas de IA salvas não coincidem com o período do pacote de dados (achado 2);
- o pacote não inclui o Ibovespa (achado 3).

Os dois últimos pontos são do modo de demonstração, não da versão publicada, e entram no primeiro snapshot do catálogo ampliado.
