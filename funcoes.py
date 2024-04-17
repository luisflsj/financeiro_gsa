import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
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
