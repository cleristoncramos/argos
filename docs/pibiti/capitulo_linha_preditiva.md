# Linha preditiva do Argos DataLab: um resultado negativo documentado

**Situação:** rascunho para o relatório do PIBITI ou para um texto curto de evento de iniciação científica · redigido em 08/11/2026 só a partir dos documentos do repositório · **não submeter antes de resolver as pendências do fim**

Convenção: cada número é seguido da fonte entre colchetes, com o caminho do artefato no repositório. "Desenvolvimento" são as dobras de 2014 a 2021; "período final" é o bloco reservado do 21º pregão de 2022 a 30/10/2026.

---

## 1. Pergunta e motivação

O Argos DataLab foi construído como ferramenta de análise histórica de ativos para pessoas sem formação em finanças. Em 07/11/2026, a proposta de reformulação pediu que se investigasse uma camada preditiva, sem dar por certo que ela funcionaria [`docs/plano_reformulacao_preditiva.md`, seção 1]. A pergunta do piloto foi delimitada assim:

> Indicadores técnicos calculados até a data `t` acrescentam informação sobre o retorno dos 20 pregões seguintes, em relação a referências simples?

O plano tratou um modelo que não supere a referência como resultado científico válido, desde que documentado [`docs/plano_reformulacao_preditiva.md`, seção 1.1]. Este texto relata justamente esse caso.

## 2. Método

O desenho foi fixado num protocolo registrado antes de qualquer teste e aprovado pelo orientador [`docs/preditivo/protocolo_piloto_v1.md`; `docs/pibiti/decisoes_orientador.md`, entrada R6–R8].

- **Ativos:** PETR4.SA e VALE3.SA, avaliados separadamente [protocolo v1, seção 1].
- **Alvo:** o retorno entre a entrada e a saída de uma posição simulada, `y_t = P(t+21)/P(t+1) − 1`, com horizonte de 20 intervalos entre observações [protocolo v1, seção 2].
- **Validação temporal:**
  - oito dobras anuais de validação, de 2014 a 2021, com janela de treino expansível [protocolo v1, seção 6.1];
  - em cada fronteira, embargo de 20 pregões e expurgo das amostras cujo alvo termina depois da primeira data avaliada, nas divisões externas e internas [protocolo v1, seção 6.2].
- **Período final:** reservado para uma única avaliação do procedimento congelado [protocolo v1, seção 6.3].
- **Modelo e referências:** regressão Ridge com variáveis padronizadas no treino e regularização (`alpha`) escolhida por três validações internas anuais. As referências são o retorno zero e a média histórica expansiva, calculada só com alvos já realizados [protocolo v1, seção 7].
- **Estratégia:** ficar exposto quando a previsão superasse `c = 0,002`, ou em caixa remunerado pelo CDI. O custo é de 0,10% por lado, com sensibilidade de 0 a 0,30% [protocolo v1, seção 8].
- **Teste estatístico:** Diebold-Mariano unilateral, com variância de Newey-West de 19 defasagens, `p < 0,10` estrito e mínimo de 200 datas. O teste foi tratado como filtro exploratório previamente especificado, sem pressupor taxa exata de falso positivo [`docs/preditivo/nota_teste_estatistico.md`, decisões N1 a N5].
- **Critérios cumulativos de elegibilidade:**
  1. ganho preditivo;
  2. comparação estatística;
  3. estabilidade (R² fora da amostra positivo em pelo menos 5 das 8 dobras);
  4. resultado econômico;
  5. robustez ao custo em dobro.

  [protocolo v1, seção 9.3]

## 3. Cuidado com os dados

Os dados foram coletados uma vez e congelados com manifesto e hashes SHA-256. O snapshot `snap-20261108-01` tem 4.679 pregões por ativo e 4.731 dias de CDI, de 02/01/2008 a 30/10/2026, sem datas repetidas nem valores não finitos [`docs/preditivo/snapshot_snap-20261108-01.md`, seção 3].

As verificações de integridade encontraram:
- um fechamento da PETR4 fora da faixa entre mínima e máxima, em 02/04/2014;
- duas ocorrências na VALE3, em 2012, atribuídas primeiro à abertura; a conferência mostrou que a divergência estava na máxima e na mínima.

Os valores da fonte foram conferidos com a série histórica oficial da B3 (COTAHIST). A conferência confirmou divergências em quatro campos de três datas; o fechamento da PETR4 em 02/04/2014, por exemplo, era 15,56 na fonte e 16,56 na B3 [snapshot, seções 6 e 7.1].

Com a decisão P1, os valores da B3 substituíram os divergentes só na visão derivada usada pelos modelos, sem alterar o snapshot original [`docs/pibiti/decisoes_orientador.md`, entrada P1; `experiments/preditivo/politica_qualidade.json`].

Como o fator de ajuste por proventos da PETR4 dependia do fechamento corrigido, ele foi reconstruído pelo método multiplicativo. Nas datas afetadas, o método reproduziu o fator da fonte com diferença relativa máxima de 5,6 × 10⁻⁷ [snapshot, seção 7.2]. O impacto medido, sem nenhum modelo, foi de zero amostras invalidadas, 308 amostras com valores alterados na PETR4 e 213 na VALE3 [snapshot, seção 7.3].

Uma limitação continua registrada: na VALE3, o mesmo método não reproduz o ajuste da fonte em 2008 e 2009, com diferença de até 6,7% [snapshot, seção 7.2; `docs/preditivo/encerramento_v1.md`, seção 4].

## 4. Resultado da v1

No desenvolvimento oficial, o R² fora da amostra foi positivo em 3 das 8 dobras nos dois ativos:
- PETR4: 2015, 2020 e 2021;
- VALE3: 2018, 2019 e 2020.

O mínimo exigido era 5 [`docs/preditivo/desenvolvimento_oficial_v1.md`, seção 3]. O R² por dobra foi de −0,6590 a +0,1315 na PETR4 e de −0,2195 a +0,1326 na VALE3 [idem, seção 2].

Como os critérios são cumulativos, a falha no critério 3 impedia a habilitação do sinal, qualquer que fosse o resultado no período final. O orientador encerrou a v1 sem abrir a avaliação final [`docs/pibiti/decisoes_orientador.md`, entrada D1; `docs/preditivo/encerramento_v1.md`, seção 1].

Um detalhe do desenvolvimento motivou a etapa seguinte: `alpha` = 1000, o maior valor da grade, foi escolhido em 7 das 8 dobras de cada ativo. Nesses ajustes, o erro interno ainda era menor que com `alpha` = 100 [`docs/preditivo/desenvolvimento_oficial_v1.md`, seção 4; `docs/preditivo/proposta_piloto_v2.md`, seção 1]. A escolha não foi tratada como previsão nula: as previsões variaram entre as datas [encerramento v1, seção 2].

## 5. Resultado da v2

A v2 foi uma hipótese nova, derivada dos resultados da v1: investigar se uma grade mais ampla de regularização permitiria ganho preditivo estável em relação ao retorno zero e à média histórica, mantendo os demais elementos [`docs/preditivo/protocolo_piloto_v2.md`, seção 1].

A única mudança de modelagem foi a grade, ampliada até 10⁶ com limite fixo [protocolo v2, seção 3]. Antes dos testes, foi acrescentado um sexto critério, obrigatório: R² positivo em relação à média histórica expansiva, no período final e em pelo menos 5 das 8 dobras. Ele servia para impedir que uma previsão quase constante fosse lida como contribuição das variáveis [protocolo v2, seção 6].

O desenvolvimento da v2 não é evidência independente: as mesmas dobras da v1 foram reutilizadas, e a proposta foi motivada por elas [protocolo v2, seção 8].

Antes dos resultados, a v2 restrita à grade antiga reproduziu as previsões oficiais da v1, com diferença máxima de 9,99 × 10⁻¹⁷ [`docs/preditivo/desenvolvimento_oficial_v2.md`, seção 1].

| Ativo | Critério 3 (contra retorno zero) | Critério 6 nas dobras (contra média histórica) | Situação |
| --- | --- | --- | --- |
| PETR4.SA | 6 de 8 | 5 de 8 | Filtros atendidos |
| VALE3.SA | 4 de 8 | 3 de 8 | Filtros não atendidos |

[`docs/preditivo/desenvolvimento_oficial_v2.md`, seção 3]

O limite superior de 10⁶ foi escolhido em 11 dos 16 ajustes. Nessas dobras, as previsões ficaram praticamente constantes dentro de cada ano: o desvio-padrão foi de 0,0001 a 0,0010, com média a no máximo 0,0004 da média do alvo no treino [idem, seção 4].

Uma análise exploratória posterior, não prevista no protocolo e calculada só sobre o desenvolvimento, comparou a média histórica com uma previsão constante igual à média do alvo no treino, sem nenhuma variável. Na PETR4, essa constante superou a média histórica em 7 das 8 dobras; a Ridge, em 5. A Ridge superou a constante em 2 dobras [idem, seção 5; `experiments/preditivo/resultados/v2/diagnostico_exploratorio_constante_treino.json`, fora do Git, SHA-256 em `experiments/preditivo/encerramento_v2.json`].

Essa análise não é um critério e não muda o registro dos filtros, que continuam atendidos. Ela mostra que a comparação com a média histórica mistura dois efeitos:
- o uso dos indicadores;
- a diferença entre a média do treino, constante durante o ano, e a média histórica, atualizada a cada data.

Por isso, o orientador não autorizou a abertura do período final para a PETR4 (decisão de não progressão) e encerrou a VALE3 pela regra V2-7 [`docs/pibiti/decisoes_orientador.md`, entrada DV2; `docs/preditivo/encerramento_v2.md`].

## 6. Integridade do desenho

- **Período final nas duas versões:** continua "ainda não utilizado para avaliação preditiva ou seleção de modelos". Os arquivos foram acessados para coleta, verificações de integridade e reconstrução do fator de ajuste, mas nenhuma previsão, alvo avaliado ou métrica do período foi produzida [encerramento v1, seção 3; encerramento v2, seção 5].
- **Travas no código:** o código recusa a avaliação final das duas versões, e as condições de abertura registradas estão em 0 cumpridas [`experiments/preditivo/encerramento_v1.json`; `experiments/preditivo/encerramento_v2.json`].
- **Previsões e sinais:** nenhuma previsão foi publicada e nenhum sinal foi habilitado no aplicativo [encerramento v2, seção 2].
- **Desvios documentados:** a árvore de trabalho estava alterada só por um documento sem relação com o piloto [`docs/preditivo/evidencias/arvore_coleta_snap-20261108-01.md`]. Uma correção de infraestrutura veio depois do congelamento da v2 e antes dos resultados, separada do congelamento [encerramento v2, seção 4].

## 7. Discussão

Três lições se apoiam nos registros.

**Regularização.** Nas duas versões, a validação interna preferiu regularização forte. Na v2, sem o teto anterior, a Ridge convergiu para uma previsão praticamente constante na maior parte das dobras (seção 5). Isso é compatível com a hipótese de que as variáveis acrescentaram pouca informação estável nesta configuração. Não demonstra que sejam inúteis, nem vale para outros modelos, ativos ou horizontes.

**Escolha da referência.** O critério 6 foi criado para separar o efeito das variáveis do efeito de uma previsão quase constante. A análise exploratória indicou que a média histórica expansiva não faz essa separação: uma referência com outra regra de atualização pode ser superada sem nenhum indicador. A lição metodológica é que a referência precisa compartilhar o máximo possível do procedimento do candidato, para que a diferença medida seja atribuível ao que se quer testar.

**Disciplina de protocolo.** O que torna o resultado negativo informativo é a ordem dos passos:
- critérios fixados antes dos testes;
- dados congelados com hashes;
- divergências tratadas por decisão registrada, sem consultar o desempenho;
- período final preservado;
- encerramento formal das duas versões.

Sem esses registros, seria difícil distinguir "não houve evidência" de "a evidência foi procurada até aparecer".

## 8. Limitações e trabalho futuro

**Limitações:**
- dois ativos;
- um horizonte;
- um modelo linear;
- base ajustada reconstruída pela fonte na data da coleta, com a divergência da VALE3 em 2008–2009;
- desenvolvimento da v2 sem independência em relação à v1;
- teste estatístico tratado como filtro exploratório.

[protocolo v1, seção 3; nota metodológica, N4; protocolo v2, seção 8]

**Trabalho futuro**, só como hipóteses, sem autorização de experimento:
- **Referência sem variáveis:** comparar a Ridge com uma referência sem variáveis construída sobre a mesma amostra de treino, com o mesmo calendário de reestimação, as mesmas datas e as mesmas restrições de disponibilidade de alvos. Isso mediria outra coisa que o critério 6: separaria o efeito dos indicadores do efeito da atualização da média [encerramento v2, seção 7].
- **Dados posteriores ao corte:** avaliar uma versão futura em dados posteriores a 30/10/2026, prospectivamente, como prevê o protocolo v1 [protocolo v1, seção 11].

---

## Pendências antes de submeter

| # | O que confirmar | Quem |
| --- | --- | --- |
| 1 | Formato e limite de páginas do relatório do PIBITI ou do evento; se este texto vira capítulo ou resumo expandido | Autor, com o orientador |
| 2 | Se a linha preditiva entra no relatório parcial ou final, e com qual enquadramento da pergunta de pesquisa (R5 ainda pendente no plano) | Orientador |
| 3 | Arquivamento das mensagens originais citadas como decisões (R6–R8, N1–N5, snapshot, P1, D1, V2, confirmação, DV2), conforme `docs/pibiti/indice_mensagens_orientador.md` | Autor |
| 4 | Se é possível citar a análise exploratória da constante, e com que redação, no texto submetido | Orientador |
| 5 | Referências bibliográficas: o texto não cita literatura. A nota metodológica tem referências (`docs/preditivo/nota_teste_estatistico.md`, seção "Referências") que podem ser aproveitadas, mas a lista final precisa ser escolhida e conferida | Autor |
| 6 | Conferir no relatório de origem cada número citado, antes da versão final; nenhum foi recalculado para este texto | Autor |
| 7 | Créditos e autoria do texto, e menção à orientação | Autor, com o orientador |
