#importar bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta

#criar as funcoes de carregamento de dados
    #Cotacoes do itau - ITUB4 - 2010a 2024 

@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv("IBOV.csv", sep=";")
    tickers = list(base_tickers["Código"])
    tickers = [item + ".SA" for item in tickers]
    return tickers

@st.cache_data
def carregar_dados(empresas):
    dados_acao = yf.Tickers(empresas)
    precos_acao = dados_acao.history(period='1d', start='2014-01-01', end='2024-07-01')
    precos_acao = precos_acao["Close"]
    return precos_acao

dados  = carregar_dados(carregar_tickers_acoes())

#Criar interface da streamlit
st.write("""
# App Preço de Ações
O gráfico abaixo representa a evolução do preço das ações brasileiras ao longo dos anos
""")

#Inserir filtros
st.sidebar.header("Filtros")

#filtro de acoes
lista_acoes = st.sidebar.multiselect("Escolha as ações para exibir no gráfico", dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: "Close"})

#filtros datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider("Selecione o período", 
                  min_value=data_inicial,
                  max_value=data_final,
                  value=(data_final,data_final), 
                  step=timedelta(days=15))


dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

grafico = st.line_chart(dados)

#calculo performace
texto_performace_ativos = ""
texto_performace_carteira = ""

if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes) == 1:
    dados = dados.rename(columns={"Close": acao_unica})

carteira = [1000 for acao in lista_acoes]    
total_incial_carteira = sum(carteira)


for i,acao in enumerate(lista_acoes):
    if dados[acao].iloc[-1] != "nan" and dados[acao].iloc[0] != "nan":
        performace_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1
        performace_ativo = float(performace_ativo)
    if performace_ativo > 0:
        carteira[i] = carteira[i] * (1 + performace_ativo)

        if performace_ativo > 0:
            texto_performace_ativos = texto_performace_ativos + f"  \n{acao}:   :green[{performace_ativo:.1%}]"
        elif performace_ativo < 0:
            texto_performace_ativos = texto_performace_ativos + f"  \n{acao}:   :red[{performace_ativo:.1%}]"
        else:
            texto_performace_ativos = texto_performace_ativos + f"  \n{acao}:   {performace_ativo:.1%}"

if len(carteira) > 0:
    total_final_carteira = sum(carteira)
    performace_carteira = total_final_carteira / total_incial_carteira - 1

    if performace_carteira > 0:
        texto_performace_carteira = f"Performace da carteira com todos os ativos:   :green[{performace_carteira:.1%}]"
    elif performace_carteira < 0:
        texto_performace_carteira = f"Performace da carteira com todos os ativos:   :red[{performace_carteira:.1%}]"
    else:
        texto_performace_carteira = f"Performace da carteira com todos os ativos:   {performace_carteira:.1%}"

st.write(f"""
### Pergformace dos ATIVOS
Essa foi a pergformace de ativo durante o período selecionado:
{texto_performace_ativos}\n
{texto_performace_carteira}
""")
