
# Importación de librerias necesarias.
import streamlit as st
from PIL import Image


st.set_page_config(
        page_title="Earth Data",
        page_icon="🌍",        
        initial_sidebar_state="expanded")


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





fondo_sidebar= imagen_sidebar('https://images.unsplash.com/photo-1559915396-0e919c1f66a9?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY3MDM1ODAwOA&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080')
st.markdown(fondo_sidebar, unsafe_allow_html=True)

st.subheader('Sobre Earth Data')
st.markdown('Chequea el repositorio de nuetro trabajo y el perfil de linkedIn de nuestros integrantes.')       
st.write('[Repositorio GitHUB](https://github.com/oscarmarinoa/Sistema-de-alertas-sismicas---Proyecto-Grupal-DTS04)')  
st.write('---')
    
st.subheader('Equipo Earth Data')

# Fede
with st.container():

    column_izq,  column_cent, column_der = st.columns(3, gap='small')       
    with column_izq:
        image = Image.open(r'src/Fede.jpeg')
        st.image(image, width=130)
        st.write('')
                
    with column_cent:
        st.markdown('Federico Goyechea')
        st.write('[LinkedIn](https://www.linkedin.com/in/federico-goyechea-65361b24a/)')
        st.write('[GitHub](https://github.com/Workitaws)')
        st.write('feditowo0w@gmail.com')
        
# Gise
with st.container():
    
    column_izq,  column_cent, column_der = st.columns(3, gap='small')       
    with column_izq:
        image = Image.open(r'src/Gise.jpeg')
        st.image(image, width=130)
        st.write('')
                
    with column_cent:
        st.markdown('Gisela Sánchez')
        st.write('[LinkedIn](https://www.linkedin.com/in/gisela-s%C3%A1nchez-272b9017a)')
        st.write('[GitHub](https://github.com/sgisela945)')
        st.write('ingiselasanchez@gmail.com')
                     
# Lala
with st.container():

    column_izq,  column_cent, column_der = st.columns(3, gap='small')       
    with column_izq:
        image = Image.open(r'src/Lala.jpeg')
        st.image(image, width=130)
        st.write('')
                
    with column_cent:
        st.markdown('Lala Weber')
        st.write('[GitHub](https://github.com/LalaYupii)')
        st.write('mimundo.lalayupii@gmail.com')
        
# Oscar
with st.container():

    column_izq,  column_cent, column_der = st.columns(3, gap='small')       
    with column_izq:
        image = Image.open(r'src/Oscar.jpeg')
        st.image(image, width=130)
                
    with column_cent:
        st.markdown('Oscar Mario Mariño')
        st.write('[LinkedIn](https://www.linkedin.com/in/oscar-mariño-arias-774098112/)')
        st.write('[GitHub](https://github.com/oscarmarinoa)')
        st.write('oscarmarinoa@gmail.com')