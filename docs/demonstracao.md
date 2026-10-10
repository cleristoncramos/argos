# Estratégia de demonstração

Plano 2, item 8.6 e novo item 8.8 (decisões N18, N22, N24 e a decisão de 10/10/2026 sobre o modo de demonstração). Vale para o SBBD (trilha de demos), a defesa e reuniões com o orientador.

> **Requisito obrigatório do congelamento.** A demonstração ao vivo sem internet só é viável se o Argos tiver um **modo de dados salvos implementado e testado antes do congelamento da versão**. Sem ele, a demo depende do Yahoo Finance, da conexão de rede e possivelmente da API de modelo de linguagem, que são exatamente os pontos que podem falhar durante a apresentação. A seção 2 deixa de ser melhoria opcional.

## 1. Camadas da demonstração

| Camada | Descrição | Papel |
| --- | --- | --- |
| 1. Local, modo offline com dados salvos | A aplicação roda no computador do apresentador, a partir da **versão congelada**, com `ARGOS_DEMO_MODE=true`. Nenhuma chamada externa | **Principal** |
| 2. Screencast de até 5 minutos | Gravação da mesma versão, com link público | **Reserva obrigatória** |
| 3. Streamlit Community Cloud | Aplicação pública, em modo de demonstração, como vitrine | Acesso público **complementar**; não é garantia da demo |

Se a internet do local falhar, a apresentação continua no computador local, com `ARGOS_DEMO_MODE=true` e datasets congelados. Não confundir com o vídeo curto da página inicial (30 a 90 s), que é do Plano 3.

## 2. Modo de demonstração com dados salvos

### 2.1 Requisitos mínimos

O modo deve cobrir, no mínimo:

1. Datasets locais dos ativos selecionados para a demo (manifesto abaixo).
2. Períodos e frequências previamente definidos.
3. Indicadores técnicos calculados ou recalculados localmente.
4. Métricas de risco e retorno.
5. Sazonalidade por anos e períodos (incluindo recorte e janela).
6. Comparação entre ativos (incluindo sazonalidade comparada e tendência).
7. Simulação histórica.
8. Textos educativos fixos ("Como ler este gráfico", glossário, avisos).
9. Explicações de gráficos sem chamada à LLM quando não houver internet.
10. Respostas de LLM previamente geradas, **validadas** e salvas, quando aplicável.
11. **Bloqueio de chamadas externas** no modo demo.
12. **Aviso visível** de que a versão está congelada e usa dados salvos.

### 2.2 Comportamento esperado

```text
ARGOS_DEMO_MODE=true
        ↓ Não consultar o Yahoo Finance
        ↓ Carregar datasets locais (manifesto da demo)
        ↓ Executar cálculos localmente (core/)
        ↓ Usar respostas de LLM salvas e validadas, se disponíveis
        ↓ Usar textos educativos fixos como reserva
```

### 2.3 Desenho proposto [S]

| Item | Proposta |
| --- | --- |
| Conjunto de dados | 5 ativos (tabela abaixo), 5 anos até a data da coleta, frequência diária; semanal e mensal derivadas localmente |
| Formato | CSV por ativo em `data/demo/` (sem dependência extra; Parquet exigiria `pyarrow` e mais memória) |
| Manifesto | `data/demo/manifest.json`: ativos, período, frequência, data da coleta, fonte, versão do Argos e **hash SHA-256** de cada arquivo |
| Gerador | `scripts/gerar_dados_demo.py` (baixa uma vez, com internet, e grava arquivos + manifesto) |
| Ativação | Variável de ambiente `ARGOS_DEMO_MODE=true`; `core/data_loader.py` passa a ler de `data/demo/` e **nunca** chama o Yahoo Finance nesse modo |
| Ativos fora do manifesto | Mensagem clara ("disponível apenas fora do modo de demonstração"); digitação livre de ticker desabilitada no modo demo |
| Aviso na tela | Faixa discreta em todas as páginas: "Versão congelada vX · dados salvos em dd/mm/aaaa" |
| Respostas de LLM salvas | `data/demo/llm_respostas.json`: para cada análise da demo, texto aprovado, modelo, versão do prompt, data e resultado das validações; usadas antes de qualquer chamada. Sem resposta salva ou sem API, exibe o roteiro fixo de `core/chart_guides.py` |
| Chamadas externas | Auditoria do código por qualquer acesso à rede (download de dados, logos remotos, fontes e CSS externos, API de LLM); no modo demo, ou são substituídas por recursos locais ou ficam desligadas |
| Cache | `st.cache_data` com `ttl` e `max_entries`; carregar só os ativos do manifesto; não manter DataFrames grandes em `st.session_state` |

Ativos propostos para o manifesto (ajustar):

| Ativo | Classe | Para que serve |
| --- | --- | --- |
| `BTC-USD` (Bitcoin) | Criptomoeda | Sazonalidade por anos e janela (setembro → outubro) |
| `AAPL` (Apple) | Ação dos EUA | Indicadores técnicos; comparação |
| `PETR4.SA` (Petrobras PN) | Ação do Brasil | Moeda diferente (BRL) |
| `^GSPC` (S&P 500) | Índice | Comparação, tendência e simulação |
| `GC=F` (Ouro) | Commodity | Comparação entre classes; nota de contratos futuros |

**Licença dos dados.** Se os CSV forem para um repositório público, conferir os termos de uso do Yahoo Finance quanto à redistribuição [S]. Alternativa: manter `data/demo/` fora do repositório público e distribuí-lo no pacote da demonstração local.

### 2.3.1 Estado da implementação (10/10/2026)

| Item | Estado |
| --- | --- |
| `core/demo_mode.py` (ambiente, manifesto, hash, leitura diária/semanal/mensal, respostas salvas, aviso) | Implementado e testado |
| `core/data_loader.py` (rota local no modo demo, cache com `max_entries`) | Implementado e testado |
| `core/assets_logos.py` (sem imagens remotas no modo demo) | Implementado e testado |
| `app/ui/demo_banner.py` + `app/main.py` (aviso de versão congelada) | Implementado e conferido no navegador |
| `scripts/gerar_dados_demo.py` | Implementado; executado em 10/10/2026 |
| `data/demo/` (CSV, manifesto) | Gerado em 10/10/2026; **fora do Git** por ora (termos do Yahoo); cópia em .zip |
| Respostas de LLM salvas e validadas | Pendente (dependem da 7A/7B); sem elas, texto fixo |
| Auditoria de recursos remotos nas páginas | Teste automatizado passando (518 testes, `core/` a 100%) |
| Execução sem internet | **Concluída em 10/10/2026**, sem falhas |
| Teste de memória (Streamlit Cloud) | Pendente |

### 2.4 Critério de aceite (condição para congelar)

O congelamento só ocorre quando:

```text
[ ] O modo demo está implementado
[ ] A aplicação abre e executa todas as análises da demo sem internet
[ ] Nenhuma chamada externa é necessária nos fluxos principais
[ ] Os datasets estão versionados ou incluídos no pacote de demonstração (com hash no manifesto)
[ ] As respostas de LLM salvas estão validadas (quando houver 7B)
[ ] O fallback de texto fixo funciona
[ ] O aviso de versão congelada aparece na interface
[ ] Um teste automatizado valida o modo demo
[ ] A demonstração foi executada uma vez com a internet desativada
```

**Teste automatizado sugerido.** Com `ARGOS_DEMO_MODE=true`, bloquear o acesso à rede (por exemplo, substituindo a conexão de socket por uma função que levanta erro) e verificar que o carregamento de cada ativo do manifesto, o cálculo e a escolha do texto de reserva funcionam; verificar também que, com o modo desligado, o comportamento atual se mantém e que o hash dos arquivos confere com o manifesto.

## 3. Roteiro do screencast (até 5 min)

| Tempo | Conteúdo | Mensagem |
| --- | --- | --- |
| 0:00–0:30 | Problema e posicionamento: ferramenta de pesquisa e educação, sem recomendação nem previsão | Quem é o público e o que a ferramenta não faz |
| 0:30–1:15 | Dados: catálogo, fonte, período efetivo, aviso de disponibilidade e de versão congelada | Coleta e qualidade (relevante para o SBBD) |
| 1:15–2:15 | Análise Individual: mapa de calor, média por mês, **recorte por anos** e janela setembro → outubro | Média histórica × ano específico |
| 2:15–3:00 | Comparação: Base 100, sazonalidade comparada, tendência histórica | Comparar sem ranking |
| 3:00–3:30 | Simulação histórica | "O que teria ocorrido", com o aviso obrigatório |
| 3:30–4:15 | Educação: "Como ler este gráfico"; "Explicar esta análise" (resposta salva e validada, se aprovada) | Texto fixo e explicação auditável |
| 4:15–5:00 | Rigor e reprodutibilidade: testes, cobertura, metodologia, versão congelada | Confiabilidade |

Regras: gravar da tag congelada, no modo demo; resolução legível; sem dados pessoais; sem mostrar chaves; narração em português (ou legenda).

## 4. Publicação no Streamlit Community Cloud

A versão pública poderá ser publicada como **complemento** à demonstração. Antes da publicação, devem ser verificados e mitigados os limites da plataforma (memória, armazenamento, hibernação) e a dependência de serviços externos. A aplicação será configurada em **modo de demonstração**, com datasets locais congelados e respostas previamente validadas para as explicações assistidas (sem chamada ao modelo na versão pública, conforme N22). A demonstração ao vivo **não dependerá exclusivamente** do Streamlit Community Cloud, da internet do local do evento nem de chamadas externas a provedores de dados ou de modelos.

### 4.1 Limites informados (N24) [S]

Valores aproximados, datados de fevereiro de 2024 e sujeitos a alteração sem aviso; **reconferir na documentação oficial antes de publicar**.

| Item | Limite / comportamento | Impacto no Argos |
| --- | --- | --- |
| CPU | cerca de 0,078 núcleo mínimo e 2 núcleos máximo | Suficiente para cálculos leves; evitar processamento pesado na demo |
| Memória | cerca de 690 MB mínimo e 2,7 GB máximo | Principal risco: limitar datasets, gráficos e cache |
| Armazenamento | até 50 GB | Suficiente para os datasets da demo |
| Atualizações pelo GitHub | até 5 por minuto | Não afeta a demo |
| Inatividade | hibernação após 12 horas sem tráfego | A primeira abertura depois pode demorar |
| Região | Estados Unidos | Latência maior a partir do Brasil |
| Apps privados | um por conta | Publicar como app público, se o repositório for público |

### 4.2 Ajustes antes de publicar

1. **Reduzir memória:** carregar só os ativos da demo, com datasets já filtrados para o período; `st.cache_data` com `ttl` e `max_entries`; não carregar todos os ativos na inicialização; não manter DataFrames grandes em `st.session_state`; liberar objetos grandes após o uso; `requirements.txt` mínimo e versionado.
2. **Usar dados salvos:** `ARGOS_DEMO_MODE=true`, arquivos locais, ativos e período do manifesto, respostas de LLM salvas e textos fixos como reserva, sem chamadas externas desnecessárias.
3. **Controlar a LLM:** nunca chamar ao abrir a página; exigir clique em "Explicar esta análise"; priorizar respostas salvas; limites por sessão, navegador e global; tempo limite de 20 s e no máximo duas novas tentativas; texto fixo se a API falhar; chave somente no gerenciador de segredos do serviço, nunca no repositório (`docs/llm_7b_especificacao.md`).
4. **Evitar hibernação na demo:** abrir o link público no dia, antes da sessão, e confirmar que carregou; não depender do público para "acordar" o app.

### 4.3 Configuração recomendada

```text
Repositório GitHub: público (conferir a licença dos dados, seção 2.3)
App Streamlit: público
Modo demo: ativado
Dados: datasets locais congelados
LLM: respostas salvas primeiro; API apenas se habilitada
Cache: habilitado, com ttl e limite de entradas
Dependências: requirements.txt mínimo e versionado
Segredos: somente no painel do serviço
Backup da demo: repositório local + vídeo gravado
```

### 4.4 Publicar somente depois de

```text
[ ] Modo demo com dados salvos implementado
[ ] Demo testada com a internet desativada
[ ] Consumo de memória reduzido e testado
[ ] Cache configurado com ttl e limite de entradas
[ ] Segredos configurados no painel, sem chave no Git
[ ] Vídeo de até 5 minutos preparado
[ ] Aplicação validada após hibernação
[ ] Versão congelada registrada (docs/versao_congelada.md)
```

## 5. Plano de contingência no dia

1. Internet ou fontes de dados fora do ar: seguir no computador local com `ARGOS_DEMO_MODE=true` (camada 1).
2. Computador com problema: exibir o screencast (camada 2).
3. Sem máquina própria: abrir a versão pública (camada 3), depois de confirmá-la no próprio dia.
4. Ter o PDF do artigo e o vídeo em duas mídias.

## 6. Enquadramento para o SBBD

O evento é de **bancos de dados**. A demonstração deve destacar: coleta e catálogo de ativos, tratamento e validação de qualidade, disponibilidade de dados, métricas reprodutíveis e testadas, e a camada de interpretação auditável, além da análise financeira. O artigo (até 6 páginas, contando referências) precisa de decisão precoce sobre o que mostrar; a chamada oficial deve ser conferida quando for publicada.