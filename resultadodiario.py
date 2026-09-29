import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Resultado Diario MTY 2", layout="wide")

st.title("📊 Monitoreo en Línea - Resultado Diario MTY 2")

SHEET_ID = "1arev4xR1GoG2ncP4NhZea3ea0NVwDb9q5DUB5qRFUyY"
GID = 404326982

@st.cache_data(ttl=300)
def cargar_datos_gspread():
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        creds_dict = dict(st.secrets["gcp_service_account"])
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(credentials)
        sh = gc.open_by_key(SHEET_ID)
        
        worksheet = None
        for ws in sh.worksheets():
            if ws.id == GID:
                worksheet = ws
                break
        if worksheet is None:
            worksheet = sh.get_worksheet(0)

        data = worksheet.get_all_values()
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None

# --- FUNCION PARA CREAR LA INTERFAZ VISUAL ---
def generar_html_dashboard(df):
    """Extrae las celdas del DataFrame y arma una tabla HTML idéntica al Excel"""
    
    def get_val(r, c):
        try:
            val = df.iloc[r, c]
            return val if pd.notna(val) else ""
        except IndexError:
            return ""

    # 1. Cabecera y títulos de Cierre del Día
    html = f"""
