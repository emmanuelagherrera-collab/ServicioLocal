import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_folium import st_folium
import folium
from folium.plugins import LocateControl
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

# Configuración de página
st.set_page_config(layout="wide", page_title="ServicioLocal - GPS")

# --- 1. LÓGICA DE GEOLOCALIZACIÓN ---
# Intentamos obtener la posición automáticamente
location_data = streamlit_js_eval(data_key='pos', function_name='getCurrentPosition', component_id='get_pos')

# Coordenadas por defecto (La Florida)
center_lat, center_lon = -33.523, -70.589

if location_data and 'coords' in location_data:
    center_lat = location_data['coords']['latitude']
    center_lon = location_data['coords']['longitude']

# --- 2. INTERFAZ Y DATOS ---
st.title("📍 ServicioLocal")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0) 

# Diccionario de Iconos para categorías
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

# Filtro de categorías
categorias_disponibles = ["Todas las categorías"] + sorted(df["Categoria"].unique().tolist())
categoria_seleccionada = st.selectbox("¿Qué buscas hoy?", categorias_disponibles)

df_filtrado = df if categoria_seleccionada == "Todas las categorías" else df[df["Categoria"] == categoria_seleccionada]

# --- 3. CREACIÓN DEL MAPA ---
m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

# Control de ubicación nativo (Añade el botón de "mira" al mapa)
LocateControl(
    auto_start=False,
    stop_following=True,
    keep_current_zoom_level=True,
    strings={"title": "Muéstrame dónde estoy"}
).add_to(m)

# Marcador del Usuario (Punto Rojo)
if location_data:
    folium.Marker(
        [center_lat, center_lon],
        popup="Tu ubicación actual",
        tooltip="Tú",
        icon=folium.Icon(color="red", icon="user", prefix='fa')
    ).add_to(m)

# Marcadores de Talentos
for index, row in df_filtrado.iterrows():
    try:
        # Limpieza de coordenadas por si vienen con comas desde el Excel
        lat = float(str(row['Latitud']).replace(',', '.'))
        lon = float(str(row['Longitud']).replace(',', '.'))
        
        if pd.notnull(lat) and pd.notnull(lon):
            icon_name = iconos_servicios.get(row['Categoria'], "info-sign")
            ig_url = row.get('Instagram', '#')
            
            # Popup personalizado
            html_popup = f"""
                <div style="font-family: sans-serif; width: 140px; text-align: center;">
                    <b>{row['Nombre']}</b><br>
                    <span style="color: #007bff; font-size: 11px;">{row['Categoria']}</span><br><br>
                    <a href="{ig_url}" target="_blank" 
                       style="text-decoration: none; color: white; background-color: #E1306C; padding: 8px; border-radius: 5px; font-size: 12px; display: block;">
                       Ver Instagram
                    </a>
                </div>
            """
            
            folium.Marker(
                [lat, lon],
                popup=folium.Popup(html_popup, max_width=180),
                tooltip=row['Nombre'],
                icon=folium.Icon(color="blue", icon=icon_name, prefix='fa')
            ).add_to(m)
    except Exception as e:
        continue

# Desplegar el mapa
st_folium(m, width="100%", height=500, use_container_width=True)

# Footer informativo
if not location_data:
    st.caption("Nota: Si no ves tu ubicación, asegúrate de dar permisos de GPS en tu navegador o usa el botón de la mira telescópica en el mapa.")
