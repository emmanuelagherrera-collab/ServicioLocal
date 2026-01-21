import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_folium import st_folium
import folium
import pandas as pd

# 1. CONFIGURACIÓN MÓVIL: Layout wide para evitar márgenes laterales innecesarios
st.set_page_config(layout="wide", page_title="ServicioLocal")

# Estilo CSS para reducir espacios superiores y mejorar la vista en móvil
st.markdown("""
    <style>
    .main > div { padding-top: 2rem; }
    iframe { width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

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

# 3. FILTRO ADAPTADO A MÓVIL (Ocupa todo el ancho para facilitar el clic)
categorias_disponibles = ["Todas las categorías"] + sorted(df["Categoria"].unique().tolist())
categoria_seleccionada = st.selectbox("¿Qué buscas hoy?", categorias_disponibles)

# Filtrado
if categoria_seleccionada != "Todas las categorías":
    df_filtrado = df[df["Categoria"] == categoria_seleccionada]
else:
    df_filtrado = df

# 4. Crear el Mapa
# Centrado en La Florida. Zoom 13 para ver más área en pantallas pequeñas.
m = folium.Map(location=[-33.523, -70.589], zoom_start=13, zoom_control=True)

for index, row in df_filtrado.iterrows():
    try:
        lat = float(str(row['Latitud']).replace(',', '.'))
        lon = float(str(row['Longitud']).replace(',', '.'))
        
        if pd.notnull(lat) and pd.notnull(lon):
            categoria_actual = row.get('Categoria', 'Otros')
            icon_name = iconos_servicios.get(categoria_actual, "info-sign")
            ig_url = row.get('Instagram', '#')
            
            # Popup con diseño vertical para móvil
            html_popup = f"""
                <div style="font-family: sans-serif; width: 140px; text-align: center;">
                    <b style="font-size: 14px;">{row['Nombre']}</b><br>
                    <span style="color: #007bff; font-size: 11px;">{categoria_actual}</span><br>
                    <i style="color: gray; font-size: 11px;">{row['Servicio']}</i><br><br>
                    <a href="{ig_url}" target="_blank" 
                       style="text-decoration: none; color: white; background-color: #E1306C; 
                              padding: 8px; border-radius: 5px; font-size: 12px; display: block;">
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
            
    except (ValueError, TypeError):
        continue 

# 5. MOSTRAR MAPA: Aumentamos el height a 700 para cubrir la mayoría de la pantalla móvil
st_folium(m, width="100%", height=700, use_container_width=True)