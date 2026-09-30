import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from html import escape


# ============================================================
# CONFIGURACIÓN DE STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Avance Resultados MTY 2",
    layout="wide"
)

st.title("📊 Avance Resultados MTY 2")


# ============================================================
# CONFIGURACIÓN DE GOOGLE SHEETS
# ============================================================

SHEET_ID = "1arev4xR1GoG2ncP4NhZea3ea0NVwDb9q5DUB5qRFUyY"
GID = 404326982


# ============================================================
# CARGA DE DATOS DESDE GOOGLE SHEETS
# ============================================================

@st.cache_data(ttl=300)
def cargar_datos_gspread():
    """
    Conecta con Google Sheets y devuelve los datos
    de la hoja cuyo GID coincida con GID.
    """

    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]

        # Credenciales almacenadas en Streamlit Secrets
        creds_dict = dict(st.secrets["gcp_service_account"])

        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=scopes
        )

        # Autenticación
        gc = gspread.authorize(credentials)

        # Abrir archivo
        sh = gc.open_by_key(SHEET_ID)

        # Buscar la hoja por GID
        worksheet = None

        for ws in sh.worksheets():
            if ws.id == GID:
                worksheet = ws
                break

        # Si no encuentra el GID, usar la primera hoja
        if worksheet is None:
            worksheet = sh.get_worksheet(0)

        # Obtener todos los valores
        data = worksheet.get_all_values()

        # Convertir a DataFrame
        df = pd.DataFrame(data)

        return df

    except Exception as e:
        st.error(
            f"❌ Error al conectar con Google Sheets: {e}"
        )
        return None


# ============================================================
# FUNCIÓN AUXILIAR PARA LEER CELDAS
# ============================================================

def obtener_valor(df, fila, columna):
    """
    Devuelve el valor de una celda como texto.
    Si la celda no existe o está vacía, devuelve "".
    """

    try:
        valor = df.iloc[fila, columna]

        if pd.isna(valor):
            return ""

        # Escapar caracteres especiales para HTML
        return escape(str(valor))

    except (IndexError, TypeError):
        return ""


# ============================================================
# GENERACIÓN DEL DASHBOARD HTML
# ============================================================

def generar_html_dashboard(df):
    """
    Genera el dashboard HTML a partir del DataFrame.
    """

    h = []

    # --------------------------------------------------------
    # ESTILOS CSS
    # --------------------------------------------------------

    h.append("""
<style>

    .dashboard {
        width: 100%;
        font-family: Arial, sans-serif;
    }

    /* Títulos de sección */
    .titulo-seccion {
        font-size: 20px;
        font-weight: bold;
        margin-top: 8px;
        margin-bottom: 3px;
    }

    /* Subtítulo */
    .subtitulo {
        font-size: 11px;
        margin-bottom: 6px;
        color: #555;
    }

    /* Tabla */
    .tabla-dashboard {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 12px;
        table-layout: fixed;
    }

    /* Encabezados */
    .tabla-dashboard th {
        background-color: #1f4e78;
        color: white;
        padding: 5px 4px;
        text-align: center;
        font-size: 11px;
        line-height: 1.1;
        border: 1px solid white;
    }

    /* Celdas */
    .tabla-dashboard td {
        border: 1px solid #d0d0d0;
        padding: 4px 3px;
        text-align: center;
        vertical-align: middle;
        line-height: 1.1;
    }

    /* Etiqueta */
    .dato-label {
        font-size: 10px;
        font-weight: bold;
        margin-bottom: 2px;
        line-height: 1.1;
    }

    /* Valor */
    .dato-valor {
        font-size: 16px;
        font-weight: bold;
        line-height: 1;
    }

    /* Valores del arranque */
    .arranque .dato-valor {
        background-color: #fce4d6;
        padding: 4px 3px;
        border-radius: 4px;
    }

    /* Separación entre tablas */
    .separador {
        height: 5px;
    }

</style>
""")

    # ========================================================
    # CIERRE DEL DÍA
    # ========================================================

    t_cierre = obtener_valor(
        df, 0, 0
    ) or "Cierre del Día"

    h.append(
        f'<div class="titulo-seccion">{t_cierre}</div>'
    )

    # --------------------------------------------------------
    # TABLA DE CIERRE
    # --------------------------------------------------------

    h.append("""
        <table class="tabla-dashboard">
            <thead>
                <tr>
    """)

    columnas_cierre = [0, 3, 6, 9]

    for col in columnas_cierre:
        encabezado = obtener_valor(
            df, 2, col
        )

        h.append(
            f"<th>{encabezado}</th>"
        )

    h.append("""
                </tr>
            </thead>
            <tbody>
    """)

    # Filas de cierre: 3 a 8
    for r in range(3, 9):

        h.append("<tr>")

        for col in columnas_cierre:

            etiqueta = obtener_valor(
                df, r, col
            )

            valor = obtener_valor(
                df, r, col + 1
            )

            h.append(f"""
                <td>
                    <div class="dato-label">
                        {etiqueta}
                    </div>

                    <div class="dato-valor">
                        {valor}
                    </div>
                </td>
            """)

        h.append("</tr>")

    h.append("""
            </tbody>
        </table>
    """)

    # ========================================================
    # ESPACIO ENTRE SECCIONES
    # ========================================================

    h.append(
        '<div class="separador"></div>'
    )

    # ========================================================
    # ARRANQUE DEL DÍA
    # ========================================================

    t_arranque = obtener_valor(
        df, 10, 0
    ) or "Arranque del Día"

    subt = obtener_valor(
        df, 11, 3
    )

    h.append(
        f'<div class="titulo-seccion">{t_arranque}</div>'
    )

    if subt:
        h.append(
            f'<div class="subtitulo">{subt}</div>'
        )

    # --------------------------------------------------------
    # TABLA DE ARRANQUE
    # --------------------------------------------------------

    h.append("""
        <table class="tabla-dashboard arranque">
            <thead>
                <tr>
    """)

    columnas_arranque = [0, 3, 6, 9]

    for col in columnas_arranque:

        encabezado = obtener_valor(
            df, 12, col
        )

        h.append(
            f"<th>{encabezado}</th>"
        )

    h.append("""
                </tr>
            </thead>
            <tbody>
    """)

    # Filas de arranque: 13 a 17
    for r in range(13, 18):

        h.append("<tr>")

        for col in columnas_arranque:

            etiqueta = obtener_valor(
                df, r, col
            )

            valor = obtener_valor(
                df, r, col + 1
            )

            h.append(f"""
                <td>
                    <div class="dato-label">
                        {etiqueta}
                    </div>

                    <div class="dato-valor">
                        {valor}
                    </div>
                </td>
            """)

        h.append("</tr>")

    h.append("""
            </tbody>
        </table>
    """)

    # ========================================================
    # CERRAR CONTENEDOR
    # ========================================================

    h.append("</div>")

    return "".join(h)


# ============================================================
# SIDEBAR / CONTROLES
# ============================================================

st.sidebar.header("Configuración")

if st.sidebar.button("🔄 Actualizar Datos Ahora"):

    st.cache_data.clear()
    st.rerun()


# ============================================================
# CARGAR INFORMACIÓN
# ============================================================

df_sheets = cargar_datos_gspread()


# ============================================================
# RENDERIZAR DASHBOARD
# ============================================================

if df_sheets is not None and not df_sheets.empty:

    tabla_estilizada = generar_html_dashboard(
        df_sheets
    )

    st.html(tabla_estilizada)

else:

    st.warning(
        "⚠️ No se pudieron obtener los datos. "
        "Revisa la conexión con Google Sheets y tus "
        "secretos de Streamlit."
    )
