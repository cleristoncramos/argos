# Etapa 6 — Integração com a Interface

## Objetivos

- [ ] Eliminar duplicação de sidebars.
- [ ] Padronizar chaves de `st.session_state`.
- [ ] Aplicar cache para coleta e processamento de dados.
- [ ] Preservar o comportamento das páginas existentes.
- [ ] Executar testes automatizados e validação manual.

## Critérios de aceite

- [ ] Cada página usa uma sidebar intencional e sem controles duplicados.
- [ ] O ativo, período e frequência persistem entre páginas quando aplicável.
- [ ] A comparação possui estado próprio, sem conflitar com a análise individual.
- [ ] A coleta não é repetida sem necessidade.
- [ ] Mudanças de símbolo, período ou frequência invalidam corretamente o cache.
- [ ] `pytest -v` termina sem falhas.