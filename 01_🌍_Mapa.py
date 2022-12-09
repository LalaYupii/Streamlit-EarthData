'''
Página principal de Streamlit
'''

# Importaciones
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import streamlit as st
import pydeck as pdk
from streamlit_metrics import metric, metric_row
import streamlit.components.v1 as components
import folium as folium
import leafmap as leafmap
#import leafmap.foliumap as lf
from streamlit_folium import st_folium, folium_static
import matplotlib.colors as colors
import branca
import branca.colormap as cm
import matplotlib.cm as cm2
from sklearn.cluster import KMeans
import datetime  
import pickle as pkl
import psycopg2 



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


    #cone = psycopg2.connect(**st.secrets["postgres"])

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


def main():
    global df

    val_pais = 0
    val_int = 2 

    # Acciones previas
    configPage()

    # Valores de seteo
    fecha_desde = datetime.datetime(2021, 1, 1)
    fecha_hasta = datetime.datetime.today()
    fecha_max_sel = fecha_hasta

    paises = ['Todos', 'USA', 'Japón', 'Chile']

    intensidades = ['Alta', 'Media', 'Baja']

    # Contenedor principal
    c = st.container()  

    with st.sidebar:
        # título
        st.header(('¿Qué te gustaría ver?'))

        # Filtro de fechas
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


        pais = st.radio('País:', paises)
        if pais == 'Todos':
            val_pais = 0
        if pais == 'USA':
            val_pais = 1
        if pais == 'Japón':
            val_pais = 2
        if pais == 'Chile':
            val_pais = 3

        color = [255, 0, 0]
        intensidad = st.radio('Amenaza:', intensidades)
        if intensidad == 'Alta':
            val_int = 2
            color = [255, 0, 0]
        if intensidad == 'Media':
            val_int = 1
            color = [255, 255, 0]
        if intensidad == 'Baja':
            val_int = 0
            color = [0, 255, 0 ]

        # Mostramos los datos filtrados
        if val_pais != 0:
            datos = df[(df['idpais'] == val_pais) &
                                       (df['peligro'] == val_int) #&
                                       #(df['time'].dt.date >= fecha_min_sel) &
                                       #(df['time'].dt.date <= fecha_max_sel)
                                       ]
        else:
            datos = df[(df['peligro'] == val_int) #&
                                       #(df['time'].dt.date >= fecha_min_sel) &
                                       #(df['time'].dt.date <= fecha_max_sel)
                                       ]
        
    layer = pdk.Layer(
        "ScatterplotLayer",
        datos,
        pickable=True,
        opacity=0.4,
        filled=True,        
        radius_scale=1,
        radius_min_pixels=3,
        radius_max_pixels=6,
        line_width_min_pixels=0.01,
        get_position='[lon, lat]',
        get_fill_color=color,
        get_line_color=[0, 0, 0],
    )
    #zoom=13, min_zoom= 10, max_zoom=30
    # Set the viewport location

    view_state = pdk.ViewState(latitude=30, longitude=25, zoom=1.2, min_zoom=1.2)
        
        #mapbox://styles/mapbox/dark-v11
        #mapbox://styles/mapbox/navigation-day-v1
        #mapbox://styles/mapbox/streets-v12
        #mapbox://styles/mapbox/outdoors-v12
        #mapbox://styles/mapbox/light-v11
        #mapbox://styles/mapbox/satellite-v9
        #mapbox://styles/mapbox/satellite-streets-v12
        #mapbox://styles/mapbox/navigation-day-v1
        # Render   

    r = pdk.Deck(layers=[layer], map_style='mapbox://styles/mapbox/dark-v11',
                initial_view_state=view_state, tooltip={"html": 
                                                                "<b>Magnitud: </b> {mag} <br /> "
                                                                "<b>Profundidad: </b> {depth} <br /> "
                                                                "<b>Longitud: </b> {lon} <br /> "
                                                                "<b>Latitud: </b>{lat} <br /> "
                                                                "<b>Amenaza: </b>{peligro}"})
    


    r

if __name__ == '__main__':
    main()
