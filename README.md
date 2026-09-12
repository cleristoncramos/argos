📊 Argos DataLab
Plataforma web para análise exploratória de ativos financeiros, comparação de desempenho, indicadores técnicos e métricas de risco. O projeto foi desenvolvido com foco educacional e de pesquisa no contexto do PIBITI UFPI 2026–2027.
Aviso importante: o Argos DataLab tem finalidade exclusivamente acadêmica, educacional e de desenvolvimento tecnológico. As informações, métricas e visualizações apresentadas não constituem recomendação, indicação ou aconselhamento de investimento.

✨ Visão geral
O Argos DataLab permite explorar séries históricas de ativos financeiros e transformar os dados em análises visuais e estatísticas. A plataforma foi desenhada para apoiar pesquisadores, estudantes e entusiastas do mercado financeiro na investigação de comportamento histórico, risco, retorno, correlação e sazonalidade.
Entre as classes de ativos contempladas no catálogo estão, conforme disponibilidade da fonte de dados:
    • Ações.
    • Criptomoedas.
    • Fundos Imobiliários (FIIs).
    • REITs.
    • Commodities.
    • Outros ativos organizados no catálogo interno da aplicação.
Os dados históricos são consultados via Yahoo Finance com o pacote yfinance, tratados localmente e apresentados em uma interface desenvolvida com Streamlit e Plotly.

🚀 Funcionalidades
🔍 Análise individual de ativos
    • Seleção hierárquica de ativos por classe e subclasse.
    • Atalhos de período para 1, 3, 5 e 10 anos.
    • Escolha de intervalo personalizado de datas.
    • Visualização de preços e evolução histórica.
    • Gráfico de volatilidade anualizada por mês.
    • Mapa de calor de sazonalidade dos retornos.
    • Exportação dos dados processados em CSV.
⚖️ Comparação de ativos
    • Comparação simultânea de 2 a 5 ativos.
    • Normalização da evolução histórica em Base 100.
    • Gráficos comparativos de desempenho.
    • Matriz de correlação e heatmap.
    • Resumo comparativo de retorno, volatilidade, drawdown e Sharpe.
📈 Indicadores técnicos
    • Gráficos de fechamento, linhas, barras e candles, quando aplicável.
    • Médias móveis simples e exponenciais: SMA e EMA.
    • Bandas de Bollinger.
    • Índice de Força Relativa: RSI.
    • MACD.
    • Acompanhamento de volume negociado.
⚠️ Risco e retorno
    • Retorno total e retorno médio.
    • Win rate.
    • Volatilidade anualizada.
    • Índice de Sharpe com taxa livre de risco configurável.
    • Drawdown máximo.
    • Data do pior drawdown do período.
    • Distribuição de retornos por faixas percentuais.

🧱 Estrutura do projeto
A estrutura abaixo representa os principais diretórios esperados pela aplicação:
argos/
├── app/
│   ├── main.py                 # Ponto de entrada da aplicação Streamlit
│   └── views/                  # Páginas e módulos de interface
├── core/
│   ├── assets.py               # Catálogo central de ativos
│   ├── ...                     # Regras de negócio, tratamento e análises
├── tests/                      # Suíte de testes automatizados
├── requirements.txt            # Dependências Python
├── README.md                   # Documentação do projeto
└── ...

A organização exata pode evoluir ao longo do projeto. Ao adicionar módulos, mantenha a separação entre interface (app/), regras analíticas e dados (core/) e testes (tests/).

🛠️ Tecnologias
    • Python: linguagem principal.
    • Streamlit: interface web e navegação da aplicação.
    • Plotly: gráficos interativos.
    • pandas: tratamento e análise tabular de dados.
    • NumPy: operações numéricas e estatísticas.
    • yfinance: consulta de dados históricos do Yahoo Finance.
    • pytest: testes automatizados.
    • coverage / pytest-cov: medição de cobertura de testes.

📋 Pré-requisitos
Antes de iniciar, tenha instalado:
    • Python 3.10 ou superior.
    • Git.
    • PowerShell no Windows ou terminal equivalente no macOS/Linux.
Verifique a versão do Python:
python --version


💻 Instalação local
1. Clone o repositório
git clone https://github.com/cleristoncramos/argos.git
cd argos

2. Crie o ambiente virtual
python -m venv venv

3. Ative o ambiente virtual
Windows — PowerShell
.\venv\Scripts\Activate.ps1

Caso o PowerShell bloqueie a execução de scripts, execute uma vez no terminal atual:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Depois, ative novamente:
.\venv\Scripts\Activate.ps1

macOS/Linux
source venv/bin/activate

4. Atualize o pip e instale as dependências
python -m pip install --upgrade pip
python -m pip install -r requirements.txt


▶️ Execução local
Com o ambiente virtual ativado, execute na raiz do projeto:
streamlit run app/main.py

O Streamlit iniciará o servidor local e normalmente abrirá a aplicação no navegador. Caso isso não ocorra, acesse:
http://localhost:8501
Para encerrar o servidor, use Ctrl + C.

📊 Fonte de dados
A aplicação utiliza dados históricos disponibilizados pelo Yahoo Finance por meio do pacote yfinance.
O catálogo de ativos é centralizado em:
core/assets.py

Esse catálogo deve concentrar:
    • Código ou ticker do ativo.
    • Nome de exibição.
    • Classe e subclasse do ativo.
    • Fonte de dados.
    • Regras de validação.
    • Critérios de liquidez e qualidade, quando aplicáveis.
Limitações da fonte
Dados de mercado podem sofrer atrasos, indisponibilidade temporária, alterações de ticker, ajustes históricos ou limitações da fonte externa. Por isso:
    • valide o ticker antes de utilizá-lo em análises;
    • trate falhas de consulta de API de forma controlada;
    • não interprete dados históricos como garantia de desempenho futuro;
    • não utilize a aplicação como ferramenta de recomendação de investimento.

🧪 Testes e cobertura
A suíte automatizada deve validar, no mínimo:
    • Integridade do catálogo de ativos.
    • Tratamento e limpeza de dados históricos.
    • Cálculos de retorno, volatilidade, Sharpe e drawdown.
    • Regras de normalização em Base 100.
    • Transformações para indicadores técnicos.
    • Regras de visualização e componentes críticos, quando aplicável.
Executar os testes
python -m pytest

Executar testes com cobertura
Se o projeto estiver configurado com pytest-cov, execute:
python -m pytest --cov=core --cov-report=term-missing --cov-report=html

A cobertura é medida prioritariamente no diretório core/. A meta mínima configurada no projeto é de 80% de cobertura. O pipeline de integração contínua deve falhar caso a cobertura fique abaixo desse limite.
Abrir o relatório HTML de cobertura
Windows
Start-Process ".\htmlcov\index.html"

macOS
open htmlcov/index.html

Linux
xdg-open htmlcov/index.html


✅ Boas práticas de desenvolvimento
Ao contribuir com o projeto:
    • Crie uma branch para cada funcionalidade ou correção.
    • Mantenha regras de negócio e cálculos em core/, evitando lógica analítica extensa dentro das páginas Streamlit.
    • Adicione ou atualize testes para toda alteração em cálculos, tratamento de dados ou regras críticas.
    • Evite expor tokens, chaves de API ou dados sensíveis no código-fonte.
    • Não faça commits de arquivos locais, ambientes virtuais, relatórios temporários ou credenciais.
    • Execute testes e valide a interface localmente antes de abrir um pull request ou fazer merge.
    • Documente decisões metodológicas que alterem métricas, indicadores ou regras de cálculo.

🌿 Fluxo de desenvolvimento e publicação
O fluxo recomendado é:
Branch feature
→ Desenvolvimento local
→ Testes com pytest
→ Validação local de UX/UI
→ Commit e push
→ Pull request / merge na main
→ Deploy automático

Exemplo de criação de branch:
git checkout -b feature/nome-da-funcionalidade

Antes de enviar alterações:
python -m pytest
git status
git add .
git commit -m "feat: descreve a funcionalidade"
git push origin feature/nome-da-funcionalidade


☁️ Publicação
O deploy é realizado pelo Streamlit Community Cloud por meio da integração com o GitHub.
Configuração esperada:
Repositório: cleristoncramos/argos
Branch de produção: main
Arquivo de entrada: app/main.py

Após o merge na branch main, a plataforma de deploy deve iniciar uma nova publicação automaticamente.
Antes de publicar, confirme:
    • Dependências atualizadas em requirements.txt.
    • Aplicação iniciando localmente com streamlit run app/main.py.
    • Testes passando.
    • Ausência de segredos no repositório.
    • Ausência de arquivos grandes ou temporários indevidos.

🎓 Contexto acadêmico
    • Programa: Iniciação em Desenvolvimento Tecnológico e Inovação — PIBITI UFPI 2026–2027.
    • Plano de Trabalho: Análise de Dados para Apoio à Tomada de Decisão em Investimentos no Mercado Financeiro.
    • Pesquisador discente: Clériston de Castro Ramos.
    • Orientador: Prof. Dr. Arlino Henrique Magalhães de Araújo.
    • Instituição: Universidade Federal do Piauí — UFPI.
    • Curso: Tecnologia em Gestão de Dados.

⚖️ Aviso legal e metodológico
O Argos DataLab é um projeto de pesquisa, ensino e desenvolvimento tecnológico. Dados históricos e indicadores quantitativos são instrumentos para estudo e análise, não previsões ou garantias.
    • Resultados passados não garantem resultados futuros.
    • A plataforma não oferece recomendação de compra, venda ou manutenção de ativos.
    • Nenhuma informação exibida deve substituir análise profissional, avaliação de perfil de risco ou orientação de especialista habilitado.
    • A disponibilidade e a precisão dos dados dependem de fontes externas e podem sofrer variações.

📄 Licença
Projeto desenvolvido para fins educacionais e de pesquisa no âmbito do PIBITI UFPI.
Todos os direitos reservados.