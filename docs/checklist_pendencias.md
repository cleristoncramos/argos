# Checklist de Pendências — Pós-Reunião 30/09/2026

Lista consolidada das deliberações da reunião com o orientador, organizada por prioridade e fase de execução. Ver `docs/ata_reuniao_2026-10-06.md` para o contexto completo.

## Como usar este checklist

- Cada item deve ser marcado `[x]` quando implementado **e** validado (não apenas codificado).
- Itens de "Prioridade alta" bloqueiam o avanço para as fases seguintes do plano de trabalho.
- Mudanças de escopo devem ser registradas como adendo a este arquivo, não como edição silenciosa.

---

## Prioridade alta

- [ ] Definir escopo acadêmico e pergunta de pesquisa (rascunho em `ata_reuniao_2026-10-06.md`, pendente validação formal com o orientador)
- [ ] Adicionar explicações educativas às métricas de risco (Fase 2)
- [ ] Revisar e documentar indicadores técnicos (Fase 3)
- [ ] Melhorar mensagens sobre histórico disponível (Fase 5)
- [ ] Separar claramente análise histórica de recomendação (Fase 1, transversal)
- [ ] Corrigir e documentar a seleção de ativos (Fase 0/5)
- [ ] Validar todos os fluxos atuais após alterações (Fase 8, contínuo)
- [ ] Implementar e validar digitação livre de ticker (ver Seção 2)

## Prioridade média

- [ ] Reutilizar cards de destaque na comparação (Fase 6)
- [ ] Criar glossário educativo (Fase 1/4)
- [ ] Criar simulação histórica de aportes (Fase 7)
- [ ] Melhorar tabelas e tooltips (Fase 4)
- [ ] Consolidar componentes visuais (Fase 4)
- [ ] Adicionar metadados nos gráficos (Fase 5/6)

## Prioridade baixa

- [ ] Revisar nome "Argos DataLab" (Fase 10)
- [ ] Refinar identidade visual (Fase 10)
- [ ] Adicionar mais classes e ativos (Fase 10)
- [ ] Criar modelos avançados de previsão (fora do escopo atual)
- [ ] Integrar dados fundamentais, sentimento ou on-chain (fora do escopo atual)
- [ ] Expandir para recomendação personalizada — **não recomendado nesta fase**

---

## Detalhamento por seção da ata

### 1. Direcionamento geral
- [ ] Registrar no projeto que as funcionalidades atuais são um protótipo evolutivo
- [ ] Definir nome/identidade visual somente após nova conversa com o orientador

### 2. Seleção e catálogo de ativos
- [ ] Exibir nome amigável, ticker e descrição em toda seleção de ativo
- [x] Confirmar se as 13 classes são necessárias para a primeira versão → **confirmado: manter as 13**
- [ ] Documentar o critério usado para escolher os ativos do catálogo
- [ ] Registrar que a seleção atual é amostra inicial, não o universo do mercado
- [x] Avaliar digitação opcional de ticker para usuários avançados → **decidido: incluir nesta fase**
- [ ] Implementar campo de digitação livre de ticker (modo alternativo à seleção hierárquica)
- [ ] Validar ticker digitado contra o yfinance antes de prosseguir
- [ ] Exibir mensagem de erro clara quando o ticker não existir ou não retornar dados
- [ ] Manter seleção hierárquica como fluxo principal/padrão para iniciantes

### 3. Período e frequência
- [ ] Informar quando o ativo não possui histórico suficiente
- [ ] Não sugerir que "10 anos" garante dez anos de dados reais
- [ ] Exibir período efetivamente utilizado após a consulta
- [ ] Exibir quantidade real de observações
- [ ] Diferenciar "período solicitado" de "período disponível"
- [ ] Documentar que criptos e ativos recentes podem ter histórico menor
- [ ] Tratar corretamente ativos com datas de início diferentes

### 4. Análise Individual
- [ ] Exibir fonte dos dados e data da última atualização
- [ ] Mensagem quando houver dados insuficientes
- [ ] Indicar que lacunas podem vir de indisponibilidade do ativo
- [ ] Revisar fallback de logos (URL indisponível → emoji)
- [ ] Confirmar rótulo "anualizada" na volatilidade
- [ ] Explicação curta do mapa de calor de sazonalidade
- [ ] Diferenciar retorno mensal de valorização acumulada
- [ ] Tooltip com unidade, período e interpretação

### 5. Indicadores técnicos
- [ ] Revisar todos os indicadores hoje disponíveis
- [ ] Reduzir ao conjunto priorizado (ver ata)
- [ ] Descrição simples por indicador
- [ ] Fórmula/lógica de cálculo por indicador
- [ ] O que o indicador mede
- [ ] Limitações do indicador
- [ ] Não apresentar indicador como sinal automático de compra/venda
- [ ] Separar visualização de geração de sinal
- [ ] Avaliar uso futuro como variável preditiva
- [ ] Criar tabela de features para modelos futuros
- [ ] Documentar parâmetros (janelas, períodos)
- [ ] Auditar vazamento de informação futura (look-ahead bias)
- [ ] Testes unitários por indicador

### 6. Indicadores e modelos futuros
- [ ] Criar camada separada para features
- [ ] Não misturar visualização, sinal e variável preditiva
- [ ] Definir indicadores de entrada dos modelos
- [ ] Definir horizonte de previsão
- [ ] Definir alvo (retorno, direção, volatilidade)
- [ ] Priorizar modelos simples e benchmarks antes de complexos
- [ ] Validação temporal (treino/validação/teste)
- [ ] Não confundir acurácia com rentabilidade

### 7-8. Risco/Retorno e Educação Financeira
- [ ] Exibir data do pior drawdown
- [ ] Texto explicativo por métrica (textos prontos na ata)
- [ ] Indicar se maior/menor é desejável, com ressalva de contexto
- [ ] Exibir unidades (%, R$/US$, índice)
- [ ] Explicar taxa livre de risco e fator de anualização
- [ ] Indicar limitações de cada métrica
- [ ] Criar glossário (retorno, volatilidade, drawdown, Sharpe, correlação, médias móveis, RSI, MACD, Base 100, sazonalidade)
- [ ] Separar informação histórica / interpretação estatística / simulação / recomendação
- [ ] Eliminar linguagem tipo "compre aqui"/"venda aqui"
- [ ] Aviso de que a ferramenta não avalia perfil individual

### 9. Simulação de aportes
- [ ] Simulação de aporte hipotético (não personalizado ao perfil real)
- [ ] Cenários positivo, negativo, neutro
- [ ] Comparar aporte único vs. periódico
- [ ] Disclaimer de simulação histórica (texto pronto na ata)
- [ ] Nunca declarar ativo "barato" ou "caro"

### 10. Comparação de ativos
- [ ] Avaliar cards de destaque reaproveitados da Análise Individual
- [ ] Exibir metadados dos ativos comparados
- [ ] Avisar sobre períodos históricos divergentes entre ativos
- [ ] Evitar comparação direta com frequências incompatíveis sem explicação

### 11. Interface
- [ ] Padronizar títulos e subtítulos
- [ ] Reduzir poluição visual
- [ ] Evitar DataFrames brutos sem interpretação
- [ ] Padronizar cores (retorno positivo/negativo) e casas decimais
- [ ] Melhorar responsividade da sidebar

### 12. Componentização
- [ ] Card de métrica reutilizável
- [ ] Componente de explicação educativa reutilizável
- [ ] Seleção de ativos unificada entre páginas
- [ ] Seletor de período/frequência unificado
- [ ] Componente de tabela padrão
- [ ] Componente de aviso metodológico
- [ ] Cálculos em `core/`, renderização em `app/`

### 13. Documentação técnica
- [ ] Arquitetura do sistema
- [ ] Catálogo de ativos
- [ ] Fontes de dados
- [ ] Tratamento de dados
- [ ] Cálculo de indicadores
- [ ] Cálculo de risco
- [ ] Limitações do yfinance
- [ ] Ativos sem histórico completo
- [ ] Tratamento de dados ausentes
- [ ] Decisões sobre frequência
- [ ] Hipóteses para previsão futura
- [ ] Reforço de que histórico não é previsão

### 14. Validação acadêmica
- [ ] Revisão teórica sobre análise técnica
- [ ] Relacionar indicadores a métodos de análise de dados
- [ ] Formalizar pergunta de pesquisa (rascunho pronto, falta validar)
- [ ] Definir hipóteses, variáveis-alvo, benchmarks
- [ ] Protocolo de validação temporal
- [ ] Registrar limitações e resultados negativos
- [ ] Relatório metodológico para o orientador

### 15. Qualidade e testes
- [ ] Testes para novos indicadores
- [ ] Testes para catálogo de ativos
- [ ] Testes para logos e fallbacks
- [ ] Testes para dados insuficientes
- [ ] Testes para ativos sem histórico completo
- [ ] Testes para filtros sem resultado
- [ ] Testes para exportação CSV
- [ ] Testes para validação de datas
- [ ] Manter cobertura ≥ 80% (meta), preservar ~95% (atual)