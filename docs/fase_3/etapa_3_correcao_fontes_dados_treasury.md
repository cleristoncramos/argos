Fase 3 - Etapa 3: Correção de Fontes de Dados de Taxas de Juros (Treasuries)
🎯 Objetivo
Garantir a estabilidade e a continuidade do fluxo de dados da aplicação, corrigindo falhas recorrentes no carregamento do histórico de taxas de juros americanas (Treasuries) de curto prazo. A correção precisava ser feita sem alterar o tamanho e a estrutura do catálogo central de ativos para manter a integridade dos testes e validações.

🛠️ Mudanças Realizadas
1. Identificação do Bloqueio na API (Yahoo Finance)
Durante os testes de integração e o uso do sistema, foi constatado um erro crítico (lançando a mensagem "Não foi possível carregar dados para o ativo...") ao tentar analisar os ativos ^US1Y, ^US3M e ^US2Y.

Causa Raiz: A biblioteca yfinance e a API pública do Yahoo Finance não fornecem um histórico de dados limpo, confiável e contínuo para esses índices brutos de curto e médio prazo do Tesouro Americano. O retorno vazio (None ou DataFrame vazio) quebrava o pipeline de processamento do módulo core.data_loader.

2. Substituição Estratégica por ETFs de Renda Fixa
Como o mercado financeiro muitas vezes utiliza fundos negociados em bolsa (ETFs) como proxies (representações fidedignas) para acompanhar a curva de juros, os índices problemáticos foram mapeados e substituídos por ETFs equivalentes de altíssima liquidez.

Implementação no arquivo core/assets.py:

^US3M (3 Meses) ➡️ Substituído por BIL (SPDR Bloomberg 1-3 Month T-Bill ETF). Representa de forma confiável as letras do tesouro de 1 a 3 meses.

^US1Y (1 Ano) ➡️ Substituído por SHV (iShares Short Treasury Bond ETF). Acompanha títulos de prazos curtíssimos, até 1 ano.

^US2Y (2 Anos) ➡️ Substituído por VGSH (Vanguard Short-Term Treasury ETF). Captura com exatidão a variação dos Treasuries na faixa de 1 a 3 anos.

3. Preservação da Integridade do Catálogo (validate_catalog)
O sistema possui uma função estrita de validação (validate_catalog()) que obriga o catálogo a ter exatamente 120 ativos listados, com campos obrigatórios preenchidos e sem tickers duplicados.

Abordagem: Ao invés de simplesmente excluir os ativos defeituosos — o que quebraria a validação do sistema —, optou-se pela substituição "um para um".

As nomenclaturas e descrições também foram atualizadas (ex: de "Treasury 2 Years" para "Treasury 1-3 Anos (VGSH)") para garantir total transparência ao usuário final.

📈 Impacto no Projeto
Prevenção de Quebras (Crash Prevention): A página de Análise Individual e Risco e Retorno voltou a funcionar perfeitamente para todos os ativos listados na classe "Renda Fixa / Treasuries", eliminando mensagens de erro na interface.

Confiabilidade de Dados: A utilização de ETFs reais (com cotas negociadas e histórico robusto) melhora a qualidade da análise estatística, uma vez que não há lacunas (missing values) na série histórica desses fundos no Yahoo Finance.

Manutenção da Governança de Código: A substituição estratégica evitou a necessidade de reescrever as regras de validação do módulo central de ativos (assets.py), preservando as travas de segurança do projeto.