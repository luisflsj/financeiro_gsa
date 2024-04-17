import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
# ======================= FORMATAÇÃO FINANCEIRA ======================= #

def format_number(value, prefix=''):
    try:
        value = float(value)
    except ValueError:
        return value  # Retorna o valor original se não puder ser convertido para float
    
    is_negative = value < 0
    value = abs(value)

    for unit in ['', 'mil']:
        if value < 1000:
            formatted_value = f'{value:.2f}'.replace('-', '')  # Remove o sinal de menos se presente
            return f'{prefix}{"-" if is_negative else ""}{formatted_value} {unit}'
        value /= 1000

    formatted_value = f'{value:.2f}'.replace('-', '')  # Remove o sinal de menos se presente
    return f'{prefix}{"-" if is_negative else ""}{formatted_value} milhões'

# ======================= FORMATAÇÃO DE DATAS ======================= #

def converter_data(data_str):
    if isinstance(data_str, str):
        return datetime.strptime(data_str, '%d/%m/%Y').date()
    else:
        return data_str
    
# ======================= DOWNLOAD DE DATAFRAMES ======================= #

def generate_pdf(df):
    pdf = FPDF(orientation='L')  # Definir orientação como paisagem
    pdf.add_page()

    # Definir título da página
    pdf.set_font("Arial", size=7)
    pdf.cell(280, 10, txt="Tabela Financeira", ln=True, align="R")  # Ajustar largura para modo paisagem

    # Adicionar dados da tabela
    col_widths = [40] * len(df.columns)  # Inicializar larguras das colunas
    row_height = 10

    # Calcular larguras ideais das colunas com base no tamanho dos dados
    for i, col in enumerate(df.columns):
        max_width = pdf.get_string_width(col)  # Largura máxima da coluna
        for value in df[col]:
            value_width = pdf.get_string_width(str(value))
            max_width = max(max_width, value_width)
        col_widths[i] = max_width + 6  # Adicionar algum espaço extra

    # Adicionar dados da tabela com larguras ajustadas
    for row in df.values:
        for i, item in enumerate(row):
            pdf.cell(col_widths[i], row_height, txt=str(item), border=1)
        pdf.ln(row_height)

    pdf_filename = "dataframe.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

