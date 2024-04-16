import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
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
    
# ======================= DOWNLOAD DE DATAS ======================= #

def generate_pdf(df):
    pdf = FPDF(orientation='L')  # Define a orientação como paisagem
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    # Cabeçalho da tabela
    pdf.set_fill_color(255, 255, 255)
    col_widths = [25, 15, 20, 35, 20, 90, 80]
    row_height = 8
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], row_height, txt=col, border=1, ln=0, align='C', fill=True)

    pdf.ln(row_height)

    # Adiciona os dados ao PDF
    for index, row in df.iterrows():
        for i, col in enumerate(df.columns):
            pdf.cell(col_widths[i], row_height, txt=str(row[col]), border=1)

        pdf.ln(row_height)

    return pdf