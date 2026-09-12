# 📊 Argos DataLab

**Plataforma web para análise exploratória de ativos financeiros, comparação de desempenho, indicadores técnicos e métricas de risco.**

O **Argos DataLab** foi desenvolvido com foco educacional e de pesquisa no contexto do **PIBITI UFPI 2026–2027**.

> [!IMPORTANT]
> O Argos DataLab tem finalidade **exclusivamente acadêmica, educacional e de desenvolvimento tecnológico**.
>
> As informações, métricas e visualizações apresentadas **não constituem recomendação, indicação ou aconselhamento de investimento**.

---

## ✨ Visão geral

O **Argos DataLab** permite explorar séries históricas de ativos financeiros e transformar os dados em análises visuais e estatísticas.

A plataforma foi desenvolvida para apoiar:

* 🔬 Pesquisadores;
* 🎓 Estudantes;
* 📈 Entusiastas do mercado financeiro;

na investigação de:

* comportamento histórico;
* risco;
* retorno;
* correlação;
* sazonalidade;
* indicadores técnicos;
* desempenho comparativo.

### 📚 Classes de ativos

Entre as classes de ativos contempladas no catálogo estão, conforme disponibilidade da fonte de dados:

* 📈 **Ações**
* ₿ **Criptomoedas**
* 🏠 **Fundos Imobiliários (FIIs)**
* 🏢 **REITs**
* 🛢️ **Commodities**
* 📊 **Outros ativos organizados no catálogo interno da aplicação**

Os dados históricos são consultados via **Yahoo Finance**, utilizando o pacote **yfinance**, tratados localmente e apresentados em uma interface desenvolvida com **Streamlit** e **Plotly**.

---

# 🚀 Funcionalidades

## 🔍 Análise individual de ativos

A plataforma permite realizar análises individuais dos ativos disponíveis no catálogo.

Principais funcionalidades:

* Seleção hierárquica de ativos por classe e subclasse;
* Atalhos de período para **1, 3, 5 e 10 anos**;
* Escolha de intervalo personalizado de datas;
* Visualização de preços e evolução histórica;
* Gráfico de volatilidade anualizada por mês;
* Mapa de calor de sazonalidade dos retornos;
* Exportação dos dados processados em **CSV**.

---

## ⚖️ Comparação de ativos

Permite comparar simultaneamente diferentes ativos para análise de desempenho e risco.

Principais funcionalidades:

* Comparação simultânea de **2 a 5 ativos**;
* Normalização da evolução histórica em **Base 100**;
* Gráficos comparativos de desempenho;
* Matriz de correlação;
* Heatmap de correlação;
* Resumo comparativo de:

  * retorno;
  * volatilidade;
  * drawdown;
  * índice de Sharpe.

---

## 📈 Indicadores técnicos

A plataforma disponibiliza diferentes recursos de análise técnica.

### Gráficos

* Gráficos de fechamento;
* Gráficos de linhas;
* Gráficos de barras;
* Gráficos de candles, quando aplicável.

### Indicadores

* **SMA** — Média Móvel Simples;
* **EMA** — Média Móvel Exponencial;
* **Bandas de Bollinger**;
* **RSI** — Índice de Força Relativa;
* **MACD**;
* Acompanhamento de volume negociado.

---

# ⚠️ Risco e retorno

O Argos DataLab disponibiliza métricas quantitativas para avaliação histórica de risco e retorno.

Entre elas:

* **Retorno total**;
* **Retorno médio**;
* **Win rate**;
* **Volatilidade anualizada**;
* **Índice de Sharpe**, com taxa livre de risco configurável;
* **Drawdown máximo**;
* Data do pior drawdown do período;
* Distribuição de retornos por faixas percentuais.

> [!NOTE]
> As métricas são calculadas com base em dados históricos e devem ser interpretadas como instrumentos de estudo e análise quantitativa.

---

# 🧱 Estrutura do projeto

A estrutura abaixo representa os principais diretórios esperados pela aplicação:

```text
argos/
├── app/
│   ├── main.py                 # Ponto de entrada da aplicação Streamlit
│   └── views/                  # Páginas e módulos de interface
│
├── core/
│   ├── assets.py               # Catálogo central de ativos
│   └── ...                     # Regras de negócio, tratamento e análises
│
├── tests/                      # Suíte de testes automatizados
│
├── requirements.txt            # Dependências Python
├── README.md                   # Documentação do projeto
└── ...
```

> [!TIP]
> A organização exata pode evoluir ao longo do projeto.
>
> Ao adicionar novos módulos, mantenha a separação entre:
>
> * **interface** → `app/`
> * **regras analíticas e dados** → `core/`
> * **testes** → `tests/`

---

# 🛠️ Tecnologias

O projeto utiliza as seguintes tecnologias:

| Tecnologia                | Finalidade                                    |
| ------------------------- | --------------------------------------------- |
| **Python**                | Linguagem principal                           |
| **Streamlit**             | Interface web e navegação da aplicação        |
| **Plotly**                | Gráficos interativos                          |
| **pandas**                | Tratamento e análise tabular de dados         |
| **NumPy**                 | Operações numéricas e estatísticas            |
| **yfinance**              | Consulta de dados históricos do Yahoo Finance |
| **pytest**                | Testes automatizados                          |
| **coverage / pytest-cov** | Medição de cobertura de testes                |

---

# 📋 Pré-requisitos

Antes de iniciar, tenha instalado:

* **Python 3.10 ou superior**
* **Git**
* **PowerShell** no Windows ou terminal equivalente no macOS/Linux

Verifique a versão do Python:

```bash
python --version
```

---

# 💻 Instalação local

## 1. Clone o repositório

```bash
git clone https://github.com/cleristoncramos/argos.git
cd argos
```

## 2. Crie o ambiente virtual

```bash
python -m venv venv
```

## 3. Ative o ambiente virtual

### Windows — PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a execução de scripts, execute uma vez no terminal atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois, ative novamente:

```powershell
.\venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
source venv/bin/activate
```

## 4. Atualize o pip e instale as dependências

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

# ▶️ Execução local

Com o ambiente virtual ativado, execute o seguinte comando na raiz do projeto:

```bash
streamlit run app/main.py
```

O Streamlit iniciará o servidor local e normalmente abrirá a aplicação automaticamente no navegador.

Caso isso não ocorra, acesse:

```text
http://localhost:8501
```

Para encerrar o servidor:

```text
Ctrl + C
```

---

# 📊 Fonte de dados

A aplicação utiliza dados históricos disponibilizados pelo **Yahoo Finance**, por meio do pacote **yfinance**.

O catálogo de ativos é centralizado em:

```text
core/assets.py
```

Esse catálogo deve concentrar:

* Código ou ticker do ativo;
* Nome de exibição;
* Classe e subclasse do ativo;
* Fonte de dados;
* Regras de validação;
* Critérios de liquidez e qualidade, quando aplicáveis.

## ⚠️ Limitações da fonte

Dados de mercado podem sofrer:

* atrasos;
* indisponibilidade temporária;
* alterações de ticker;
* ajustes históricos;
* limitações da fonte externa.

Por isso:

* valide o ticker antes de utilizá-lo em análises;
* trate falhas de consulta de API de forma controlada;
* não interprete dados históricos como garantia de desempenho futuro;
* não utilize a aplicação como ferramenta de recomendação de investimento.

---

# 🧪 Testes e cobertura

A suíte automatizada deve validar, no mínimo:

* Integridade do catálogo de ativos;
* Tratamento e limpeza de dados históricos;
* Cálculos de retorno, volatilidade, Sharpe e drawdown;
* Regras de normalização em Base 100;
* Transformações para indicadores técnicos;
* Regras de visualização e componentes críticos, quando aplicável.

## Executar os testes

```bash
python -m pytest
```

## Executar testes com cobertura

Se o projeto estiver configurado com `pytest-cov`, execute:

```bash
python -m pytest --cov=core --cov-report=term-missing --cov-report=html
```

A cobertura é medida prioritariamente no diretório `core/`.

### 🎯 Meta de cobertura

A meta mínima configurada no projeto é de:

```text
80%
```

O pipeline de integração contínua deve falhar caso a cobertura fique abaixo desse limite.

## Abrir o relatório HTML de cobertura

### Windows

```powershell
Start-Process ".\htmlcov\index.html"
```

### macOS

```bash
open htmlcov/index.html
```

### Linux

```bash
xdg-open htmlcov/index.html
```

---

# ✅ Boas práticas de desenvolvimento

Ao contribuir com o projeto:

1. Crie uma branch para cada funcionalidade ou correção.
2. Mantenha regras de negócio e cálculos em `core/`, evitando lógica analítica extensa dentro das páginas Streamlit.
3. Adicione ou atualize testes para toda alteração em cálculos, tratamento de dados ou regras críticas.
4. Evite expor tokens, chaves de API ou dados sensíveis no código-fonte.
5. Não faça commits de arquivos locais, ambientes virtuais, relatórios temporários ou credenciais.
6. Execute testes e valide a interface localmente antes de abrir um pull request ou fazer merge.
7. Documente decisões metodológicas que alterem métricas, indicadores ou regras de cálculo.

---

# 🌿 Fluxo de desenvolvimento e publicação

O fluxo recomendado é:

```text
Branch feature
      ↓
Desenvolvimento local
      ↓
Testes com pytest
      ↓
Validação local de UX/UI
      ↓
Commit e push
      ↓
Pull request / merge na main
      ↓
Deploy automático
```

## Criar uma branch

Exemplo:

```bash
git checkout -b feature/nome-da-funcionalidade
```

## Antes de enviar alterações

Execute os testes:

```bash
python -m pytest
```

Verifique o estado do repositório:

```bash
git status
```

Adicione as alterações:

```bash
git add .
```

Crie o commit:

```bash
git commit -m "feat: descreve a funcionalidade"
```

Envie a branch:

```bash
git push origin feature/nome-da-funcionalidade
```

---

# ☁️ Publicação

O deploy é realizado pelo **Streamlit Community Cloud**, por meio da integração com o GitHub.

## Configuração esperada

| Configuração           | Valor                   |
| ---------------------- | ----------------------- |
| **Repositório**        | `cleristoncramos/argos` |
| **Branch de produção** | `main`                  |
| **Arquivo de entrada** | `app/main.py`           |

Após o merge na branch `main`, a plataforma de deploy deve iniciar uma nova publicação automaticamente.

## Checklist antes da publicação

Antes de publicar, confirme:

* [ ] Dependências atualizadas em `requirements.txt`;
* [ ] Aplicação iniciando localmente com `streamlit run app/main.py`;
* [ ] Testes passando;
* [ ] Ausência de segredos no repositório;
* [ ] Ausência de arquivos grandes ou temporários indevidos.

---

# 🎓 Contexto acadêmico

O **Argos DataLab** está inserido no contexto do seguinte projeto acadêmico:

| Informação               | Detalhes                                                                               |
| ------------------------ | -------------------------------------------------------------------------------------- |
| **Programa**             | Iniciação em Desenvolvimento Tecnológico e Inovação — PIBITI UFPI 2026–2027            |
| **Plano de Trabalho**    | Análise de Dados para Apoio à Tomada de Decisão em Investimentos no Mercado Financeiro |
| **Pesquisador discente** | Clériston de Castro Ramos                                                              |
| **Orientador**           | Prof. Dr. Arlino Henrique Magalhães de Araújo                                          |
| **Instituição**          | Universidade Federal do Piauí — UFPI                                                   |
| **Curso**                | Tecnologia em Gestão de Dados                                                          |

---

# ⚖️ Aviso legal e metodológico

O **Argos DataLab** é um projeto de **pesquisa, ensino e desenvolvimento tecnológico**.

Dados históricos e indicadores quantitativos são instrumentos para **estudo e análise**, não previsões ou garantias.

### Importante

* Resultados passados não garantem resultados futuros.
* A plataforma não oferece recomendação de compra, venda ou manutenção de ativos.
* Nenhuma informação exibida deve substituir análise profissional, avaliação de perfil de risco ou orientação de especialista habilitado.
* A disponibilidade e a precisão dos dados dependem de fontes externas e podem sofrer variações.

> [!WARNING]
> O Argos DataLab **não deve ser utilizado como ferramenta de recomendação de investimentos**.
>
> Seu objetivo é exclusivamente **acadêmico, educacional e de desenvolvimento tecnológico**.

---

# 📄 Licença

Projeto desenvolvido para fins **educacionais e de pesquisa** no âmbito do **PIBITI UFPI**.

**Todos os direitos reservados.**
