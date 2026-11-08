# Evidência — árvore de trabalho na coleta do snapshot `snap-20261108-01`

Desvio documental: a coleta foi feita com a árvore registrada como alterada. Esta evidência demonstra que a única alteração local era um documento sem relação com o piloto.

| Item | Evidência |
| --- | --- |
| Commit da implementação | `47642c7ed233c07ba23539ec14b6e63c38a5fbf6` |
| Coleta | 08/11/2026, 11:49:21 (Brasília) |
| Única alteração local no momento da coleta | `docs/versao_congelada.md` (saída de `git status` imediatamente antes e depois da coleta) |
| Data de modificação do arquivo | 25/10/2026, 15:00:59 (anterior à coleta) |
| Diferenças em código, configuração ou dependências desde o commit | Nenhuma (`git diff --stat 47642c7 -- experiments app core requirements.txt app/requirements.txt pytest.ini` vazio) |
| SHA-256 da diferença do documento | `2eca26164fad294c898c63e628dfa95bfd558a6258bbb88187911b4f57154ed3` |

O registro "árvore alterada" permanece no manifesto e não é reclassificado como limpo.

## Diferença do documento

```diff
diff --git a/docs/versao_congelada.md b/docs/versao_congelada.md
index 71537a2..b47ae4e 100644
--- a/docs/versao_congelada.md
+++ b/docs/versao_congelada.md
@@ -50,7 +50,12 @@ O nome `v1.0-demo` é uma sugestão; mantenha o mesmo nome em todos os documento
 | Identificador do commit | _[saída de `git rev-parse HEAD`]_ |
 | Data do congelamento | _[dd/mm/aaaa]_ |
 | Testes e cobertura | _[ex.: 5xx testes, core/ 100%]_ |
-| Python / pandas / numpy / streamlit / plotly / yfinance | _[de `requirements-congelado.txt`]_ |
+| Sistema operacional | Windows |
+| Python | 3.13.15 |
+| Streamlit | 1.63.0 |
+| Pandas | 3.0.5 |
+| yfinance | 1.7.0 |
+| Data do teste | 25/10/2026 |
 | Dados em cache coletados em | _[dd/mm/aaaa]_ |
 | Explicação assistida | _[incluída / não incluída]_; versão pública: sem chamadas ao modelo (respostas salvas ou texto fixo) |
 | Modo de demonstração | _[validado com a internet desativada em dd/mm/aaaa]_ |
```

## Encerramento do desvio (08/11/2026)

Decisão do autor do projeto: **descartar** as alterações locais de `docs/versao_congelada.md`, que nunca entraram em commit.

- **Conferência antes do descarte:** o diff era exatamente o reproduzido acima. Nenhuma informação existia só ali. As versões e o sistema (Windows, Python 3.13.15, Streamlit 1.63.0, pandas 3.0.5, yfinance 1.7.0) constam em `TESTES.md`, `app/requirements.txt` e `docs/checkpoint_qualidade.md`. A data de 25/10/2026 consta em `TESTES.md` como a última execução registrada.
- **Como foi feito:** o arquivo voltou ao estado versionado (`git checkout`), sem commit de conteúdo novo.
- **Efeito:** a partir de agora, as execuções não registram mais a árvore como alterada por causa desse arquivo. Os registros anteriores, com `arvore_alterada: true`, continuam como estão e devem ser lidos com esta evidência.
