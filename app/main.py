import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from core.config import config
from core.data_loader import download_active_data, validate_data
from core.data_processor import (
    prepare_dataframe,
    aggregate_by_frequency,
    select_primary_variable,
)
from core.analyzer import (
    calculate_statistics,
    calculate_percentage_change,
    create_year_month_matrix,
)

st.set_page_config(
    page_title="Argos DataLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Argos DataLab")

st.markdown(
    "### Inteligência de Dados para Apoio à Decisão no Mercado Financeiro"
)

st.caption(
    "Projeto PIBITI UFPI 2026–2027 · "
    "Orientador: Arlino Henrique Magalhães de Araújo"
)

# Sidebar com controles
st.sidebar.header("⚙️ Configurações")

# Seleção de ativo
symbol = st.sidebar.text_input(
    "Símbolo do Ativo",
    value=config.DEFAULT_ACTIVE,
    help="Exemplos: BTC-USD, AAPL, USD=BRL, GOLD"
)

# Seleção de período
start_date = st.sidebar.date_input(
    "Data Inicial",
    value=datetime.strptime(config.DEFAULT_START_DATE, "%Y-%m-%d")
)

end_date = st.sidebar.date_input(
    "Data Final",
    value=datetime.strptime(config.DEFAULT_END_DATE, "%Y-%m-%d")
)

# Frequência
frequency = st.sidebar.selectbox(
    "Frequência",
    options=config.FREQUENCIES,
    index=config.FREQUENCIES.index(config.DEFAULT_FREQUENCY)
)

# Botão de carregar
if st.sidebar.button("🔄 Carregar Dados", type="primary"):
    with st.spinner("Baixando dados..."):
        # 1. Baixar dados
        df_raw = download_active_data(
            symbol=symbol,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            interval="1d"
        )
        
        if df_raw is None or df_raw.empty:
            st.error("❌ Nenhum dado encontrado. Verifique o símbolo e o período.")
            st.stop()
        
        # 2. Validar dados
        validation = validate_data(df_raw)
        
        if not validation['has_data']:
            st.error("❌ Dados inválidos.")
            st.stop()
        
        # 3. Preparar dados
        df_prepared = prepare_dataframe(df_raw)
        
        # 4. Agregar por frequência
        df_aggregated = aggregate_by_frequency(df_prepared, frequency)
        
        # 5. Selecionar variável principal
        df_primary = select_primary_variable(df_aggregated, "Close")
        
        # 6. Calcular variação percentual
        df_with_change = calculate_percentage_change(df_primary, "Value")
        
        # 7. Calcular estatísticas
        stats = calculate_statistics(df_with_change, "Value")
        
        # Sucesso
        st.success(f"✅ Dados carregados: {symbol} | {len(df_with_change)} períodos")
        
        # Armazenar no session_state
        st.session_state['df'] = df_with_change
        st.session_state['symbol'] = symbol
        st.session_state['stats'] = stats
        st.session_state['validation'] = validation

# Verificar se há dados carregados
if 'df' not in st.session_state:
    st.info("👈 Configure os parâmetros na barra lateral e clique em **Carregar Dados**.")
    st.stop()

# Recuperar dados do session_state
df = st.session_state['df']
symbol = st.session_state['symbol']
stats = st.session_state['stats']

# =====================
# Seção 1: Resumo
# =====================
st.header("📊 Visão Geral do Ativo")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Primeiro Valor",
        value=f"R$ {stats['first_value']:,.2f}" if stats['first_value'] else "N/A"
    )

with col2:
    st.metric(
        label="Último Valor",
        value=f"R$ {stats['last_value']:,.2f}" if stats['last_value'] else "N/A"
    )

with col3:
    st.metric(
        label="Retorno Total",
        value=f"{stats['total_return']:.2f}%",
        delta=f"{stats['total_return']:.2f}%"
    )

with col4:
    st.metric(
        label="Períodos",
        value=stats['count']
    )

# =====================
# Seção 2: Evolução Temporal
# =====================
st.header("📈 Evolução Temporal do Ativo")

# Gráfico de linha
fig_line = px.line(
    df,
    x='Date',
    y='Value',
    title=f"Evolução do Preço de Fechamento — {symbol}",
    labels={'Date': 'Data', 'Value': 'Preço'},
    template='plotly_white'
)
fig_line.update_traces(line=dict(width=2))
st.plotly_chart(fig_line, use_container_width=True)

# =====================
# Seção 3: Variação Percentual
# =====================
st.header(f"📉 Variação Percentual — {frequency}")

# Gráfico de barras colorido
df_chart = df.dropna(subset=['Pct_Change']).copy()

fig_bar = px.bar(
    df_chart,
    x='Date',
    y='Pct_Change',
    title=f"Variação Percentual entre Períodos — {frequency}",
    labels={'Date': 'Data', 'Pct_Change': 'Variação (%)'},
    color='Pct_Change',
    color_continuous_scale='RdYlGn',
    template='plotly_white'
)
st.plotly_chart(fig_bar, use_container_width=True)

# =====================
# Seção 4: Matriz Anual x Mensal
# =====================
st.header("🗓️ Padrões Sazonais")

# Criar matriz
df_matrix = create_year_month_matrix(df, "Pct_Change")

# Heatmap com Plotly
fig_heatmap = go.Figure(data=go.Heatmap(
    z=df_matrix.values,
    x=df_matrix.columns,
    y=df_matrix.index,
    colorscale='RdYlGn',
    hoverongaps=False,
    hovertemplate='Ano: %{y}<br>Mês: %{x}<br>Variação: %{z:.2f}%<extra></extra>'
))

fig_heatmap.update_layout(
    title="Variação Média por Ano e Mês",
    xaxis_title="Mês",
    yaxis_title="Ano",
    template='plotly_white'
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# =====================
# Seção 5: Tabela de Dados
# =====================
st.header("📋 Dados Processados")

# Mostrar amostra
st.dataframe(
    df[['Date', 'Value', 'Pct_Change', 'Year', 'Month']].head(100),
    use_container_width=True,
    height=300
)

# Botão para download
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Baixar CSV",
    data=csv_data,
    file_name=f"{symbol}_dados_tratados.csv",
    mime='text/csv'
)

# =====================
# Seção 6: Validação
# =====================
st.header("🔍 Qualidade e Validação dos Dados")

validation = st.session_state['validation']

col_v1, col_v2 = st.columns(2)

with col_v1:
    st.subheader("Qualidade")
    st.write(f"**Total de linhas:** {validation['total_rows']}")
    st.write(f"**Datas duplicadas:** {validation['duplicate_dates']}")
    st.write(f"**Valores negativos (Close):** {validation['negative_close']}")

with col_v2:
    st.subheader("Valores Ausentes")
    st.write(validation['missing_values'])

# =====================
# Rodapé
# =====================
st.markdown("---")
st.caption(
    "⚠️ **Aviso:** Esta ferramenta é destinada a fins educacionais e de pesquisa. "
    "Os dados históricos não garantem resultados futuros. "
    "Não constitui recomendação de investimento."
)