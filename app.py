import streamlit as st
import datetime
import numpy as np
import pandas as pd
from modules.financials_functions import portfolio_volatility, portfolio_returns, VaR
from modules.backend import tickers_by_issuer

# =======
# BACKEND
# =======

def complemento_confianza(confianza_str: str) -> float:
    """
    Recibe un nivel de confianza como string (por ejemplo '95')
    y retorna 1 - nivel_de_confianza como float (por ejemplo 0.05).
    """
    # Eliminar el símbolo '%' si está presente
    limpio = confianza_str.strip().replace('%', '')

    valor = float(limpio) / 100   # convertir '95' -> 0.95
    return 1 - valor

def risk(start:str, end:str, confidence:float) -> pd.DataFrame:
    '''
    '''
    # obtener tickers de ishares
    tickers = tickers_by_issuer(issuer='iShares')

    # portafolio de renta fija
    tickers_rf = tickers[tickers['CATEGORIA']=='ETF RF']
    list_tickers_rf = list(tickers_rf['TICKER'])

    # portafolio de renta variable
    tickers_rv = tickers[tickers['CATEGORIA']=='ETF RV']
    list_tickers_rv = list(tickers_rv['TICKER'])

    lst = []
    for portafolio in [list_tickers_rf, list_tickers_rv]:

        # obtener retornos
        df = portfolio_returns(tickers=portafolio,start=start, end=end)

        vector_w = np.array( [1/len(portafolio)] * len(portafolio) )
   
        # calcular volatilidad
        sigma = portfolio_volatility(df=df, vector_w=vector_w)

        # calcular VaR
        var = VaR(sigma=sigma, confidence=confidence)
        var = np.abs(var)
        var_mensual = var * np.sqrt(20)
        lst.append(var_mensual)
    
    df_final = pd.DataFrame(
        {
            'PORTAFOLIO': ['Ishares Renta Fija', 'Ishares Renta Variable'],
            f'Value At Risk: {1-confidence}%': lst

        }
    )
    df_final = df_final.sort_values(
        by=f'Value At Risk: {1-confidence}%',
         ascending=False)
    
    return df_final


st.title('Programación en Finanzas - Evaluación 2')

# Panel Lateral
st.sidebar.title('Parametros de Entrada')

st.sidebar.date_input("Fecha Inicio", '2023-01-01',key='start')
st.sidebar.date_input("Fecha Fin", '2025-09-01', key='end')

confidence = st.sidebar.selectbox('Nivel de Confianza', ['95%', '99%'])
confidence = complemento_confianza(confianza_str=confidence)
st.session_state.confidence = np.round(confidence,2)



df = risk(
    start = st.session_state.start,
    end = st.session_state.end,
    confidence = st.session_state.confidence,
)

st.dataframe(df)
