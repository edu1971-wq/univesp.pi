
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página e CSS para Fundo Azul Forte ---
st.set_page_config(layout="wide", page_title="Análise Fiscal e Operacional",
                    initial_sidebar_state="expanded") 

# CSS personalizado para o fundo azul mais forte
# Usando um azul médio vibrante (#81d4fa) para um contraste decente com o texto preto.
st.markdown(
    """
    <style>
    .stApp {
        background-color: #81d4fa; /* Azul médio vibrante */
    }
    .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
        background-color: rgba(255, 255, 255, 0.9); /* Adiciona um fundo branco semi-transparente para as áreas de conteúdo */
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
    }
    h1, h2, h3, h4, h5, h6 {
        color: #0d47a1; /* Azul marinho para títulos */
    }
    .stMarkdown {
        color: #1a237e; /* Azul escuro para o texto */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.header("Análise do Relatório Fiscal - Largo de Osasco")
st.write("Dados extraídos de um relatório fiscal para visualização em gráficos e tabelas coloridas.")

# Os dados
data = {
    'Linha': [329, 329, 329, 329, 329, 330, 329, 330, 329, 329, 329, 329, 329],
    'Carro': [329, 330, 329, 329, 330, 329, 330, 329, 329, 329, 329, 329, 330],
    'Partida': ['4:05', '5:15', '6:25', '7:50', '8:55', '10:25', '12:00', '13:30', '14:40', '15:50', '17:05', '18:20', '19:35'],
    'Entrada': ['4:05', '5:15', '6:15', '7:30', '8:55', '9:10', '10:45', '12:15', '13:25', '14:35', '15:45', '17:00', '18:15'],
    'Saida': ['4:49', '5:56', '7:22', '8:15', '9:04', '10:04', '11:33', '13:06', '14:10', '15:22', '16:32', '17:52', '19:01'],
    'Tempo': [44, 46, 67, 45, 54, 48, 51, 45, 47, 47, 52, 46, 52],
    'Catraca': ['4:05', '5:15', '6:25', '7:50', '8:55', '10:25', '12:00', '13:30', '14:40', '15:50', '17:05', '18:20', '19:35'],
    'Retorno': ['7:50', '8:55', '10:25', '12:00', '13:30', '14:40', '15:50', '17:05', '18:20', '19:35', '20:50', '22:25', '23:40'],
    'Motorista': ['Odenilton', 'Odenilton', 'Jessy', 'Jessy', 'Odenilton', 'Odenilton', 'Odenilton', 'Odenilton', 'L Daniel', 'Dantas', 'S DANIEL', 'Dantas', 'S DANIEL'],
    'Cobrador': ['Odenilton', 'Odenilton', 'Jessy', 'Jessy', 'Odenilton', 'Odenilton', 'Odenilton', 'Odenilton', 'L Daniel', 'Dantas', 'S DANIEL', 'Dantas', 'S DANIEL'],
    'Pass.': [24, 22, 44, 16, 17, 13, 15, 8, 15, 17, 17, 17, 19],
    'Observações': [None, None, None, None, None, None, None, None, 'REND', None, None, None, None]
}

df = pd.DataFrame(data)

# Processamento de dados
df['Catraca'] = pd.to_datetime(df['Catraca'], format='%H:%M', errors='coerce')
df['Retorno'] = pd.to_datetime(df['Retorno'], format='%H:%M', errors='coerce')
df.dropna(subset=['Catraca', 'Retorno'], inplace=True)
df['Duração (minutos)'] = (df['Retorno'] - df['Catraca']).dt.total_seconds() / 60
df.loc[df['Duração (minutos)'] < 0, 'Duração (minutos)'] += 24 * 60
df['Duração (horas)'] = df['Duração (minutos)'] / 60
df['REND'] = df['Observações'].astype(str).str.contains('REND', na=False)

# --- Gráficos Interativos ---
st.header("Gráficos por Motorista")

# Dropdown para selecionar um motorista
all_drivers = ['Todos'] + sorted(df['Motorista'].dropna().unique())
col_select, _ = st.columns([1, 3])
with col_select:
    selected_driver = st.selectbox("Selecione um Motorista:", all_drivers)

filtered_df = df if selected_driver == 'Todos' else df[df['Motorista'] == selected_driver]

# --- Colunas para os gráficos ---
col1, col2 = st.columns(2)

# --- Gráfico 1: Número de Viagens por Motorista (Pizza) ---
with col1:
    st.subheader("Número de Viagens")
    trip_counts = filtered_df.groupby('Motorista').size().reset_index(name='Viagens')

    if not trip_counts.empty:
        fig1 = px.pie(trip_counts, values='Viagens', names='Motorista',
                      title='Distribuição de Viagens por Motorista',
                      color_discrete_sequence=px.colors.sequential.Agsunset) # Paleta de cores vibrantes
        fig1.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Nenhuma viagem encontrada para o filtro selecionado.")

# --- Gráfico 2: Duração Total de Viagens por Motorista (Torre/Barras) ---
with col2:
    st.subheader("Duração Total de Viagens (em horas)")
    total_duration = filtered_df.groupby('Motorista')['Duração (horas)'].sum().reset_index()

    if not total_duration.empty:
        fig2 = px.bar(total_duration, x='Motorista', y='Duração (horas)',
                      title='Duração Total de Viagens por Motorista',
                      color='Motorista', 
                      color_discrete_sequence=px.colors.qualitative.Pastel) # Paleta de cores suave para barras
        fig2.update_layout(xaxis_title='Motorista', yaxis_title='Duração Total (horas)')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Nenhuma duração de viagem encontrada para o filtro selecionado.")

# --- Novo Gráfico 3: Total de Passageiros por Motorista (Torre/Barras) ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("Total de Passageiros Transportados")
    total_passageiros = filtered_df.groupby('Motorista')['Pass.'].sum().reset_index()

    if not total_passageiros.empty:
        fig_pass = px.bar(total_passageiros, x='Motorista', y='Pass.',
                          title='Total de Passageiros por Motorista',
                          color='Motorista',
                          color_discrete_sequence=px.colors.qualitative.Vivid) # Paleta de cores vibrante
        fig_pass.update_layout(xaxis_title='Motorista', yaxis_title='Total de Passageiros')
        st.plotly_chart(fig_pass, use_container_width=True)
    else:
        st.info("Nenhum passageiro encontrado para o filtro selecionado.")

# --- Gráfico 4: Contagem de Observações 'REND' (Pizza) ---
with col4:
    st.subheader("Proporção de Observações 'REND'")
    total_viagens_com_rend = filtered_df['REND'].sum()
    total_viagens_sem_rend = len(filtered_df) - total_viagens_com_rend

    rend_data = pd.DataFrame({
        'Tipo': ['Com REND', 'Sem REND'],
        'Contagem': [total_viagens_com_rend, total_viagens_sem_rend]
    })

    if rend_data['Contagem'].sum() > 0:
        fig_rend_pie = px.pie(rend_data, values='Contagem', names='Tipo',
                              title='Proporção de Viagens com Observação "REND"',
                              color_discrete_sequence=px.colors.qualitative.D3) # Paleta D3
        fig_rend_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        st.plotly_chart(fig_rend_pie, use_container_width=True)
    else:
        st.info("Nenhuma ocorrência de 'REND' ou viagens para mostrar a proporção.")


# --- Tabela de Dados Originais Colorida ---
st.markdown("---") 
st.header("Tabela de Dados Filtrados (Colorida)")

# Seleciona as colunas numéricas para aplicar o gradiente
numeric_cols = ['Tempo', 'Duração (minutos)', 'Duração (horas)', 'Pass.']

# Aplica um estilo de gradiente colorido nas colunas numéricas
if not filtered_df.empty:
    styled_df = filtered_df.style.background_gradient(subset=numeric_cols, cmap='Blues')
    st.dataframe(styled_df, use_container_width=True)
else:
    st.dataframe(filtered_df, use_container_width=True)


# --- Aba de Dashboards Adicionais (Também Coloridos) ---
st.markdown("---")
st.header("Outras Análises (Coloridas)")

tab_frota, tab_cumprimento, tab_passageiros_fluxo = st.tabs(["Resumo da Frota", "Fator de Cumprimento", "Fluxo de Passageiros Linha 378TRO"])

with tab_frota:
    st.subheader('Resumo da Frota - Domingos e Feriados')
    data_domingos = {
        'Unidade': ['Intermunicipal G1', 'Municipal Osasco G4', 'Seletivo G4', 'Total Osasco G1+G4', 'Intermunicipal G5', 'Total Santana G5'],
        'Frota Média': [42.0, 45.0, 2.0, 89.0, 23.5, 44.5],
        'Total Viagens': [598, 715, 20, 1333, 259, 528]
    }
    df_domingos = pd.DataFrame(data_domingos).set_index('Unidade')
    
    st.markdown("##### Frota Média (Torres Coloridas)")
    fig_frota_media = px.bar(df_domingos, x=df_domingos.index, y='Frota Média',
                             title='Frota Média por Unidade (Domingos e Feriados)',
                             color='Frota Média',
                             color_continuous_scale=px.colors.sequential.Mint)
    st.plotly_chart(fig_frota_media, use_container_width=True)
    
    st.markdown("##### Total de Viagens (Torres Coloridas)")
    fig_total_viagens_frota = px.bar(df_domingos, x=df_domingos.index, y='Total Viagens',
                                     title='Total de Viagens por Unidade (Domingos e Feriados)',
                                     color='Total Viagens',
                                     color_continuous_scale=px.colors.sequential.Sunset)
    st.plotly_chart(fig_total_viagens_frota, use_container_width=True)

with tab_cumprimento:
    st.subheader('Fator de Cumprimento de Viagens - Janeiro a Agosto/2025')
    data_cumprimento = {
        'Dia': [1, 2, 3, 4, 5],
        'NÚCLEO 1': [99.66, 100.00, 99.50, 99.56, 99.89],
        'NÚCLEO 4': [99.41, 99.59, 99.60, 99.78, 99.83],
        'NÚCLEO 5': [94.48, 98.30, 99.12, 99.59, 99.73],
        'SOMA DOS NÚCLEOS': [98.24, 99.35, 99.42, 99.65, 99.82]
    }
    df_cumprimento = pd.DataFrame(data_cumprimento).set_index('Dia')
    
    fig_cumprimento = px.line(df_cumprimento, x=df_cumprimento.index, y=['NÚCLEO 1', 'NÚCLEO 4', 'NÚCLEO 5', 'SOMA DOS NÚCLEOS'],
                              title='Fator de Cumprimento de Viagens por Dia',
                              color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig_cumprimento, use_container_width=True)

with tab_passageiros_fluxo:
    st.subheader('Fluxo de Passageiros - Linha 378TRO')
    data_passageiros = {
        'Hora': ['04:40', '05:00', '05:30', '05:45', '06:00'],
        'Passageiros': [34, 30, 31, 45, 26]
    }
    df_passageiros_fluxo = pd.DataFrame(data_passageiros)
    df_passageiros_fluxo['Hora_dt'] = pd.to_datetime(df_passageiros_fluxo['Hora'], format='%H:%M').dt.time
    df_passageiros_fluxo = df_passageiros_fluxo.sort_values(by='Hora_dt')

    fig_passageiros_fluxo = px.line(df_passageiros_fluxo, x='Hora', y='Passageiros',
                                    title='Fluxo de Passageiros por Hora na Linha 378TRO',
                                    markers=True,
                                    color_discrete_sequence=["#FF5733"]) # Linha de cor única e forte
    st.plotly_chart(fig_passageiros_fluxo, use_container_width=True)