Fase 3 - Etapa 1: Nova Arquitetura de Navegação e Reestruturação de Diretórios
🎯 Objetivo
Modernizar o sistema de roteamento do Argos DataLab, substituindo menus customizados legados pela nova arquitetura nativa de navegação do Streamlit. Além disso, reorganizar a árvore de diretórios do projeto para melhorar a manutenibilidade e resolver conflitos de importação de módulos gerados pelo novo escopo de pastas.

🛠️ Mudanças Realizadas
1. Migração para st.navigation e st.Page
A navegação do sistema foi completamente refatorada. Anteriormente, a troca de páginas dependia de mecanismos mais engessados ou da estrutura padrão (e limitante) de multipages do Streamlit, que muitas vezes exibia rótulos indesejados como "main" na barra lateral.

Implementação:

Adoção das novas APIs st.Page e st.navigation no arquivo principal (main.py).

Agora, a definição de rotas, títulos, ícones e a renderização do menu lateral ocorrem de forma programática, centralizada e limpa.

Essa mudança permitiu a remoção de rótulos indesejados, garantindo um visual de dashboard profissional e fluido.

Exemplo conceitual do novo roteamento (em main.py):

Python
import streamlit as st

# Definição das páginas
pg_sobre = st.Page("views/sobre_projeto.py", title="Sobre o Projeto", icon="📊")
pg_analise = st.Page("views/analise_individual.py", title="Análise Individual", icon="📈")
# ... demais páginas

# Configuração e execução da navegação
pg = st.navigation([pg_sobre, pg_analise, ...])
pg.run()
2. Reestruturação de Diretórios (app/views/)
Com a nova navegação programática, não há mais a obrigatoriedade de manter as páginas soltas na raiz do projeto ou na pasta padrão pages/.

Implementação:

Criou-se o diretório app/views/ dedicado exclusivamente a armazenar os arquivos de interface de cada tela (ex: sobre_projeto.py, indicadores_tecnicos.py, risco_retorno.py, etc.).

O arquivo main.py atua apenas como o entrypoint (ponto de entrada) e orquestrador das rotas.

Essa separação de responsabilidades (MVC - Model-View-Controller adaptado) isola a lógica de visualização (views) do núcleo da aplicação (core) e dos componentes reutilizáveis (ui).

3. Resolução do Erro de Importação (ModuleNotFoundError)
A movimentação dos arquivos de página para a subpasta app/views/ causou a perda de referência do diretório raiz (argos) pelo interpretador Python na hora da execução via st.navigation. Isso resultava no erro crítico:

ModuleNotFoundError: No module named 'app' (ou core).

Implementação e Correção:
Para evitar configurações complexas de ambiente no servidor de deploy ou depender do PYTHONPATH, foi adotada uma injeção dinâmica no sys.path diretamente no topo de cada arquivo de visualização (dentro de app/views/).

Isso garante que, independentemente de onde o script for chamado, o Python reconheça o diretório raiz do projeto e consiga importar os pacotes app e core corretamente.

Padrão de injeção implementado no topo de todas as views:

Python
import os
import sys

# Garante que a raiz do projeto seja reconhecida pelo Python
PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../..",  # Sobe dois níveis: views -> app -> raiz
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from app.ui.sidebar import render_asset_controls
from core.data_loader import download_active_data
# ... demais importações relativas à raiz do projeto
📈 Impacto no Projeto
Escalabilidade: Adicionar novas telas ao sistema agora exige apenas a criação do arquivo em views/ e a declaração de um novo st.Page no arquivo principal.

Organização Profissional: O código fica mais limpo, com rotas centralizadas e uma arquitetura de pastas padronizada com ecossistemas de desenvolvimento modernos.

Robustez: A injeção de sys.path previne falhas de importação silenciosas ou dependentes da máquina do desenvolvedor (ambiente local vs. produção).