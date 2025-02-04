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
    st.write(df)   

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
                        color_discrete_sequence=["green"], text_auto=True)

            fig.update_layout(
                xaxis_title="",  
                yaxis_title="",  
                xaxis_showticklabels=True,  
                yaxis_showticklabels=True   
            )
            st.plotly_chart(fig)

    # Análise de colunas numéricas
    numerical_columns = df.select_dtypes(include=['number']).columns
    if len(numerical_columns) > 0:
        st.write("**Distribuição das Variáveis Numéricas**:")
        for col in numerical_columns:
            fig = px.histogram(df, x=col, title=f"Distribuição de {col}",color_discrete_sequence=["green"], text_auto=True)
            st.plotly_chart(fig)

        # Adicionando seleção para gráfico personalizado
        st.write("### Gráfico Personalizado")
        div1,div2 = st.columns(2)
        with div1:
            selected_cat_col = st.selectbox("Escolha uma coluna categórica (Eixo X):", categorical_columns)
        with div2:
            selected_num_col = st.selectbox("Escolha uma coluna numérica (Eixo Y - Soma):", numerical_columns)

        if selected_cat_col and selected_num_col:
            aggregated_df = df.groupby(selected_cat_col, as_index=False)[selected_num_col].sum()

            fig = px.bar(aggregated_df, x=selected_cat_col, y=selected_num_col, 
                         title=f"Soma de {selected_num_col} por {selected_cat_col}",
                         color=selected_cat_col, text_auto=True)
            fig.update_layout(
                xaxis_title="",  
                yaxis_title="",  
                xaxis_showticklabels=True,  
                yaxis_showticklabels=True   
            )
            st.plotly_chart(fig)

def apply_filters(df):
    if df is None:
        return None

    with st.sidebar.expander("🔧 Configuração da Tabela", expanded=False):
        # Seleção de colunas
        available_columns = df.columns.tolist()
        selected_columns = st.multiselect("Selecione as colunas a serem exibidas", available_columns, default=available_columns)

    if not selected_columns:
        return None  # Retorna None se nenhuma coluna for selecionada

    filtered_df = df[selected_columns].copy()

    st.sidebar.header("Filtros")

    # Filtros para colunas categóricas
    categorical_columns = filtered_df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_columns:
        unique_values = filtered_df[col].dropna().unique().tolist()
        if unique_values:
            with st.sidebar.expander(f"Filtrar {col}", expanded=False):
                selected_values = st.multiselect(f"Escolha valores para {col}", unique_values, default=unique_values)
                filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

    # Filtros para colunas numéricas
    numerical_columns = filtered_df.select_dtypes(include=['number']).columns
    for col in numerical_columns:
        min_val = float(filtered_df[col].min())
        max_val = float(filtered_df[col].max())

        if min_val < max_val:  # Evita erro quando os valores são iguais
            with st.sidebar.expander(f"Filtrar {col}", expanded=False):
                selected_range = st.slider(f"Defina o intervalo de {col}", min_val, max_val, (min_val, max_val))
                filtered_df = filtered_df[(filtered_df[col] >= selected_range[0]) & (filtered_df[col] <= selected_range[1])]

    return filtered_df

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


 #Calculos de horas
def converter_para_minutos(hora_str):
    """Converte uma string no formato HH:MM para minutos inteiros."""
    horas, minutos = map(int, hora_str.split(":"))
    return horas * 60 + minutos

def converter_para_horas(minutos_totais):
    """Converte minutos inteiros para o formato HH:MM."""
    horas = minutos_totais // 60
    minutos = minutos_totais % 60
    return f"{horas:02}:{minutos:02}"

def calcular_diferenca_horas(hora_inicio, hora_fim):
    """Calcula a diferença entre duas horas no formato HH:MM, permitindo horas acima de 24h."""
    minutos_inicio = converter_para_minutos(hora_inicio)
    minutos_fim = converter_para_minutos(hora_fim)
    
    if minutos_fim < minutos_inicio:
        minutos_fim += 24 * 60  # Ajusta para casos em que a hora final passa da meia-noite
    
    diferenca_minutos = minutos_fim - minutos_inicio
    return converter_para_horas(diferenca_minutos)


        
st.subheader("📊 Ferramentas")

col1, col2 = st.columns([4,1.5])

with col1:


    # Cabeçalho
    st.subheader("Analisador de Dados CSV/Excel")

    # Carregar arquivo    
    data = load_file()

    # Verifica se há dados carregados
    if data is not None:
        filtered_data = apply_filters(data)
        show_detailed_summary(filtered_data)
    else:
        st.write("Por favor, faça o upload de um arquivo.")


with col2:  

    st.write("🧮 Calculadora")
    expressao = st.text_input("Digite sua expressão matemática:")
    if expressao:
        resultado_calculadora = calcular_expressao(expressao)
        st.success(f"Resultado: {resultado_calculadora}")
    st.write("_______")


    st.write("📅 Cálculo de Diferença entre Datas")
    data_inicio = st.date_input("Selecione a data de início")
    data_fim = st.date_input("Selecione a data de fim", datetime.date.today())
    if data_inicio and data_fim and data_inicio <= data_fim:
        anos, meses, dias = calcular_diferenca_datas(data_inicio, data_fim)
        st.success(f"Diferença: {anos} anos, {meses} meses, {dias} dias")
    else:
        st.warning("A data final deve ser maior ou igual à data de início.")
    st.write("_______")

    st.write("📊 Cálculo de Percentual")
    valor_total = st.number_input("Digite o valor total", min_value=0.0, step=1.0)
    valor_parcial = st.number_input("Digite o valor parcial", min_value=0.0, step=1.0)
    if valor_total > 0:
        percentual = calcular_percentual(valor_total, valor_parcial)
        st.success(f"O valor parcial representa {percentual:.2f}% do total.")
    st.write("_______")

    st.write("📏 Regra de Três Simples")
    base = st.number_input("Valor base", min_value=0.0, step=1.0)
    referencia = st.number_input("Valor de referência", min_value=0.0, step=1.0)
    novo_valor = st.number_input("Novo valor a comparar", min_value=0.0, step=1.0)
    if base > 0:
        resultado = regra_de_tres(base, referencia, novo_valor)
        st.success(f"Resultado: {resultado:.2f}")
    st.write("_______")



    st.write("⏳ Conversor de Unidades de Tempo")
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

    st.write("⏰ Cálculo de Diferença entre Horas")

    hora_inicio = st.text_input("Digite a hora de início (HH:MM)", "08:00", key="hora_inicio")
    hora_fim = st.text_input("Digite a hora de fim (HH:MM)", "17:00", key="hora_fim")

    # Validação e cálculo
    try:
        if hora_inicio and hora_fim:
            resultado = calcular_diferenca_horas(hora_inicio, hora_fim)
            st.success(f"Diferença: {resultado}")
        else:
            st.warning("Por favor, insira as horas corretamente.")
    except ValueError:
        st.warning("Formato inválido! Use HH:MM, exemplo: 12:00 ou 01:50.")

    st.write("_______")

    st.write("📏 Conversor Universal")
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


if "visits" not in st.session_state:
    st.session_state.visits = 0  # Inicializa contador

st.session_state.visits += 1  # Incrementa a cada acesso

st.write(f"Este projeto já foi acessado {st.session_state.visits} vezes.")