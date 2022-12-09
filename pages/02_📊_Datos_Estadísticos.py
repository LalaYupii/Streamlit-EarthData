'''
Gráficos estadísticos
'''

# Importaciones
import pandas as pd
from sqlalchemy import create_engine
import psycopg2 
import streamlit as st
from streamlit_metrics import metric, metric_row
#import streamlit.components.v1 as components
#from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pickle as pkl
import datetime
import numpy as np


# Variables globales
df = pd.DataFrame()
k_mag = pkl.load(open('Modelo/k_mag.py', 'rb'))
k_depth = pkl.load(open('Modelo/k_depth.py', 'rb'))


def configPage():
    '''
    Configura la pagina de Streamlit
    '''
    #configuraciones de la página
    st.set_page_config(
        page_title="Earth Data",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded")

    #Título principál de la página
    st.title("EARTH DATA")  
            
    page = """
    <style>
        [data-testid="stMetricLabel"] {
            color: #aaaaff;
            font-size: 25px;
            text-align: center;
        }

        [data-testid="metric-container"] {
            color: #ccccff;
            border-style: solid;
            border-radius: 20px;
            padding-left: 20px;
            padding-top: 10px;
        }
    </style>
    """
    st.markdown(page, unsafe_allow_html=True)
        

def cargarDatos(fec_desde, fec_hasta):
    '''
    Filtra y carga los datos al DataFrame
    fec_desde: fecha inicio
    fecha_hasta: fecha fin
    '''
    global df, k_mag, k_depth
    # cone = create_engine(
    #                 'postgresql://airflow:airflow@localhost:5432/sismosdb', 
    #                 pool_size=50, 
    #                 max_overflow=0)
    
    cone = psycopg2.connect(**st.secrets["postgres"]) 

    qry = (f""" \
        SELECT * FROM sismos  \
        where time between '{fec_desde}' and  '{fec_hasta}' \
        """)

    df = pd.read_sql(sql=qry, con=cone)

    x_mag = df['mag']
    x_depth = df['depth']

    x_mag = np.array(x_mag)
    x_depth = np.array(x_depth)

    x_mag = x_mag.reshape(-1, 1)
    x_depth = x_depth.reshape(-1, 1)

    k_mag_pred = k_mag.predict(x_mag)
    k_depth_pred = k_depth.predict(x_depth)

    df['k_mag'] = k_mag_pred
    df['k_depth'] = k_depth_pred

    for i in range(len(df)):
        # Fuerte
        if df['k_mag'].iloc[i] == 1:
            if df['k_depth'].iloc[i] == 0:
                df.loc[i, 'peligro'] = 2
            if df['k_depth'].iloc[i] == 1:
                df.loc[i, 'peligro'] = 1
            if df['k_depth'].iloc[i] == 2:
                df.loc[i, 'peligro'] = 1

        # Media
        elif df['k_mag'].iloc[i] == 0:
            if df['k_depth'].iloc[i] == 1:
                df.loc[i, 'peligro'] = 1
            if df['k_depth'].iloc[i] == 0:
                df.loc[i, 'peligro'] = 1
            if df['k_depth'].iloc[i] == 2:
                df.loc[i, 'peligro'] = 0

        # Suave
        elif df['k_mag'].iloc[i] == 2:
            if df['k_depth'].iloc[i] == 0:
                df.loc[i, 'peligro'] = 2
            if df['k_depth'].iloc[i] == 1:
                df.loc[i, 'peligro'] = 1
            if df['k_depth'].iloc[i] == 2:
                df.loc[i, 'peligro'] = 0

    # renombramos lng a lon para poder ser utilizado por el mapa de streamlit
    df = df.rename(columns={'lng':'lon'})
    #Para poder poner una etiqueta a los gráficos de líneas
    df['Mag. por día'] = df['mag']
    df['Mag. por mes'] = df['mag']
    df['Mag. por año'] = df['mag']


def main():
    global df

    configPage()

    #colA, colB, colC, colD, colE = st.columns([2.5, 1, 2.5, 1, 2.5])

    # Valores de seteo
    fecha_desde = datetime.datetime(2021, 1, 1)
    fecha_hasta = datetime.datetime.today()
    fecha_max_sel = fecha_hasta

    with st.sidebar:
        fecha_min_sel = st.date_input(
            label='Fecha desde:',
            value=fecha_hasta - datetime.timedelta(days=30),
            min_value=fecha_desde,
            max_value=fecha_max_sel
        )
        
        fecha_max_sel = st.date_input(
            label='Fecha hasta:',
            value=fecha_hasta,
            min_value=fecha_min_sel,
            max_value=fecha_hasta
        )

        cargarDatos(fecha_min_sel, fecha_max_sel)        

        # Cantidad de dias entre las fechas desde y hasta
        lapso = (fecha_max_sel - fecha_min_sel).days

        # Datos para los pie
        df_usa = df[df['idpais'] == 1]
        df_japon = df[df['idpais'] == 2]
        df_chile = df[df['idpais'] == 3]   

  

    #colA, colB, colC, colD, colE = st.columns([3, 1, 3, 1, 3])
    colA, colC,  colE = st.columns([1, 1, 1], gap='large')

    #USA
    with colA:
        st.metric('Máxima magnitud USA', df_usa['mag'].max())

        usa_0 = df_usa[(df_usa['peligro'] == 0)].shape[0]
        usa_1 = df_usa[(df_usa['peligro'] == 1)].shape[0]
        usa_2 = df_usa[(df_usa['peligro'] == 2)].shape[0]
        usa_total = usa_0 + usa_1 + usa_2         
        
        b = round((usa_0 / usa_total) * 100, 2)
        m = round((usa_1 / usa_total) * 100, 2)
        a = round((usa_2 / usa_total) * 100, 2)

        

        fig_1, ax_1 = plt.subplots()  
        ax_1.pie([usa_0, usa_1, usa_2], 
                labels=[f'Amenazas bajas {b}% ({usa_0})', f'Amenazas moderadas {m}% ({usa_1})', f'Amenazas altas {a}% ({usa_2})'], 
                colors=['green', 'yellow', 'red'],                      
                textprops=dict(color="w"))       

        fig_1.set_facecolor('#0E1117')            
        st.pyplot(fig_1) 

        st.container()

        #Evaluamos el lapso de tiempo para agrupars
        if lapso <= 30:
            st.line_chart(df_usa['Mag. por día'].groupby(df_usa['time'].dt.day).max())
        elif lapso > 30 and lapso <= 360:
            st.line_chart(df_usa['Mag. por mes'].groupby(df_usa['time'].dt.month).max())
        elif lapso > 360:
            st.line_chart(df_usa['Mag. por año'].groupby(df_usa['time'].dt.year).max())   
        
    #Japón
    with colC:
        st.metric('Máxima magnitud Japón', df_japon['mag'].max())

        japon_0 = df_japon[(df_japon['peligro'] == 0)].shape[0]
        japon_1 = df_japon[(df_japon['peligro'] == 1)].shape[0]
        japon_2 = df_japon[(df_japon['peligro'] == 2)].shape[0]
        japon_total = japon_0 + japon_1 + japon_2       
        
        b = round((japon_0 / japon_total) * 100, 2)
        m = round((japon_1 / japon_total) * 100, 2)
        a = round((japon_2 / japon_total) * 100, 2)            

        fig_2, ax_2 = plt.subplots()           
        
        ax_2.pie([japon_0, japon_1, japon_2], 
                labels=[f'Amenazas bajas {b}% ({japon_0})', f'Amenazas moderadas {m}% ({japon_1})', f'Amenazas altas {a}% ({japon_2})'],
                colors=['green', 'yellow', 'red'],                
                textprops=dict(color="w")) 

        fig_2.set_facecolor('#0E1117')             
        st.pyplot(fig_2) 

        st.container()

        # Evaluamos el lapso de tiempo para agrupars
        if lapso <= 30:
            st.line_chart(df_japon['Mag. por día'].groupby(df_japon['time'].dt.day).max())
        elif lapso > 30 and lapso <= 360:
            st.line_chart(df_japon['Mag. por mes'].groupby(df_japon['time'].dt.month).max())
        elif lapso > 360:
            st.line_chart(df_japon['Mag. por año'].groupby(df_japon['time'].dt.year).max())
        
    
    #Chile
    with colE:
        st.metric('Máxima magnitud Chile', df_chile['mag'].max())            

        chile_0 = df_chile[(df_chile['peligro'] == 0)].shape[0]
        chile_1 = df_chile[(df_chile['peligro'] == 1)].shape[0]
        chile_2 = df_chile[(df_chile['peligro'] == 2)].shape[0]
        chile_total = chile_0 + chile_1 + chile_2       
        
        b = round((chile_0 / chile_total) * 100, 2)
        m = round((chile_1 / chile_total) * 100, 2)
        a = round((chile_2 / chile_total) * 100, 2)  

        fig_3, ax_3 = plt.subplots()        
        
        ax_3.pie([chile_0, chile_1, chile_2], 
                labels=[f'Amenazas bajas {b}% ({chile_0})', f'Amenazas moderadas {m}% ({chile_1})', f'Amenazas altas {a}% ({chile_2})'],
                colors=['green', 'yellow', 'red'], 
                textprops=dict(color="w"))         
        
        fig_3.set_facecolor('#0E1117')             
        st.pyplot(fig_3)

        st.container()

        # Evaluamos el lapso de tiempo para agrupars
        if lapso <= 30:
            st.line_chart(df_chile['Mag. por día'].groupby(df_chile['time'].dt.day).max())
        elif lapso > 30 and lapso <= 360:
            st.line_chart(df_chile['Mag. por mes'].groupby(df_chile['time'].dt.month).max())
        elif lapso > 360:
            st.line_chart(df_chile['Mag. por año'].groupby(df_chile['time'].dt.year).max())


if __name__ == '__main__':
    main()
