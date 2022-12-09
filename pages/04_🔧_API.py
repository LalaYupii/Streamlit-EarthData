
# Importación de librerias necesarias.
import streamlit as st
import datetime
from datetime import date
import requests
import pandas as pd
from unidecode import unidecode
from PIL import Image



st.set_page_config(
        page_title="Earth Data",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded")

#Título principál de la página
st.title("EARTH DATA")  


def imagen_sidebar(url):
    return f"""
    <style>
    [data-testid="stSidebar"] {{
    background-image: url({url});
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    }}
    </style>
    """


# fondo_sidebar= imagen_sidebar('https://images.unsplash.com/photo-1515879218367-8466d910aaa4?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTYzNDY4MTE4MQ&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080')
# st.markdown(fondo_sidebar, unsafe_allow_html=True)

st.markdown('''
En esta sección podras realizar peticiones a la API para descargar información relacionada con sismos.
La información obtenida puede ser visualizada en como un Dataframe o JSON y descargada en formato CSV.            
            ''')

# Lineas de división
st.write('---')

st.subheader('API Earth Data')

# División en columnas para obtener los filtros usados para la api
column_izq,column_cent, column_der = st.columns(3)

# Característica pais
with column_izq:
    pais = st.radio('Selecciona el pais:',[ 'Todos','Chile', 'Japón', 'Estados Unidos'] )
    pais = unidecode(pais.lower())
    if pais == 'estados unidos':
        pais='usa'

# Característica fecha
with column_cent:
    fecha_min = st.date_input('Fecha minima:',datetime.date(2000,1,1))
    fecha_max = st.date_input('Fecha maxima:', date.today())
    fecha_max = fecha_max.year
    fecha_min = fecha_min.year

# Característica tipo de dato
with column_der:
    tipo = st.radio('En que formato quieres los datos:', ['.csv', '.json'])    

# Característica magnitud
magnitud_min, magnitud_max = st.slider('Magnitud:',0,100,(0,100))
st.write('Los valores de magnitud están una decima por encima. Ejm. Una magnitud de 7.3 en la escala de Richter equivales a 73 en la barra de magnitud.')

# Característica Profundidad
profundidad_min, profundidad_max = st.slider('Profundidad (km):', 0, 800, (100, 700))

# Petición de información a la API
if st.button('Obtener datos'):
    st.write('---')
    
    if pais=='todos':
        if tipo == '.csv':
            url = 'https://api-sismo.onrender.com/sismos/all'
            
            df = pd.DataFrame(requests.get(url).json())
            df = df[['idsismo','mag','depth', 'lat', 'lng','year', 'tsunami', 'idpais','time']]
            df
            st.download_button('Descargar CSV', df.to_csv(index=False).encode('utf-8'), "sismos_filtro.csv",
                "text/csv", key='download-csv')

                  
        else: 
            url = 'https://api-sismo.onrender.com/sismos/all'
            st.json(requests.get(url).json())
    else:   
        if tipo == '.csv':
            url= f'https://api-sismo.onrender.com/sismos/?max_depth={profundidad_max}&min_depth={profundidad_min}&min_mag={round(magnitud_min/10,1)}&max_mag={round(magnitud_max/10,1)}&min_lat=-90&max_lat=90&min_long=-180&max_long=180&min_anio={fecha_min}&max_anio={fecha_max}&pais={pais}'
            
            if requests.get(url).json() == []:
                'No hay resultados que coincidan con los parametros de busqueda.'
            else:
                df = pd.DataFrame(requests.get(url).json())
                df = df[['idsismo','mag','depth', 'lat', 'lng','year', 'tsunami', 'idpais','time']]
                df
                st.download_button('Descargar CSV', df.to_csv(index=False).encode('utf-8'))
        else: 
            url = f'https://api-sismo.onrender.com/sismos/?max_depth={profundidad_max}&min_depth={profundidad_min}&min_mag={round(magnitud_min/10,1)}&max_mag={round(magnitud_max/10,1)}&min_lat=-90&max_lat=90&min_long=-180&max_long=180&min_anio={fecha_min}&max_anio={fecha_max}&pais={pais}'
            
            if requests.get(url).json() == []:
                'No hay resultados que coincidan con los parametros de busqueda.'
            else: st.json(requests.get(url).json())            

st.markdown('''
            Para consultas más detalladas de la base de datos utilizar la interfaz de usuario de nuestro producto.
            ''')
st.write(':point_down:')
st.write('[API Earth Data](https://api-sismo.onrender.com/docs)')
st.write(':point_up_2:')
st.write('---')