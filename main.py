import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
from dataframes import df_financeiro
from funcoes import format_number, converter_data, generate_pdf
from fpdf import FPDF

st.set_page_config(page_title="Análise Financeira GSA", layout="wide")

st.markdown("<h1 style='text-align: center;'>Análise Financeira GSA</h1>", unsafe_allow_html=True)
st.markdown("---")

# ====================== SIDEBAR ====================== #

st.sidebar.image('logo_gsa.png', width=300)

with st.sidebar:
    # Defina a data de hoje
    hoje = date.today()

    # Primeiro dia do mês atual
    primeiro_dia_mes_atual = hoje.replace(day=1)

    # Último dia do mês anterior
    ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)

    # Primeiro dia do mês anterior
    primeiro_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)

    # Crie os campos de entrada de data com os valores padrão para o mês anterior
    data_inicio_default = primeiro_dia_mes_anterior
    data_fim_default = ultimo_dia_mes_anterior

    # Crie os campos de entrada de data
    data_inicio_str, data_fim_str = st.date_input("Selecione um intervalo de datas", [data_inicio_default, data_fim_default])

    # Converta as datas para o formato de objeto de data
    data_inicio = converter_data(data_inicio_str)
    data_fim = converter_data(data_fim_str)

    receita_despesa = df_financeiro['Tipo'].unique().tolist()
    filtro_receita_despesa = st.multiselect('Receita / Despesa', receita_despesa)

    cliente = df_financeiro['Cliente/Fornecedor'].unique().tolist()
    filtro_cliente = st.multiselect('Cliente', cliente)

    categoria = df_financeiro['Categoria'].unique().tolist()
    filtro_categoria = st.multiselect('Categoria', categoria)

    quitado = df_financeiro['Quitado'].unique().tolist()
    filtro_quitado = st.multiselect('Quitado?', quitado)

    df_financeiro_filtrado = df_financeiro

    # Convertendo a coluna 'Vencimento' do DataFrame para objetos de data do Pandas
    df_financeiro_filtrado['Vencimento'] = pd.to_datetime(df_financeiro_filtrado['Vencimento'], format='%d/%m/%Y')

    if data_inicio and data_fim:
        df_financeiro_filtrado = df_financeiro_filtrado[
            (df_financeiro_filtrado['Vencimento'] >= pd.Timestamp(data_inicio)) &
            (df_financeiro_filtrado['Vencimento'] <= pd.Timestamp(data_fim))
        ]

    if filtro_receita_despesa:
        df_financeiro_filtrado = df_financeiro_filtrado[df_financeiro_filtrado['Tipo'].isin(filtro_receita_despesa)]

    if filtro_cliente:
        df_financeiro_filtrado = df_financeiro_filtrado[df_financeiro_filtrado['Cliente/Fornecedor'].isin(filtro_cliente)]

    if filtro_categoria:
        df_financeiro_filtrado = df_financeiro_filtrado[df_financeiro_filtrado['Categoria'].isin(filtro_categoria)]

    if filtro_quitado:
        df_financeiro_filtrado = df_financeiro_filtrado[df_financeiro_filtrado['Quitado'].isin(filtro_quitado)]
        
# ====================== FORMATAÇÃO PARA FLOAT ====================== #

colunas = ['Valor (R$)']

for coluna in colunas:
    df_financeiro_filtrado[coluna] = df_financeiro_filtrado[coluna].astype(str)
    df_financeiro_filtrado[coluna] = df_financeiro_filtrado[coluna].str.replace(',', '.', regex=False).astype(float)

aba1, aba2, aba3, aba4 = st.tabs(['Métricas Financeiro', 'Receitas', 'Despesas', 'Despesas Diretoria'])

# ==================== MÉTRICAS ==================== #
with aba1:

    coluna1, coluna2, coluna3 = st.columns(3)

    # === RECEITAS === #
    df_receitas = df_financeiro_filtrado[df_financeiro_filtrado['Tipo'] == 'RECEITA']

    valor = df_receitas['Valor (R$)'].sum()
  
    with coluna1:
        st.subheader('Receitas')
        st.metric('Valor (R$)', format_number(valor, "R$"))

    # === DESPESAS === #

    df_despesas = df_financeiro_filtrado[df_financeiro_filtrado['Tipo'] == 'DESPESA']

    valor = df_despesas['Valor (R$)'].sum()

    with coluna2:
        st.subheader('Despesas')
        st.metric('Valor (R$)', format_number(valor, "R$"))

    # === RECEITAS - DESPESAS === #

    diff_valor = df_receitas['Valor (R$)'].sum() - df_despesas['Valor (R$)'].sum()

    with coluna3:
        st.subheader('Diferença')
        st.metric('Valor (R$)', format_number(diff_valor, "R$"))

    st.divider()

    st.subheader('Base de dados')
    colunas_exibir = ['Tipo', 'Quitado', 'Competência', 'Vencimento', 'Valor (R$)', 'Categoria', 'Cliente/Fornecedor']
    df_financeiro_exibicao = df_financeiro_filtrado[colunas_exibir]
    st.dataframe(df_financeiro_exibicao)


    # Botão para download do PDF
    if st.button('Download PDF'):
        pdf = generate_pdf(df_financeiro_exibicao)
        pdf_file = "dataframe.pdf"
        pdf.output(pdf_file)
        st.download_button(label="Download", data=pdf_file, file_name=pdf_file)

    st.divider()
    st.subheader('Estatísticas Gerais')

    qtd_clientes = len(df_receitas['Cliente/Fornecedor'].unique())
    qtd_fornecedores = len(df_despesas['Cliente/Fornecedor'].unique())

    coluna1, coluna2 = st.columns(2)

    with coluna1:
        st.metric('Quantidade de Clientes', qtd_clientes)
    with coluna2:
        st.metric('Quantidade de Fornecedores', qtd_fornecedores)

    st.divider()

with aba2:
    clientes = len(df_receitas['Cliente/Fornecedor'].unique())

    st.metric('Quantidade de Clientes', qtd_clientes)
   
    # === GRÁFICOS DE RECEITAS === #

    st.subheader('Distribuição de Valores por Clientes')

    # === VALOR === #
    df_receitas_clientes = df_receitas.groupby('Cliente/Fornecedor')['Valor (R$)'].sum().reset_index()
    df_receitas_clientes = df_receitas_clientes.sort_values(by = 'Valor (R$)', ascending=False)
    df_receitas_clientes['Valor'] = df_receitas_clientes['Valor (R$)'].apply(format_number)

    graf_valor = px.bar(
        df_receitas_clientes.head(10),
        x = 'Cliente/Fornecedor',
        y = 'Valor (R$)',
        color_discrete_sequence=[px.colors.qualitative.Vivid[5]],
        text = 'Valor',
        title='TOP 10 Distribuição de Receitas por Cliente'
    )
    st.plotly_chart(graf_valor, use_container_width=True)

    # === QUITAÇÃO TOTAL === #
    df_quitacao_total = df_receitas['Quitado'].value_counts().reset_index()
    df_quitacao_total.columns = ['Quitado', 'Quantidade']
    df_quitacao_total = df_quitacao_total.sort_values(by='Quantidade', ascending=False)

    coluna1, coluna2 = st.columns(2)

    with coluna1:
        graf_quitacao_total = px.bar(
            df_quitacao_total,
            x = 'Quitado',
            y = 'Quantidade',
            color_discrete_sequence=[px.colors.qualitative.Vivid[5]],
            text = 'Quantidade',
            title= 'Quantidade de Clientes Quitados Total'
        )
        st.plotly_chart(graf_quitacao_total, use_container_width=True)

        df_quitacao_total_receita = df_receitas.groupby('Quitado')['Valor (R$)'].sum().reset_index()
        df_quitacao_total_receita = df_quitacao_total_receita.sort_values(by = 'Valor (R$)', ascending=False)
        df_quitacao_total_receita['Valor'] = df_quitacao_total_receita['Valor (R$)'].apply(format_number)

    with coluna2:
        graf_quitacao_total_receita = px.bar(
            df_quitacao_total_receita,
            x = 'Quitado',
            y = 'Valor (R$)',
            color_discrete_sequence=[px.colors.qualitative.Vivid[5]],
            text = 'Valor',
            title='Distribuição de Valores de Receitas Quitadas Totalmente'
        )
        st.plotly_chart(graf_quitacao_total_receita, use_container_width=True)

    df_categoria_receita = df_receitas.groupby('Categoria')['Valor (R$)'].sum().reset_index()
    df_categoria_receita = df_categoria_receita.sort_values(by = 'Valor (R$)', ascending=False)
    df_categoria_receita['Valor'] = df_categoria_receita['Valor (R$)'].apply(format_number)

    graf_categoria_receita = px.bar(
        df_categoria_receita.head(10),
        x = 'Categoria',
        y = 'Valor (R$)',
        color_discrete_sequence=[px.colors.qualitative.Vivid[5]],
        text = 'Valor',
        title='Distribuição de Valores por Categoria'
    )
    st.plotly_chart(graf_categoria_receita, use_container_width=True)

with aba3:
    fornecedores = len(df_despesas['Cliente/Fornecedor'].unique())

    st.metric('Quantidade de Fornecedores', fornecedores)
    
    # === GRÁFICOS DE DESPESAS === #

    st.subheader('Distribuição de Valores por Fornecedores')

    # === VALOR === #
    df_despesas_clientes = df_despesas.groupby('Cliente/Fornecedor')['Valor (R$)'].sum().reset_index()
    df_despesas_clientes = df_despesas_clientes.sort_values(by = 'Valor (R$)', ascending=False)
    df_despesas_clientes['Valor'] = df_despesas_clientes['Valor (R$)'].apply(format_number)

    graf_valor = px.bar(
        df_despesas_clientes.head(10),
        x = 'Cliente/Fornecedor',
        y = 'Valor (R$)',
        color_discrete_sequence=[px.colors.qualitative.Vivid[5]],
        text = 'Valor',
        title='TOP 10 Distribuição de despesas por Cliente'
    )
    st.plotly_chart(graf_valor, use_container_width=True)

    coluna1, coluna2 = st.columns(2)

    with coluna1:
        # === QUITAÇÃO TOTAL === #
        df_quitacao_total = df_despesas['Quitado'].value_counts().reset_index()
        df_quitacao_total.columns = ['Quitado', 'Quantidade']
        df_quitacao_total = df_quitacao_total.sort_values(by='Quantidade', ascending=False)

        graf_quitacao_total = px.bar(
            df_quitacao_total,
            x = 'Quitado',
            y = 'Quantidade',
            color_discrete_sequence=[px.colors.qualitative.Vivid[5]],
            text = 'Quantidade',
            title= 'Quantidade de Clientes Quitados Total'
        )
        st.plotly_chart(graf_quitacao_total, use_container_width=True)

    with coluna2:
        df_quitacao_total_despesa = df_despesas.groupby('Quitado')['Valor (R$)'].sum().reset_index()
        df_quitacao_total_despesa = df_quitacao_total_despesa.sort_values(by = 'Valor (R$)', ascending=False)
        df_quitacao_total_despesa['Valor'] = df_quitacao_total_despesa['Valor (R$)'].apply(format_number)

        graf_quitacao_total_despesa = px.bar(
            df_quitacao_total_despesa,
            x = 'Quitado',
            y = 'Valor (R$)',
            color_discrete_sequence=[px.colors.qualitative.Vivid[5]],
            text = 'Valor',
            title='Distribuição de Valores de despesas Quitadas Totalmente'
        )
        st.plotly_chart(graf_quitacao_total_despesa, use_container_width=True)

    df_categoria_despesa = df_despesas.groupby('Categoria')['Valor (R$)'].sum().reset_index()
    df_categoria_despesa = df_categoria_despesa.sort_values(by = 'Valor (R$)', ascending=False)
    df_categoria_despesa['Valor'] = df_categoria_despesa['Valor (R$)'].apply(format_number)

    graf_categoria_despesa = px.bar(
        df_categoria_despesa.head(10),
        x = 'Categoria',
        y = 'Valor (R$)',
        color_discrete_sequence=[px.colors.qualitative.Vivid[5]],
        text = 'Valor',
        title='Distribuição de Valores por Categoria'
    )
    st.plotly_chart(graf_categoria_despesa, use_container_width=True)

with aba4:
    df_retirada = df_despesas[df_despesas['Categoria'].str.contains('RETIRADA')]

    # ==================== MÉTRICAS ==================== #
    valor_retirada = df_retirada['Valor (R$)'].sum()

    st.metric('Retirada Diretoria', format_number(valor_retirada, 'R$'))

    df_categoria_retirada = df_retirada.groupby('Categoria')['Valor (R$)'].sum().reset_index()
    df_categoria_retirada = df_categoria_retirada.sort_values(by = 'Valor (R$)', ascending=False)
    df_categoria_retirada['Valor'] = df_categoria_retirada['Valor (R$)'].apply(format_number)

    graf_categoria_retirada = px.bar(
        df_categoria_retirada.head(10),
        x = 'Categoria',
        y = 'Valor (R$)',
        color_discrete_sequence=[px.colors.qualitative.Vivid[5]],
        text = 'Valor',
        title='Distribuição de Valores de Retiradas por Categoria'
    )
    st.plotly_chart(graf_categoria_retirada, use_container_width=True)
