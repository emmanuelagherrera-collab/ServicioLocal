import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_folium import st_folium
import folium
from folium.plugins import LocateControl
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(layout="wide", page_title="ServicioLocal", initial_sidebar_state="collapsed")

# Mantener el buscador "Sticky"
st.markdown("""
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container { padding-top: 0rem; padding-bottom: 0rem; }
        div[data-testid="stVerticalBlock"] > div:has(div.stSelectbox) {
            position: sticky; top: 0; z-index: 1000; background-color: white;
            padding: 10px; border-bottom: 1px solid #ddd;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE MEMORIA (Session State) ---
# Inicializamos las coordenadas por defecto si no existen en la memoria
if 'user_lat' not in st.session_state:
    st.session_state.user_lat = -33.523
if 'user_lon' not in st.session_state:
    st.session_state.user_lon = -70.589
if 'gps_detected' not in st.session_state:
    st.session_state.gps_detected = False

# Intentamos capturar el GPS
location_data = streamlit_js_eval(data_key='pos', function_name='getCurrentPosition', component_id='get_pos')

# Si el GPS nos da datos nuevos, los guardamos en la memoria persistente
if location_data and 'coords' in location_data:
    new_lat = location_data['coords']['latitude']
    new_lon = location_data['coords']['longitude']
    
    # Solo actualizamos si la diferencia es significativa para evitar recargas infinitas
    if abs(st.session_state.user_lat - new_lat) > 0.0001:
        st.session_state.user_lat = new_lat
        st.session_state.user_lon = new_lon
        st.session_state.gps_detected = True

# --- 3. DATOS Y FILTROS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0) 

iconos_servicios = {
    "Análisis de Datos": "chart-pie", "Soporte Técnico": "laptop", "Costuras": "scissors",
    "Gasfitería": "wrench", "Carpintería": "hammer", "Jardinería": "leaf",
    "Asistencia Administrativa": "briefcase", "Cuidado Personal": "heart",
    "Clases Particulares": "graduation-cap", "Otros": "info-sign"
}

categorias_disponibles = ["Todas las categorías"] + sorted(df["Categoria"].unique().tolist())
categoria_seleccionada = st.selectbox("🔍 Buscar en La Florida", categorias_disponibles)

df_filtrado = df if categoria_seleccionada == "Todas las categorías" else df[df["Categoria"] == categoria_seleccionada]

# --- 4. MAPA (Usando la memoria st.session_state) ---
# El mapa ahora siempre mirará a la memoria, no a la función de GPS directamente
m = folium.Map(
    location=[st.session_state.user_lat, st.session_state.user_lon], 
    zoom_start=15, 
    zoom_control=False
)

LocateControl(auto_start=False).add_to(m)

# Marcador del Usuario (Solo si se detectó GPS real)
if st.session_state.gps_detected:
    folium.Marker(
        [st.session_state.user_lat, st.session_state.user_lon],
        popup="Tú estás aquí",
        icon=folium.Icon(color="red", icon="user", prefix='fa')
    ).add_to(m)

# Marcadores de Talentos (Bucle estándar)
for index, row in df_filtrado.iterrows():
    try:
        lat = float(str(row['Latitud']).replace(',', '.'))
        lon = float(str(row['Longitud']).replace(',', '.'))
        if pd.notnull(lat) and pd.notnull(lon):
            icon_name = iconos_servicios.get(row['Categoria'], "info-sign")
            ig_url = row.get('Instagram', '#')
            html_popup = f"""
                <div style="font-family: sans-serif; width: 140px; text-align: center;">
                    <b>{row['Nombre']}</b><br><span style="color: #007bff; font-size: 11px;">{row['Categoria']}</span><br><br>
                    <a href="{ig_url}" target="_blank" style="text-decoration: none; color: white; background-color: #E1306C; padding: 10px; border-radius: 8px; font-size: 12px; display: block; font-weight: bold;">INSTAGRAM</a>
                </div>
            """
            folium.Marker([lat, lon], popup=folium.Popup(html_popup, max_width=200), icon=folium.Icon(color="blue", icon=icon_name, prefix='fa')).add_to(m)
    except: continue

st_folium(m, width="100%", height=700, use_container_width=True)
