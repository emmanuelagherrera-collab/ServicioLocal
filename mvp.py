import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_folium import st_folium
import folium
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide", page_title="ServicioLocal")

# 1. Obtener ubicación del usuario vía GPS
# Esto disparará la pregunta "¿Permitir que esta app acceda a tu ubicación?" en el celular
location_data = streamlit_js_eval(data_key='pos', function_name='getCurrentPosition', component_id='get_pos')

# Coordenadas por defecto (La Florida) si el usuario no da permiso
center_lat, center_lon = -33.523, -70.589

if location_data:
    center_lat = location_data['coords']['latitude']
    center_lon = location_data['coords']['longitude']

st.title("📍 ServicioLocal")

# 2. Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0) 

# Diccionario de Iconos
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

# 3. Filtro
categorias_disponibles = ["Todas las categorías"] + sorted(df["Categoria"].unique().tolist())
categoria_seleccionada = st.selectbox("¿Qué buscas hoy?", categorias_disponibles)

df_filtrado = df if categoria_seleccionada == "Todas las categorías" else df[df["Categoria"] == categoria_seleccionada]

# 4. Crear el Mapa centrado en el Usuario o en La Florida
m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

# Marcador del Usuario (Solo si hay GPS)
if location_data:
    folium.Marker(
        [center_lat, center_lon],
        popup="Tú estás aquí",
        tooltip="Mi ubicación",
        icon=folium.Icon(color="red", icon="user", prefix='fa')
    ).add_to(m)

# 5. Marcadores de Talentos
for index, row in df_filtrado.iterrows():
    try:
        lat = float(str(row['Latitud']).replace(',', '.'))
        lon = float(str(row['Longitud']).replace(',', '.'))
        if pd.notnull(lat) and pd.notnull(lon):
            icon_name = iconos_servicios.get(row['Categoria'], "info-sign")
            ig_url = row.get('Instagram', '#')
            
            html_popup = f"""
                <div style="font-family: sans-serif; width: 140px; text-align: center;">
                    <b>{row['Nombre']}</b><br>
                    <span style="color: #007bff; font-size: 11px;">{row['Categoria']}</span><br><br>
                    <a href="{ig_url}" target="_blank" 
                       style="text-decoration: none; color: white; background-color: #E1306C; padding: 8px; border-radius: 5px; font-size: 12px; display: block;">
                       Instagram
                    </a>
                </div>
            """
            folium.Marker(
                [lat, lon],
                popup=folium.Popup(html_popup, max_width=180),
                tooltip=row['Nombre'],
                icon=folium.Icon(color="blue", icon=icon_name, prefix='fa')
            ).add_to(m)
    except:
        continue 

st_folium(m, width="100%", height=600, use_container_width=True)
