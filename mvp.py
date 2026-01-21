import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_folium import st_folium
import folium
from folium.plugins import LocateControl
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    layout="wide", 
    page_title="ServicioLocal", 
    initial_sidebar_state="collapsed"
)

# CSS AVANZADO: Buscador "Sticky" y limpieza de UI
st.markdown("""
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Eliminar espacio superior */
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }

        /* HACER QUE EL BUSCADOR SE QUEDE ARRIBA (STICKY) */
        div[data-testid="stVerticalBlock"] > div:has(div.stSelectbox) {
            position: sticky;
            top: 0;
            z-index: 1000;
            background-color: white;
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        
        /* Ajuste para que el mapa no se pegue al borde superior */
        .stSelectbox {
            margin-bottom: 0px;
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

# --- INTERFAZ TIPO APP CON BUSCADOR FIJO ---
categorias_disponibles = ["Todas las categorías"] + sorted(df["Categoria"].unique().tolist())

# Este elemento ahora se queda fijo arriba gracias al CSS anterior
categoria_seleccionada = st.selectbox("🔍 Buscar en La Florida", categorias_disponibles)

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
                <div style="font-family: sans-serif; width: 140px; text-align: center;">
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

# Altura ajustada para dejar espacio al buscador fijo
st_folium(m, width="100%", height=700, use_container_width=True)
