Python
import pandas as pd
import streamlit as st
import time

st.set_page_config(page_title="Resultado Diario MTY 2", layout="wide")

st.title("📊 Monitoreo en Línea - Resultado Diario MTY 2")

# ID de tu Google Sheet y GID de la pestaña específica extraídos de tu URL
SHEET_ID = "1arev4xR1GoG2ncP4NhZea3ea0NVwDb9q5DUB5qRFUyY"
GID = "404326982"

# URL de exportación directa a CSV para una hoja específica de Google Sheets
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=300) # Caché de 5 minutos para no saturar las peticiones, ajustable a tus necesidades
def cargar_datos(url):
    try:
        # Leemos el CSV generado por Google Sheets
        df = pd.read_csv(url, header=None)
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos de Google Sheets: {e}")
        return None

# Controles en la barra lateral
st.sidebar.header("Configuración")
if st.sidebar.button("🔄 Actualizar Datos Ahora"):
    st.cache_data.clear()
    st.rerun()

# Cargar los datos
df_sheets = cargar_datos(csv_url)

if df_sheets is not None:
    st.subheader("Vista General de la Hoja de Google Sheets")
    
    # Mostramos los datos tal cual están estructurados en la hoja de cálculo
    # Al ser una tabla con celdas combinadas y secciones fijas, mostrarla 
    # como tabla de Pandas limpia permite visualizar los bloques de "Cierre del Día" y "Arranque del Día".
    st.dataframe(df_sheets, use_container_width=True)
    
    # Opcional: Si prefieres extraer métricas clave (KPIs) de celdas específicas, 
    # puedes hacerlo mediante índices de Pandas, por ejemplo:
    # meta_area_cierre = df_sheets.iloc[3, 1] # Ejemplo según la posición de la celda
    
else:
    st.warning("No se pudieron obtener los datos en este momento. Verifica que el enlace sea accesible.")