import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_folium import st_folium
import folium
from folium.plugins import LocateControl
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO APP
st.set_page_config(
    layout="wide", 
    page_title="ServicioLocal", 
    initial_sidebar_state="collapsed"
)

# Inyección de CSS para que parezca una App nativa
st.markdown("""
    <style>
        /* Ocultar header y footer de Streamlit */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* Eliminar márgenes y paddings innecesarios */
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
        }
        
        /* Ajustar el contenedor del selectbox para que no flote */
        .stSelectbox {
            margin: 10px;
        }
        
        /* Forzar que el mapa ocupe el resto de la pantalla */
        iframe {
            border-radius: 0px;
        }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE GEOLOCALIZACIÓN ---
location_data = streamlit_js_eval(data_key='pos', function_name='getCurrentPosition', component_id='get_pos')
center_lat, center_lon = -33.523, -70.589
if location_data and 'coords' in location_data:
    center_lat = location_data['coords']['latitude']
    center_lon = location_data['coords']['longitude']

# --- DATOS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0) 

iconos_servicios = {
    "Análisis de Datos": "chart-pie",
    "Soporte Técnico": "laptop",
    "Costuras": "scissors",
    "Gasfitería": "wrench",
    "Carpintería": "hammer",
    "Jardinería": "leaf",
    "Asistencia Administrativa": "briefcase",
    "Cuidado Personal": "heart",
    "Clases Particulares": "graduation-cap",
    "Otros": "info-sign"
}

# --- INTERFAZ TIPO APP ---
# El buscador ahora parece una barra de búsqueda de App
categorias_disponibles = ["Todas las categorías"] + sorted(df["Categoria"].unique().tolist())
categoria_seleccionada = st.selectbox("🔍 Buscar servicio en La Florida", categorias_disponibles)

df_filtrado = df if categoria_seleccionada == "Todas las categorías" else df[df["Categoria"] == categoria_seleccionada]

# --- MAPA ---
m = folium.Map(location=[center_lat, center_lon], zoom_start=15, zoom_control=False)

# Botón de ubicación nativo
LocateControl(auto_start=False, strings={"title": "Mi ubicación"}).add_to(m)

for index, row in df_filtrado.iterrows():
    try:
        lat = float(str(row['Latitud']).replace(',', '.'))
        lon = float(str(row['Longitud']).replace(',', '.'))
        if pd.notnull(lat) and pd.notnull(lon):
            icon_name = iconos_servicios.get(row['Categoria'], "info-sign")
            ig_url = row.get('Instagram', '#')
            
            html_popup = f"""
                <div style="font-family: sans-serif; width: 150px; text-align: center;">
                    <b style="font-size: 14px;">{row['Nombre']}</b><br>
                    <span style="color: #007bff; font-size: 11px;">{row['Categoria']}</span><br><br>
                    <a href="{ig_url}" target="_blank" 
                       style="text-decoration: none; color: white; background-color: #E1306C; padding: 10px; border-radius: 8px; font-size: 12px; display: block; font-weight: bold;">
                       INSTAGRAM
                    </a>
                </div>
            """
            folium.Marker(
                [lat, lon],
                popup=folium.Popup(html_popup, max_width=200),
                tooltip=row['Nombre'],
                icon=folium.Icon(color="blue", icon=icon_name, prefix='fa')
            ).add_to(m)
    except:
        continue

# Mapa a pantalla completa (Ajustado para altura de smartphone)
st_folium(m, width="100%", height=800, use_container_width=True)
