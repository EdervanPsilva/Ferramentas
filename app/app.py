import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ferramentas", layout="wide")

# Função para carregar o arquivo CSV ou Excel
def load_file():
    uploaded_file = st.file_uploader("Escolha um arquivo CSV ou Excel", type=["csv", "xlsx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith("xlsx"):
            df = pd.read_excel(uploaded_file)
        
        if df.empty:
            st.error("O arquivo está vazio!")
        elif df.columns.size == 0:
            st.error("O arquivo não contém colunas!")
        return df
    return None

# Função para mostrar um resumo detalhado dos dados
def show_detailed_summary(df):
    st.write("### Visão geral dos Dados")   

    # Contagem de valores únicos por coluna
    st.write("**Contagem de Valores Únicos por Coluna:**")
    st.write(df.nunique())

    # Análise de categorias
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_columns) > 0:
        st.write("**Análise das Categorias**:")
        for col in categorical_columns:
            st.write(f"Categoria: {col}")
            st.write(df[col].value_counts())
            fig = px.bar(df[col].value_counts(), 
             title=f"Distribuição de {col}", 
             color_discrete_sequence=["green"])

            fig.update_layout(
                xaxis_title="",  # Remove o título do eixo X
                yaxis_title="",  # Remove o título do eixo Y
                xaxis_showticklabels=True,  # Remove os rótulos do eixo X
                yaxis_showticklabels=True   # Remove os rótulos do eixo Y
                )
            st.plotly_chart(fig)

    # Análise de colunas numéricas
    numerical_columns = df.select_dtypes(include=['number']).columns
    if len(numerical_columns) > 0:
        st.write("**Distribuição das Variáveis Numéricas**:")
        for col in numerical_columns:
            fig = px.histogram(df, x=col, title=f"Distribuição de {col}")
            st.plotly_chart(fig)

def calcular_diferenca_datas(data_inicio, data_fim):
    delta = data_fim - data_inicio
    anos = relativedelta(data_fim, data_inicio).years
    meses = relativedelta(data_fim, data_inicio).months
    dias = delta.days
    return anos, meses, dias

def calcular_percentual(valor_total, valor_parcial):
    return (valor_parcial / valor_total) * 100 if valor_total != 0 else 0

def regra_de_tres(base, referencia, novo_valor):
    return (novo_valor * referencia) / base if base != 0 else 0

def converter_tempo(valor, unidade):
    conversoes = {
        "Horas para Minutos": valor * 60,
        "Horas para Segundos": valor * 3600,
        "Minutos para Segundos": valor * 60,
        "Segundos para Minutos": valor / 60,
        "Segundos para Horas": valor / 3600,
        "Minutos para Horas": valor / 60
    }
    return conversoes.get(unidade, valor)

def converter_medidas(valor, unidade):
    conversoes = {
        "Km para m": valor * 1000,
        "m para Km": valor / 1000,
        "m para cm": valor * 100,
        "cm para m": valor / 100,
        "m para mm": valor * 1000,
        "mm para m": valor / 1000,
        "Litros para Mililitros": valor * 1000,
        "Mililitros para Litros": valor / 1000,
        "Celsius para Fahrenheit": (valor * 9/5) + 32,
        "Fahrenheit para Celsius": (valor - 32) * 5/9,
        "Km/h para m/s": valor / 3.6,
        "m/s para Km/h": valor * 3.6
    }
    return conversoes.get(unidade, valor)

def calcular_expressao(expressao):
    try:
        resultado = eval(expressao)
        return resultado
    except Exception as e:
        return f"Erro: {e}"

def save_notes(notes):
    with open("notes.txt", "w", encoding="utf-8") as file:
        file.write(notes)

def load_notes():
    try:
        with open("notes.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""


        
st.subheader("📊 Ferramentas")

col1, col2 = st.columns([4,2])

with col1:
    # st.subheader("Bloco de Anotações")

    # notes = st.text_area("Digite suas anotações aqui:", value=load_notes(), height=300)

    # if st.button("Salvar Anotações"):
    #     save_notes(notes)
    #     st.success("Anotações salvas com sucesso!")


    # Cabeçalho
    st.subheader("Analisador de Dados CSV/Excel")

    # Carregar arquivo
    data = load_file()

    # Verifica se há dados carregados
    if data is not None:
        show_detailed_summary(data)
    else:
        st.write("Por favor, faça o upload de um arquivo.")


with col2:
    

    st.subheader("🧮 Calculadora")
    expressao = st.text_input("Digite sua expressão matemática:")
    if expressao:
        resultado_calculadora = calcular_expressao(expressao)
        st.success(f"Resultado: {resultado_calculadora}")
    st.write("_______")


    st.subheader("📅 Cálculo de Diferença entre Datas")
    data_inicio = st.date_input("Selecione a data de início")
    data_fim = st.date_input("Selecione a data de fim", datetime.date.today())
    if data_inicio and data_fim and data_inicio <= data_fim:
        anos, meses, dias = calcular_diferenca_datas(data_inicio, data_fim)
        st.success(f"Diferença: {anos} anos, {meses} meses, {dias} dias")
    else:
        st.warning("A data final deve ser maior ou igual à data de início.")
    st.write("_______")

    st.subheader("📊 Cálculo de Percentual")
    valor_total = st.number_input("Digite o valor total", min_value=0.0, step=1.0)
    valor_parcial = st.number_input("Digite o valor parcial", min_value=0.0, step=1.0)
    if valor_total > 0:
        percentual = calcular_percentual(valor_total, valor_parcial)
        st.success(f"O valor parcial representa {percentual:.2f}% do total.")
    st.write("_______")

    st.subheader("📏 Regra de Três Simples")
    base = st.number_input("Valor base", min_value=0.0, step=1.0)
    referencia = st.number_input("Valor de referência", min_value=0.0, step=1.0)
    novo_valor = st.number_input("Novo valor a comparar", min_value=0.0, step=1.0)
    if base > 0:
        resultado = regra_de_tres(base, referencia, novo_valor)
        st.success(f"Resultado: {resultado:.2f}")
    st.write("_______")



    st.subheader("⏳ Conversor de Unidades de Tempo")
    valor_tempo = st.number_input("Digite o valor de tempo", min_value=0.0, step=1.0)
    opcoes_tempo = [
        "Horas para Minutos", "Horas para Segundos",
        "Minutos para Segundos", "Segundos para Minutos",
        "Segundos para Horas", "Minutos para Horas"
    ]
    unidade_tempo = st.selectbox("Escolha a conversão", opcoes_tempo)
    resultado_tempo = converter_tempo(valor_tempo, unidade_tempo)
    st.success(f"Resultado: {resultado_tempo:.2f}")
    st.write("_______")

    st.subheader("📏 Conversor Universal")
    valor_medida = st.number_input("Digite o valor", min_value=0.0, step=1.0)
    opcoes_medida = [
        "Km para m", "m para Km", "m para cm", "cm para m", "m para mm", "mm para m",
        "Litros para Mililitros", "Mililitros para Litros",
        "Celsius para Fahrenheit", "Fahrenheit para Celsius",
        "Km/h para m/s", "m/s para Km/h"
    ]
    unidade_medida = st.selectbox("Escolha a conversão", opcoes_medida)
    resultado_medida = converter_medidas(valor_medida, unidade_medida)
    st.success(f"Resultado: {resultado_medida:.2f}")
    st.write("_______")


