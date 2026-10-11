# Congelamento e registro da versão

Plano 2, item 8.5. A versão congelada é a usada em **qualquer demonstração** (ao vivo, screencast e versão pública) e na **avaliação com usuários**. Depois do congelamento, só entram correções pequenas; qualquer mudança de comportamento exige nova versão e novo registro.

## 1. Quando congelar

Depois dos blocos 7 (explicação assistida, se aprovada) e 9 (protocolo do CEP), da implementação e validação do **modo de demonstração com dados salvos** (requisito obrigatório) e da conferência final no navegador. Previsão do plano: **fevereiro/2027**. Marcos intermediários (tags provisórias) podem ser criados antes, mas **não** valem como versão de demonstração.

## 2. Antes de marcar a versão

```text
[ ] python -m pytest --cov=core --cov-report=term-missing   (sem falhas, core/ >= 95%)
[ ] roteiro de conferência no navegador executado sem falhas bloqueantes
[ ] textos revisados (linguagem neutra; avisos presentes em todas as páginas)
[ ] docs/checkpoint_qualidade.md e docs/checklist_pendencias.md atualizados
[ ] versões das bibliotecas registradas (abaixo)
[ ] git status limpo (nada por commitar)
[ ] MODO DE DEMONSTRAÇÃO implementado e validado (docs/demonstracao.md, seção 2.4):
    [ ] app abre e roda todas as análises da demo sem internet
    [ ] nenhuma chamada externa nos fluxos principais
    [ ] datasets versionados ou no pacote da demo, com hash no manifesto
    [ ] respostas de LLM salvas validadas (se houver 7B) e texto fixo de reserva funcionando
    [ ] aviso de versão congelada visível na interface
    [ ] teste automatizado do modo demo passando
    [ ] demonstração executada uma vez com a internet desativada
[ ] dados de demonstração gerados e a data da coleta registrada
```

## 3. Como marcar (PowerShell)

```powershell
git status
python -m pytest --cov=core --cov-report=term-missing
pip freeze > requirements-congelado.txt
git add requirements-congelado.txt docs/versao_congelada.md
git commit -m "Congela a versão de demonstração"
git tag -a v1.0-demo -m "Versão congelada para demonstração e avaliação"
git push
git push origin v1.0-demo
git rev-parse HEAD
```

O nome `v1.0-demo` é uma sugestão; mantenha o mesmo nome em todos os documentos. Para voltar a essa versão depois: `git checkout v1.0-demo` (e `git switch -` para retornar).

## 4. Registro (preencher no congelamento)

| Campo | Valor |
| --- | --- |
| Tag | _[ex.: v1.0-demo]_ |
| Identificador do commit | _[saída de `git rev-parse HEAD`]_ |
| Data do congelamento | _[dd/mm/aaaa]_ |
| Testes e cobertura | _[ex.: 5xx testes, core/ 100%]_ |
| Python / pandas / numpy / streamlit / plotly / yfinance | _[de `requirements-congelado.txt`]_ |
| Dados em cache coletados em | _[dd/mm/aaaa]_ |
| Explicação assistida | _[incluída / não incluída]_; versão pública: sem chamadas ao modelo (respostas salvas ou texto fixo) |
| Modo de demonstração | _[validado com a internet desativada em dd/mm/aaaa]_ |
| Manifesto dos dados | _[caminho e hash de `data/demo/manifest.json`]_ |
| Aprovada pelo orientador em | _[dd/mm/aaaa]_ (evidência em `docs/pibiti/decisoes_orientador.md`) |

## 5. Regras após o congelamento

1. Correção de erro: pequena, com teste, em nova tag (`v1.0.1-demo`), e o screencast e o cache são refeitos **se** a mudança aparecer neles.
2. Revisão de textos pela pessoa da área de educação (decisão N23): entra em **versão posterior**; se mudar algo que aparece na demonstração, refazer o cache e o screencast.
3. A coleta da avaliação com usuários (O6) só ocorre sobre a versão congelada e depois do parecer favorável do CEP.
4. O artigo e os relatórios citam a tag e a data.

## 6. Marcos provisórios já existentes

| Marco | Sugestão de tag | Observação |
| --- | --- | --- |
| Plano 2, blocos 1 a 6 | `plano2-bloco6` | Opcional; apenas marco de histórico |