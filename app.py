#importar as bibliotecas necessarias

# streamlit é a biblioteca para criar a dash
import streamlit as st
import pandas as pd
import plotly.express as px

# começando a criar o laytou da pagina 
# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados conforme feito no colab
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- cria Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")


# primeiro filtro barra lateral Filtro de Ano
# recebe os anos disponiveis no dataframe selecionando a coluna 'ano', pegar os valores unicos e organizar com o sorted
anos_disponiveis = sorted(df['ano'].unique())
# adiciona na sidebar cada valor dos anos 
# multiselect permite adicionar/remover filtros e define o nome desta opção como ano
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# #iremos executar um teste para verificar o que já foi feito
# deixaremos somente até o a linha 21 (t.sidebar.header("🔍 Filtros"))
# comentar o restante do codigo com ctrl + k + c (para retirar cttl + k + u)
# executar no terminal o comando streamlit run app.py

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# agora que temos o site com titulo, barra e filtros precisamos colocar o conteudo que são os graficos
# partir do momento que existem os filtros precisamos criar os dataframes filtrados
# uma vez que o usuario selecionou o filtro, temos que aplica-lo
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    #cria um dataframe com os dados dos anos selecionados
    (df['ano'].isin(anos_selecionados)) &
    # agora as seniorirdades selecionadas
    (df['senioridade'].isin(senioridades_selecionadas)) &
    # contratos selecionados
    (df['contrato'].isin(contratos_selecionados)) &
    # tamanho da empresa selecionadas
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
# definindo um titulo para o dashboard
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
# texto explicativo
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")


# --- Métricas Principais (KPIs) ---
# muito comum ao criar um dash é colocar as metricas principais
# para quem está analisando ter uma noção dos dados
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio = 0
    salario_mediano = 0
    salario_maximo = 0
    total_registros = 0
    cargo_mais_frequente = 'sem dados disponiveis'
    #salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

#dividindo a pagina em colunas 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")



# --- Análises Visuais com Plotly ---
# criando um novo subtitulo
st.subheader("Gráficos")

#definindo duas colunas para criar um grafico ao lado do outro
col_graf1, col_graf2 = st.columns(2)

#primeiro grafico
with col_graf1:
    if not df_filtrado.empty:
        # dentro dos dados filtrados pegando o top 10 (nlargest(10)) cargos('cargo') por salario medio ['usd'].mean()
        # agrupando por cargo groupby('cargo')
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        #tipo de grafico :barras
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            #orientação horizontal
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        # update_layout(title_x=0.1) move o local do titulo dea acordo com a alteração do grafico
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        # exibindo o grafico 
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        # caso ocorra algum erro o grafico nao é exibido
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

# segundo grafico é um histograma
# feito com a biblioteca seaborn, mas interativo por usar o plotly
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

#terceiro grafico (pizza)
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

#quarto grafico (exercicio desafio 3 aula)
# criar um grafico com diferença de média salarial para o cargo de cientista de dados por pais
with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
# exibindo linhas e colunas para analise de informações
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
     