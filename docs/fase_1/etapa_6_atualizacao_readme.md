# Fase 1 — Etapa 6: Atualização do README

## Objetivo

Transformar o `README.md` em guia de instalação, execução, uso, testes e publicação do Argos DataLab.

## Conteúdo documentado

O README passou a registrar:

- propósito educacional e de pesquisa;
- aviso de não recomendação de investimento;
- URL da aplicação publicada;
- funcionalidades de análise individual;
- indicadores técnicos;
- risco e retorno;
- comparação de ativos;
- cache e persistência de estado;
- tecnologias utilizadas;
- estrutura de diretórios;
- instalação com ambiente virtual;
- execução local com Streamlit;
- execução de testes e cobertura;
- fonte de dados;
- fluxo de publicação;
- práticas de qualidade;
- licença e responsabilidade de uso.

## Comandos principais

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app/main.py
python -m pytest
```

## Arquivos relacionados

- `README.md`
- `requirements.txt`
- `pytest.ini`
- `TESTES.md`

## Resultado

O repositório passou a oferecer instruções suficientes para instalação, execução local, validação e entendimento do projeto.
