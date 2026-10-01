import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import datetime
import requests
import zipfile
import io
import numpy as np
import re
import os
import glob
from html import escape
from streamlit_gsheets import GSheetsConnection

# ============================================================
# 1. CONFIGURACIÓN PRINCIPAL DE LA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Monterrey (Seguimiento y Reportes)", 
    page_icon="📊", 
    layout="wide"
)

# Ocultar marcas de agua de Streamlit
ocultar_iconos = """

"""
st.markdown(ocultar_iconos, unsafe_allow_html=True)

# ============================================================
# 2. FUNCIONES - REPORTE TELCEL (EXCLUSIVO MTY )
# ============================================================
estructura_cac = {
    "MONTERREY 1": ["2008604 TCC MON103 COUNTRY4", "2008604 TCC MON103 EXPRESS ESFERA4", "2008604 TCC MON103 EXPRESS NUEVO SUR4", "2008604 TCC MON103 SATELITE4", "2008604 TCC MON103 VALLE ORIENTE4", "2008604 TCC MON104 CUMBRES4", "2008604 TCC MON104 SENDERO LINCOLN4", "2008604 TCC MON104 SERVICIO TECNICO Tlc Y CENTRo", "2008604 TCC MON105 CENTRIKA4", "2008604 TCC MON105 GALERIAS4", "2008604 TCC MON106 CENTRO4", "2008604 TCC MON106 EXPRESS FASHION DRIVE4", "2008604 TCC MON106 EXPRESS HUMBERTO LOBO4", "2008604 TCC MON106 EXPRESS PASEO TEC", "2008604 TCC MON106 EXPRESS VILLAS VALLE4", "2008604 TCC MON106 PUNTO VALLE4", "2008604 TCC MON106 SAN AGUSTIN4"],
    "MONTERREY 2": ["2008604 TCC MON107 EXPOSICION4", "2008604 TCC MON107 GUADALUPE4", "2008604 TCC MON108 ANAHUAC4", "2008604 TCC MON108 EXPRESS PLAZA FIESTA ANAHUAC4", "2008604 TCC MON108 PLAZA BELLA4", "2008604 TCC MON108 SANTA CATARINA4", "2008604 TCC MON109 CITADEL4", "2008604 TCC MON109 LAS AMERICAS4", "2008604 TCC MON110 ESCOBEDO4"],
    "MONTERREY 3": ["2008604 TCC MON111 APODACA4", "2008604 TCC MON111 MTY SUN MALL VIP4", "2008604 TCC MON112 EXPRESS MONTEMORELOS"]
}

catalogo_asesores_mty = {
    "2008604 TCC MON103 COUNTRY4": 22, "2008604 TCC MON103 EXPRESS ESFERA4": 10, "2008604 TCC MON103 EXPRESS NUEVO SUR4": 7, "2008604 TCC MON103 SATELITE4": 14, "2008604 TCC MON103 VALLE ORIENTE4": 14, "2008604 TCC MON104 CUMBRES4": 29, "2008604 TCC MON104 SENDERO LINCOLN4": 30, "2008604 TCC MON104 SERVICIO TECNICO Tlc Y CENTRo": 19, "2008604 TCC MON105 CENTRIKA4": 15, "2008604 TCC MON105 GALERIAS4": 25, "2008604 TCC MON106 CENTRO4": 24, "2008604 TCC MON106 EXPRESS FASHION DRIVE4": 6, "2008604 TCC MON106 EXPRESS HUMBERTO LOBO4": 13, "2008604 TCC MON106 EXPRESS PASEO TEC": 7, "2008604 TCC MON106 EXPRESS VILLAS VALLE4": 4, "2008604 TCC MON106 PUNTO VALLE4": 11, "2008604 TCC MON106 SAN AGUSTIN4": 18,
    "2008604 TCC MON107 EXPOSICION4": 20, "2008604 TCC MON107 GUADALUPE4": 28, "2008604 TCC MON108 ANAHUAC4": 20, "2008604 TCC MON108 EXPRESS PLAZA FIESTA ANAHUAC4": 8, "2008604 TCC MON108 PLAZA BELLA4": 27, "2008604 TCC MON108 SANTA CATARINA4": 23, "2008604 TCC MON109 CITADEL4": 25, "2008604 TCC MON109 LAS AMERICAS4": 20, "2008604 TCC MON110 ESCOBEDO4": 20,
    "2008604 TCC MON111 APODACA4": 26, "2008604 TCC MON111 MTY SUN MALL VIP4": 20, "2008604 TCC MON112 EXPRESS MONTEMORELOS": 7
}

nombres_simples_mty = {
    "2008604 TCC MON103 COUNTRY4": "COUNTRY",
    "2008604 TCC MON103 EXPRESS ESFERA4": "EXPRESS ESFERA",
    "2008604 TCC MON103 EXPRESS NUEVO SUR4": "EXPRESS NUEVO SUR",
    "2008604 TCC MON103 SATELITE4": "SATELITE",
    "2008604 TCC MON103 VALLE ORIENTE4": "VALLE ORIENTE",
    "2008604 TCC MON104 CUMBRES4": "CUMBRES",
    "2008604 TCC MON104 SENDERO LINCOLN4": "SENDERO LINCOLN",
    "2008604 TCC MON104 SERVICIO TECNICO Tlc Y CENTRo": "SERVICIO TECNICO Tlc Y CENTRo",
    "2008604 TCC MON105 CENTRIKA4": "CENTRIKA",
    "2008604 TCC MON105 GALERIAS4": "GALERIAS",
    "2008604 TCC MON106 CENTRO4": "CENTRO",
    "2008604 TCC MON106 EXPRESS FASHION DRIVE4": "EXPRESS FASHION DRIVE",
    "2008604 TCC MON106 EXPRESS HUMBERTO LOBO4": "EXPRESS HUMBERTO LOBO",
    "2008604 TCC MON106 EXPRESS PASEO TEC": "EXPRESS PASEO TEC",
    "2008604 TCC MON106 EXPRESS VILLAS VALLE4": "EXPRESS VILLAS VALLE",
    "2008604 TCC MON106 PUNTO VALLE4": "PUNTO VALLE",
    "2008604 TCC MON106 SAN AGUSTIN4": "SAN AGUSTIN",
    "2008604 TCC MON107 EXPOSICION4": "EXPOSICION",
    "2008604 TCC MON107 GUADALUPE4": "GUADALUPE",
    "2008604 TCC MON108 ANAHUAC4": "ANAHUAC",
    "2008604 TCC MON108 EXPRESS PLAZA FIESTA ANAHUAC4": "EXPRESS PLAZA FIESTA ANAHUAC",
    "2008604 TCC MON108 PLAZA BELLA4": "PLAZA BELLA",
    "2008604 TCC MON108 SANTA CATARINA4": "SANTA CATARINA",
    "2008604 TCC MON109 CITADEL4": "CITADEL",
    "2008604 TCC MON109 LAS AMERICAS4": "LAS AMERICAS",
    "2008604 TCC MON110 ESCOBEDO4": "ESCOBEDO",
    "2008604 TCC MON111 APODACA4": "APODACA",
    "2008604 TCC MON111 MTY SUN MALL VIP4": "SUN MALL VIP",
    "2008604 TCC MON112 EXPRESS MONTEMORELOS": "MONTEMORELOS"
}

def colorear_semaforo(val):
    if isinstance(val, str): return ''
    if val >= 0.80: color = '#28a745'
    elif val >= 0.50: color = '#ffc107'
    else: color = '#dc3545'
    return f'color: {color}; font-weight: bold;'

def generar_boton_descarga_telcel(df, nombre_archivo, btn_key):
    try:
        df_export = df.copy()
        if 'Avance' in df_export.columns:
            df_export['Avance'] = pd.to_numeric(df_export['Avance'], errors='coerce').fillna(0)
            df_export['Avance'] = df_export['Avance'].apply(lambda x: f"{x:.0%}")
            
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Resultados')
        excel_data = output.getvalue()
        
        st.download_button(
            label=f"📥 Descargar {nombre_archivo}.xlsx",
            data=excel_data,
            file_name=f"{nombre_archivo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=btn_key
        )
    except Exception as e:
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Descargar {nombre_archivo} (CSV)",
            data=csv_data,
            file_name=f"{nombre_archivo}.csv",
            mime="text/csv",
            key=f"{btn_key}_csv"
        )

def cargar_datos_telcel(archivo):
    df_temp = pd.read_excel(archivo, sheet_name="Detalle1", header=2)
    if 'NOM_ESTRATEGIA' in df_temp.columns: return df_temp
    return pd.read_excel(archivo, sheet_name="Detalle1")

@st.cache_data(ttl=600)
def obtener_archivo_clarodrive_telcel():
    url_carpeta = "https://i0000.clarodrive.com/s/FSXKpraaEE8owPZ"
    url_descarga = url_carpeta.rstrip('/') + '/download'
    try:
        respuesta = requests.get(url_descarga, timeout=15)
        if respuesta.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(respuesta.content)) as archivo_zip:
                excel_infos = [info for info in archivo_zip.infolist() if info.filename.endswith('.xlsx') and not info.filename.startswith('~')]
                if excel_infos:
                    excel_reciente = max(excel_infos, key=lambda x: x.date_time)
                    archivo_bytes = io.BytesIO(archivo_zip.read(excel_reciente.filename))
                    
                    fecha_tupla = excel_reciente.date_time 
                    fecha_utc = datetime.datetime(
                        year=fecha_tupla[0], month=fecha_tupla[1], day=fecha_tupla[2],
                        hour=fecha_tupla[3], minute=fecha_tupla[4], second=fecha_tupla[5]
                    )
                    fecha_mexico = fecha_utc - datetime.timedelta(hours=6)
                    fecha_str = fecha_mexico.strftime('%d/%m/%Y %H:%M:%S')
                    return archivo_bytes.getvalue(), excel_reciente.filename, fecha_str
    except Exception:
        pass
    return None, None, None


# ============================================================
# 3. CREACIÓN DEL MENÚ SUPERIOR
# ============================================================
st.title("Monterrey (Seguimiento y Reportes)")

seleccion = option_menu(
    menu_title=None, 
    options=["Resultados Diarios", "Reporte Telcel", "Tablero Bolsas"],
    icons=["bar-chart-line", "phone", "briefcase"], 
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "18px"}, 
        "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#024B7A"}, 
    }
)
st.markdown("---")

# ============================================================
# 4. VISTAS DE LA APLICACIÓN
# ============================================================

def mostrar_resultados_diarios():


    # ============================================================
    # CONFIGURACIÓN DE STREAMLIT
    # ============================================================


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
        de la hoja cuyo GID coincida con GID, junto con la hora de actualización.
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

            # Capturar la hora exacta de lectura en Monterrey
            hora_extrac = pd.Timestamp.now(tz="America/Monterrey").strftime("%d/%m/%Y a las %I:%M %p")

            return df, hora_extrac

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

        .titulo-seccion {
            font-size: 20px;
            font-weight: bold;
            margin-top: 8px;
            margin-bottom: 3px;
        }

        .subtitulo {
            font-size: 11px;
            margin-bottom: 6px;
            color: #555;
        }

        .tabla-dashboard {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 12px;
            table-layout: fixed;
        }

        .tabla-dashboard th {
            background-color: #1f4e78;
            color: white;
            padding: 5px 4px;
            text-align: center;
            font-size: 11px;
            line-height: 1.1;
            border: 1px solid white;
        }

        .tabla-dashboard td {
            border: 1px solid #d0d0d0;
            padding: 4px 3px;
            text-align: center;
            vertical-align: middle;
            line-height: 1.1;
        }

        .dato-label {
            font-size: 10px;
            font-weight: bold;
            margin-bottom: 2px;
            line-height: 1.1;
        }

        .dato-valor {
            font-size: 16px;
            font-weight: bold;
            line-height: 1;
        }

        /* CIERRE = CREMA */
        .cierre .dato-valor {
            background-color: #fce4d6;
            padding: 4px 3px;
            border-radius: 4px;
        }

        /* ARRANQUE = VERDE */
        .arranque .dato-valor {
            background-color: #d9ead3;
            padding: 4px 3px;
            border-radius: 4px;
        }

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
        <table class="tabla-dashboard cierre">
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

    resultado = cargar_datos_gspread()


    # ============================================================
    # RENDERIZAR DASHBOARD
    # ============================================================

    if resultado is not None:

        df_sheets, hora_actualizacion = resultado

        if not df_sheets.empty:

            st.markdown(
                f"**⏱️ Última lectura de datos:** `{hora_actualizacion}`"
            )

            tabla_estilizada = generar_html_dashboard(df_sheets)

            st.html(tabla_estilizada)

        else:

            st.info(
                "ℹ️ La conexión fue exitosa, pero "
                "la hoja de Google Sheets está vacía."
            )

    else:

        st.warning(
            "⚠️ No se pudieron obtener los datos. "
            "Revisa la conexión con Google Sheets y tus "
            "secretos de Streamlit."
        )


def mostrar_reporte_telcel():

    st.subheader("📱 Reporte Telcel - Monterrey")

    # ============================================================
    # DESCARGA AUTOMÁTICA
    # ============================================================

    bytes_automatico, nombre_corto, fecha_actualizacion = (
        obtener_archivo_clarodrive_telcel()
    )

    archivo_a_procesar_telcel = None

    col1, col2 = st.columns([2, 1])

    with col1:

        if bytes_automatico:

            archivo_automatico = io.BytesIO(bytes_automatico)

            st.success(
                f"☁️ **Base de datos (Claro Drive):** {nombre_corto}  \n"
                f"⏱️ **Actualizado:** {fecha_actualizacion}"
            )

            archivo_a_procesar_telcel = archivo_automatico

        else:

            st.warning(
                "⚠️ No se pudo conectar con Claro Drive "
                "o la carpeta está vacía."
            )

    with col2:

        usar_manual = st.checkbox(
            "Subir archivo manualmente",
            value=False if bytes_automatico else True,
            key="telcel_subir_manual"
        )

    if usar_manual:

        archivo_a_procesar_telcel = st.file_uploader(
            "Arrastra aquí tu archivo de Excel (Telcel)",
            type=["xlsx", "xls"],
            key="telcel_uploader"
        )

    # ============================================================
    # SI NO HAY ARCHIVO
    # ============================================================

    if not archivo_a_procesar_telcel:

        st.info("Esperando archivo de Telcel...")

        return

    # ============================================================
    # CARGAR ARCHIVO
    # ============================================================

    try:

        df_telcel = cargar_datos_telcel(
            archivo_a_procesar_telcel
        )

    except Exception as e:

        st.error(
            f"❌ Error al leer el archivo de Telcel: {e}"
        )

        return

    # ============================================================
    # LIMPIEZA BÁSICA
    # ============================================================

    df_telcel.columns = df_telcel.columns.str.strip()

    if "NOM_ESTRATEGIA" not in df_telcel.columns:

        st.error(
            "❌ La columna 'NOM_ESTRATEGIA' "
            "no existe en el archivo."
        )

        return

    df_telcel["NOM_ESTRATEGIA"] = (
        df_telcel["NOM_ESTRATEGIA"]
        .astype(str)
        .str.strip()
    )

    # ============================================================
    # FILTROS LATERALES
    # ============================================================

    st.sidebar.divider()

    st.sidebar.header("🎛️ Filtros Telcel")

    # ============================================================
    # FILTRO DE MES
    # ============================================================

    if "MES_CAPTURA" in df_telcel.columns:

        df_telcel["MES_CAPTURA"] = pd.to_datetime(
            df_telcel["MES_CAPTURA"],
            errors="coerce"
        )

        meses_disponibles = sorted(
            df_telcel["MES_CAPTURA"]
            .dt.month
            .dropna()
            .unique()
            .astype(int)
            .tolist()
        )

        mes_actual = datetime.datetime.now().month

        if mes_actual in meses_disponibles:

            default_index = meses_disponibles.index(
                mes_actual
            )

        else:

            default_index = (
                len(meses_disponibles) - 1
                if meses_disponibles
                else 0
            )

        if meses_disponibles:

            mes_seleccionado = st.sidebar.selectbox(
                "📅 Mes de Captura:",
                meses_disponibles,
                index=default_index,
                key="telcel_mes"
            )

            df_filtrado_t = df_telcel[
                df_telcel["MES_CAPTURA"].dt.month
                == mes_seleccionado
            ].copy()

        else:

            df_filtrado_t = df_telcel.copy()

    else:

        df_filtrado_t = df_telcel.copy()

    # ============================================================
    # FILTRO DE ÁREAS
    # ============================================================

    areas_telcel = [
        "MONTERREY 1",
        "MONTERREY 2",
        "MONTERREY 3"
    ]

    areas_seleccionadas = st.sidebar.multiselect(
        "🏢 Áreas a visualizar:",
        options=areas_telcel,

        # POR DEFECTO:
        default=["MONTERREY 2"],

        key="telcel_areas"
    )

    # ============================================================
    # VALIDACIÓN
    # ============================================================

    if not areas_seleccionadas:

        st.warning(
            "⚠️ Selecciona al menos un área."
        )

        return

    # ============================================================
    # INFORMACIÓN DEL FILTRO
    # ============================================================

    st.caption(
        "Filtros activos → "
        f"Mes: {mes_seleccionado if 'mes_seleccionado' in locals() else 'Todos'} | "
        f"Áreas: {', '.join(areas_seleccionadas)}"
    )

    # ============================================================
    # FUNCIÓN PARA GENERAR TABLA DE CADA ÁREA
    # ============================================================

    def generar_tabla_area_telcel(area):

        cacs_area = estructura_cac.get(
            area,
            []
        )

        if not cacs_area:

            st.warning(
                f"⚠️ No hay CAC configurados para {area}."
            )

            return

        # --------------------------------------------------------
        # FILTRAR SOLO CAC DEL ÁREA
        # --------------------------------------------------------

        df_area = df_filtrado_t[
            df_filtrado_t["NOM_ESTRATEGIA"].isin(cacs_area)
        ].copy()

        # --------------------------------------------------------
        # RESUMEN
        # --------------------------------------------------------

        resumen_cacs = (
            df_area
            .groupby("NOM_ESTRATEGIA")
            .size()
            .reset_index(name="Avance Mes")
        )

        datos_area = []

        total_avance = 0
        total_asesores = 0
        total_meta = 0

        # --------------------------------------------------------
        # GENERAR CADA CAC
        # --------------------------------------------------------

        for cac in cacs_area:

            avance_fila = resumen_cacs[
                resumen_cacs["NOM_ESTRATEGIA"] == cac
            ]

            if not avance_fila.empty:

                avance = int(
                    avance_fila["Avance Mes"].iloc[0]
                )

            else:

                avance = 0

            asesores = catalogo_asesores_mty.get(
                cac,
                0
            )

            meta = asesores * 2

            porcentaje = (
                avance / meta
                if meta > 0
                else 0
            )

            nombre_mostrar = nombres_simples_mty.get(
                cac,
                cac
            )

            datos_area.append({

                "Area/CAC":
                    nombre_mostrar,

                "Avance Mes":
                    avance,

                "Asesores":
                    asesores,

                "Meta":
                    meta,

                "Avance":
                    porcentaje
            })

            total_avance += avance
            total_asesores += asesores
            total_meta += meta

        # --------------------------------------------------------
        # PORCENTAJE TOTAL DEL ÁREA
        # --------------------------------------------------------

        total_porcentaje = (
            total_avance / total_meta
            if total_meta > 0
            else 0
        )

        # --------------------------------------------------------
        # INSERTAR TOTAL AL PRINCIPIO
        # --------------------------------------------------------

        datos_area.insert(
            0,
            {
                "Area/CAC":
                    f"[-] {area} (TOTAL)",

                "Avance Mes":
                    total_avance,

                "Asesores":
                    total_asesores,

                "Meta":
                    total_meta,

                "Avance":
                    total_porcentaje
            }
        )

        # --------------------------------------------------------
        # DATAFRAME FINAL
        # --------------------------------------------------------

        df_area_final = pd.DataFrame(
            datos_area
        )

        # --------------------------------------------------------
        # TÍTULO DEL ÁREA
        # --------------------------------------------------------

        st.markdown("---")

        st.subheader(
            f"📊 {area}"
        )

        # --------------------------------------------------------
        # TABLA
        # --------------------------------------------------------

        altura_tabla = (
            (len(df_area_final) + 1) * 35 + 3
        )

        st.dataframe(

            df_area_final.style
            .format({
                "Avance": "{:.0%}"
            })
            .map(
                colorear_semaforo,
                subset=["Avance"]
            ),

            width="content",

            hide_index=True,

            height=altura_tabla,

            column_config={

                "Avance": st.column_config.ProgressColumn(

                    "Avance",

                    help="Cumplimiento de la meta",

                    format="%.2f",

                    min_value=0,

                    max_value=1
                )
            }
        )

        # --------------------------------------------------------
        # DETALLE DE DESCARGA
        # --------------------------------------------------------

        df_detalle_area = df_filtrado_t[
            df_filtrado_t["NOM_ESTRATEGIA"].isin(
                cacs_area
            )
        ].copy()

        generar_boton_descarga_telcel(

            df_detalle_area,

            f"Detalle_{area.replace(' ', '_')}",

            f"btn_descarga_{area.replace(' ', '_').lower()}"
        )

    # ============================================================
    # MOSTRAR ÁREAS SELECCIONADAS
    # ============================================================

    for area in areas_seleccionadas:

        generar_tabla_area_telcel(
            area
        )


def mostrar_tablero_bolsas():
        #

    # 2. FUNCIÓN DE EXTRACCIÓN CON ANTI-BLOQUEO
    @st.cache_data(ttl=3600, show_spinner=False)  
    def obtener_base_fielders_clarodrive():
        # Simulamos ser un navegador (Headers) para evitar rechazos de Clarodrive
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
        url = "https://i0000.clarodrive.com/s/9LdJSbwx9yBC5mi/download"

        res = requests.get(url, headers=headers)
        res.raise_for_status()

        # Manejo dinámico de ZIP o Excel directo
        try:
            with zipfile.ZipFile(io.BytesIO(res.content)) as z:
                archivos_xlsx = [f for f in z.infolist() if f.filename.lower().endswith('.xlsx')]
                if archivos_xlsx:
                    archivos_xlsx.sort(key=lambda x: x.date_time)
                    with z.open(archivos_xlsx[-1]) as f:
                        contenido_excel = f.read()
                else:
                    contenido_excel = res.content
        except zipfile.BadZipFile:
            contenido_excel = res.content

        # Leemos fila 3 (header=2) y estrictamente las columnas P y Y
        df_ext = pd.read_excel(
            io.BytesIO(contenido_excel), 
            sheet_name='Detalle1', 
            header=2, 
            usecols="P,Y" 
        )
        # Renombramos a la fuerza para ignorar errores
        df_ext.columns = ['osalta', 'NOM_ESTRATEGIA']
        return df_ext

    # ---------------------------------------------------------
    # 🎨 ESTILOS CORPORATIVOS (OCULTAR ICONOS DE STREAMLIT/GITHUB)
    # ---------------------------------------------------------
    ocultar_iconos = """
    <style>
    /* 1. Ocultar pie de página (marca de agua de Streamlit) */
    footer {
        display: none !important;
    }

    /* 2. Ocultar el espacio en blanco que deja el encabezado al desaparecer */
    .stApp > header {
        background-color: transparent !important;
    }
    </style>
    """
    st.markdown(ocultar_iconos, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🎛️ FILTROS LATERALES DEL TABLERO
    # ---------------------------------------------------------
    st.sidebar.header("🎛️ Filtros del Tablero Bolsas")
    st.sidebar.caption("Por defecto: Monterrey 2")

    region_seleccionada = st.sidebar.selectbox(
        "📍 Región:",
        ["Monterrey", "Tamaulipas"],
        index=0,
        key="tablero_region"
    )
    # ---------------------------------------------------------

    # --- INYECCIÓN DE CSS PARA COMPACTAR, ESCALAR Y HACER RESPONSIVAS LAS TABLAS ---
    st.markdown("""
        <style>
            /* 💻 ESTILOS GENERALES */
            [data-testid="stTable"] { 
                width: max-content !important; 
                max-width: 100%; 
                overflow-x: auto; 
                font-size: 85% !important;
                color: black !important;
            }
            [data-testid="stTable"] table { width: auto !important; }

            /* 👇 SOLO centrar los encabezados superiores (Columnas) */
            [data-testid="stTable"] thead th {
                text-align: center !important;
                vertical-align: middle !important;
            }

            /* 👇 Mantener a la izquierda la columna de CTs (Índices) */
            [data-testid="stTable"] tbody th {
                text-align: left !important;
            }

            [data-testid="stTable"] th, [data-testid="stTable"] td {
                white-space: nowrap !important;
                padding: 5px 10px !important;
                color: black !important;
            }

            /* 📱 ESTILOS PARA CELULARES */
            @media (max-width: 768px) {
                [data-testid="stTable"] th, [data-testid="stTable"] td {
                    font-size: 10px !important; 
                    padding: 4px 6px !important;
                    color: black !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # ☁️ LÓGICA DE DETECCIÓN AUTOMÁTICA (CLARO DRIVE)
    # ---------------------------------------------------------
    def obtener_archivo_clarodrive():
        # Truco de ClaroDrive: Agregamos /download a tu liga para bajar la carpeta
        url_carpeta = "https://i0000.clarodrive.com/s/KRrAxbKcriJiwcK"
        url_descarga = url_carpeta.rstrip('/') + '/download'

        try:
            respuesta = requests.get(url_descarga, timeout=15)
            if respuesta.status_code == 200:
                # Leemos el archivo ZIP directamente en la memoria del servidor
                with zipfile.ZipFile(io.BytesIO(respuesta.content)) as archivo_zip:
                    # Buscamos todos los archivos Excel (ignorando los temporales que empiezan con ~)
                    excel_infos = [info for info in archivo_zip.infolist() if info.filename.endswith('.xlsx') and not info.filename.startswith('~')]

                    if excel_infos:
                        # Si hay varios, tomamos el más reciente por fecha de modificación
                        excel_reciente = max(excel_infos, key=lambda x: x.date_time)

                        # Lo extraemos a la memoria
                        archivo_bytes = io.BytesIO(archivo_zip.read(excel_reciente.filename))

                        # =========================================================
                        # 🕒 AJUSTE DE ZONA HORARIA (UTC A CENTRO DE MÉXICO)
                        # =========================================================
                        fecha_tupla = excel_reciente.date_time 

                        # 1. Convertimos la tupla del ZIP a un formato de fecha manipulable
                        fecha_utc = datetime.datetime(
                            year=fecha_tupla[0], month=fecha_tupla[1], day=fecha_tupla[2],
                            hour=fecha_tupla[3], minute=fecha_tupla[4], second=fecha_tupla[5]
                        )

                        # 2. Le restamos 6 horas (Diferencia de México respecto a UTC)
                        fecha_mexico = fecha_utc - datetime.timedelta(hours=6)

                        # 3. Lo convertimos al texto final
                        fecha_str = fecha_mexico.strftime('%d/%m/%Y %H:%M:%S')
                        # =========================================================

                        return archivo_bytes, excel_reciente.filename, fecha_str
        except Exception:
            pass # Si falla el internet del servidor o la liga, no rompe el programa

        return None, None, None

    archivo_automatico, nombre_corto, fecha_actualizacion = obtener_archivo_clarodrive()
    archivo_a_procesar = None

    col1, col2 = st.columns([2, 1])
    with col1:
        if archivo_automatico:
            st.success(f"☁️ **Base de datos (Sharepoint):** {nombre_corto}  \n⏱️ **Actualizado:** {fecha_actualizacion}")
            archivo_a_procesar = archivo_automatico
        else:
            st.warning("⚠️ No se pudo conectar con Claro Drive o la carpeta está vacía.")

    with col2:
        # Si Claro Drive falla, habilitamos la subida manual como "Plan B"
        usar_manual = st.checkbox("Subir archivo manualmente", value=False if archivo_automatico else True)

    if usar_manual:
        archivo_a_procesar = st.file_uploader("Arrastra aquí tu archivo de Excel", type=['xlsx'])
    
    st.divider ()
    
    # ---------------------------------------------------------
    # PROCESAMIENTO GENERAL
    # ---------------------------------------------------------
    if archivo_a_procesar is not None:
        datos_listos = False
        with st.spinner(f"⏳ Estructurando datos para {region_seleccionada}..."):
            try:
                df = pd.read_excel(archivo_a_procesar, sheet_name='Detalle')
                df.columns = df.columns.str.strip()

                # Limpieza Básica
                columnas_clave = ['ULTIMOS_6_MESES', 'ESTATUS_AGR_N2', 'ESTATUS_AGR_N1', 'ETAPA_OS', 'PORTABILIDAD', 'TIPO_MOVIMIENTO', 'ESTATUS_OS']
                for col in columnas_clave:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.strip().str.upper()

                # 🧹 1. FILTRO DE ESTATUS: Conservar solo PENDIENTES
                if 'ESTATUS_OS' in df.columns:
                    df = df[df['ESTATUS_OS'] == 'PENDIENTE']

                # 🧹 2. FILTRO DE CT Y "PASES VIP" PARA BLANCOS
                if 'CT' in df.columns:
                    df = df[df['CT'].astype(str).str.upper() != 'CT TULANCINGO']

                    es_ct_vacio = df['CT'].isna() | (df['CT'].astype(str).str.strip() == '')

                    estatus_n2 = df['ESTATUS_AGR_N2'].astype(str).str.upper()
                    pase_vip = estatus_n2.str.contains('4 EN VALIDACION') | estatus_n2.str.contains('6. PENDIENTE')

                    df = df[~es_ct_vacio | (es_ct_vacio & pase_vip)]

                    df['CT'] = df['CT'].fillna('SIN CT')
                    df.loc[df['CT'].astype(str).str.strip() == '', 'CT'] = 'SIN CT'

                # =========================================================
                # 🗺️ LÓGICA DE RUTEO POR REGIÓN
                # =========================================================
                if region_seleccionada == "Monterrey":
                    diccionario_ct_area = {
                        "CT SANTA FE [MTY]": "MONTERREY 2", "CT UNIVERSIDAD (NL)": "MONTERREY 2", "CT LA SILLA": "MONTERREY 2",
                        "CT PUENTES": "MONTERREY 2", "CT SANTA CATARINA": "MONTERREY 2",
                        "CT REVOLUCION": "MONTERREY 1", "CT LINCOLN": "MONTERREY 1", "CT SAN PEDRO [NL]": "MONTERREY 1",
                        "CT COLON (MTY)": "MONTERREY 1", "CT GONZALITOS": "MONTERREY 1",
                        "CT GENERAL ESCOBEDO (BRISAS)": "MONTERREY 3", "CT CADEREYTA": "MONTERREY 3",
                        "CT MONTEMORELOS": "MONTERREY 3", "CT APODACA": "MONTERREY 3", "CT LINARES": "MONTERREY 3"
                    }
                    df['AREA_CORREGIDA'] = df['CT'].map(diccionario_ct_area).fillna(df.get('AREA', "ÁREA NO DEFINIDA"))
                    df = df[df['AREA_CORREGIDA'].isin(["MONTERREY 1", "MONTERREY 2", "MONTERREY 3"])]

                elif region_seleccionada == "Tamaulipas":
                    df['AREA_TEMP'] = df.get('AREA', '').astype(str).str.strip().str.upper()
                    diccionario_tam = {
                        "MATAMOROS": "MATAMOROS-REYNOSA",
                        "REYNOSA": "MATAMOROS-REYNOSA",
                        "CD VICTORIA": "CIUDAD VICTORIA",
                        "CD. VICTORIA": "CIUDAD VICTORIA",
                        "VICTORIA": "CIUDAD VICTORIA"
                    }
                    df['AREA_CORREGIDA'] = df['AREA_TEMP'].map(diccionario_tam).fillna(df['AREA_TEMP'])
                    df = df[df['AREA_CORREGIDA'].isin(["CIUDAD VICTORIA", "NUEVO LAREDO", "MATAMOROS-REYNOSA", "TAMPICO"])]
                # =========================================================

                # Rangos
                if 'DIL2' in df.columns:
                    df['DIL2'] = pd.to_numeric(df['DIL2'], errors='coerce')
                    cortes = [-float('inf'), 2, 5, 10, 20, 50, 100, float('inf')]
                    etiquetas = ['0 A 2', '3 A 5', '6 A 10', '11 A 20', '21 A 50', '51 A 100', '> 100']
                    df['Rango x Dil'] = pd.cut(df['DIL2'], bins=cortes, labels=etiquetas).astype(str).replace('nan', 'Sin Rango')

                datos_listos = True
            except Exception as e:
                st.error(f"Error al procesar los datos: {e}")
                st.stop()

        if datos_listos:
            orden_columnas = ['0 A 2', '3 A 5', '6 A 10', '11 A 20', '21 A 50', '51 A 100', '> 100', 'Sin Rango', 'Total']

            # =========================================================================
            # 🏗️ DICCIONARIO MAESTRO EXTRACTO DE 'Relacion MTY.xlsx' (242 RUTAS)
            # =========================================================================
            diccionario_tiendas = {
                '95L': 'CAT GES', 'AAB': 'CAT ALL', 'ACE': 'CAT GPE', 'AFO': 'CAT BRI', 
                'AIG': 'CAT SCA', 'AKA': 'CAT LIN', 'ALL': 'CAT ALL', 'AMB': 'CAT STD', 
                'ANA': 'CAT PUN', 'AOQ': 'CAT STD', 'APO': 'CAT STD', 'AUU': 'CAT BRI', 
                'BDA': 'CAT GES', 'BES': 'CAT GES', 'BIT': 'CAT CAD', 'BKL': 'CAT ECE', 
                'BLN': 'CAT SFE', 'BLX': 'CAT LIN', 'BQN': 'CAT BRI', 'BQS': 'CAT CAD', 
                'BRI': 'CAT BRI', 'BSD': 'CAT STD', 'CAD': 'CAT CAD', 'CAR': 'CAT CUA', 
                'CBT': 'CAT VVE', 'CEX': 'CAT GPE', 'CGL': 'CAT MOM', 'CHN': 'CAT CAD', 
                'CIE': 'CAT STD', 'CMT': 'CAT SCA', 'CPI': 'CAT GES', 'CPQ': 'CAT VAE', 
                'CRB': 'CAT SFE', 'CRV': 'CAT SCA', 'CTB': 'CAT GES', 'CUA': 'CAT CUA', 
                'CVY': 'CAT SCA', 'DAG': 'CAT BRI', 'DEC': 'CAT PUN', 'DGA': 'CAT BRI', 
                'DOT': 'CAT GZL', 'DRG': 'CAT BRI', 'DRL': 'CAT BRI', 'DRS': 'CAT LAS', 
                'DUL': 'CAT STD', 'EAS': 'CAT PUN', 'EBD': 'CAT GES', 'ECA': 'CAT STD', 
                'ECE': 'CAT ECE', 'ELB': 'CAT ECE', 'EOW': 'CAT SCA', 'ESM': 'CAT VVE', 
                'ETD': 'CAT CAD', 'ETV': 'CAT BRI', 'EVO': 'CAT LAS', 'EZL': 'CAT BRI', 
                'FAL': 'CAT VVE', 'FOY': 'CAT VVE', 'FRL': 'CAT VVE', 'FTR': 'CAT CON', 
                'GAL': 'CAT LIN', 'GBR': 'CAT CAD', 'GDX': 'CAT BRI', 'GDY': 'CAT BRI', 
                'GEE': 'CAT BRI', 'GES': 'CAT GES', 'GID': 'CAT BRI', 'GPE': 'CAT GPE', 
                'GTE': 'CAT MOM', 'GZU': 'CAT STD', 'HCC': 'CAT PUN', 'HCE': 'CAT STD', 
                'HHS': 'CAT LIN', 'HIA': 'CAT STD', 'HKM': 'CAT STD', 'HLR': 'CAT CAD', 
                'HOD': 'CAT ALL', 'HOT': 'CAT PUN', 'HSJ': 'CAT STD', 'IDV': 'CAT SFE', 
                'IMX': 'CAT CAD', 'INA': 'CAT STD', 'INC': 'CAT BRI', 'INM': 'CAT STD', 
                'INP': 'CAT GZL', 'IOS': 'CAT CAD', 'ISO': 'CAT STD', 'IST': 'CAT STD', 
                'ITE': 'CAT STD', 'JDS': 'CAT LAS', 'JOY': 'CAT GPE', 'LAE': 'CAT PUN', 
                'LAP': 'CAT BRI', 'LAS': 'CAT LAS', 'LBN': 'CAT GZL', 'LDE': 'CAT STD', 
                'LEB': 'CAT STD', 'LEO': 'CAT VVE', 'LFA': 'CAT GZL', 'LFQ': 'CAT GPE', 
                'LFS': 'CAT STD', 'LIN': 'CAT LIN', 'LJM': 'CAT BRI', 'LLB': 'CAT VVE', 
                'LMD': 'CAT CAD', 'LNE': 'CAT ECE', 'LNO': 'CAT STD', 'LNP': 'CAT CAD', 
                'LOP': 'CAT GES', 'LRO': 'CAT STD', 'LSC': 'CAT SCA', 'LVM': 'CAT BRI', 
                'LVZ': 'CAT ECE', 'LYX': 'CAT GES', 'LZI': 'CAT ALL', 'MAY': 'CAT CON', 
                'MER': 'CAT STD', 'MHK': 'CAT GZL', 'MIT': 'CAT GZL', 'MJS': 'CAT STD', 
                'MLE': 'CAT ECE', 'MLU': 'CAT SCA', 'MOM': 'CAT MOM', 'MQU': 'CAT STD', 
                'MRI': 'CAT STD', 'MRL': 'CAT PUN', 'MSF': 'CAT LAS', 'MSH': 'CAT STD', 
                'MSK': 'CAT SCA', 'MTB': 'CAT CAD', 'MUF': 'CAT STD', 'NAL': 'CAT CUA', 
                'NEK': 'CAT SCA', 'NNA': 'CAT STD', 'NRP': 'CAT VAE', 'NRS': 'CAT STD', 
                'NRT': 'CAT VVE', 'NSM': 'CAT SFE', 'NSY': 'CAT CAD', 'NVG': 'CAT VVE', 
                'NVZ': 'CAT VVE', 'OBI': 'CAT GZL', 'OGW': 'CAT CON', 'OIC': 'CAT CAD', 
                'OIL': 'CAT VAE', 'ONO': 'CAT GPE', 'OOE': 'CAT VAE', 'ORN': 'CAT SCA', 
                'ORQ': 'CAT GPE', 'OSJ': 'CAT CAD', 'OSY': 'CAT VAE', 'PBV': 'CAT STD', 
                'PEV': 'CAT BRI', 'PFS': 'CAT GES', 'PGI': 'CAT BRI', 'PGX': 'CAT BRI', 
                'PMD': 'CAT PUN', 'PMK': 'CAT STD', 'PNQ': 'CAT STD', 'PPD': 'CAT STD', 
                'PPQ': 'CAT STD', 'PPU': 'CAT GES', 'PQD': 'CAT LIN', 'PQG': 'CAT SCA', 
                'PQO': 'CAT STD', 'PQP': 'CAT SCA', 'PQX': 'CAT STD', 'PQZ': 'CAT STD', 
                'PSL': 'CAT GES', 'PSQ': 'CAT STD', 'PUF': 'CAT GES', 'PUN': 'CAT PUN', 
                'PVN': 'CAT GES', 'PVV': 'CAT SCA', 'PWR': 'CAT SCA', 'PXS': 'CAT BRI', 
                'PXZ': 'CAT GES', 'RBT': 'CAT BRI', 'RCI': 'CAT BRI', 'RCK': 'CAT VVE', 
                'RCU': 'CAT VVE', 'RDH': 'CAT PUN', 'RGJ': 'CAT BRI', 'RLO': 'CAT VVE', 
                'RMS': 'CAT SFE', 'RNJ': 'CAT STD', 'ROB': 'CAT VVE', 'RPG': 'CAT BRI', 
                'RVA': 'CAT BRI', 'SAS': 'CAT VAE', 'SBR': 'CAT VVE', 'SCA': 'CAT SCA', 
                'SCZ': 'CAT LAS', 'SDS': 'CAT STD', 'SFE': 'CAT SFE', 'SGE': 'CAT VAE', 
                'SGL': 'CAT SCA', 'SII': 'CAT VAE', 'SJM': 'CAT GZL', 'SNP': 'CAT VAE', 
                'SPW': 'CAT VAE', 'SRF': 'CAT SFE', 'SSF': 'CAT CAD', 'STD': 'CAT PUN', 
                'SVI': 'CAT STD', 'SWW': 'CAT PUN', 'TEC': 'CAT BRI', 'TOO': 'CAT VVE', 
                'TPK': 'CAT STD', 'UBR': 'CAT VVE', 'UDE': 'CAT CAD', 'UGN': 'CAT GZL', 
                'UHK': 'CAT GZL', 'UID': 'CAT VVE', 'UMO': 'CAT VVE', 'UOL': 'CAT ECE', 
                'UPE': 'CAT VVE', 'UPI': 'CAT LAS', 'URK': 'CAT ECE', 'VAF': 'CAT SCA', 
                'VAL': 'CAT VAE', 'VEP': 'CAT GES', 'VGA': 'CAT SCA', 'VJU': 'CAT CAD', 
                'VLB': 'CAT STD', 'VLC': 'CAT STD', 'VMT': 'CAT VVE', 'VNE': 'CAT VAE', 
                'VPP': 'CAT GZL', 'VSD': 'CAT SFE', 'VSE': 'CAT STD', 'VSK': 'CAT CAD', 
                'VSQ': 'CAT SFE', 'VVE': 'CAT VVE', 'VYD': 'CAT CAD', 'VYG': 'CAT VAE', 
                'XEP': 'CAT CAD', 'YES': 'CAT CAD', 'ZNL': 'CAT VVE', 'ZOZ': 'CAT SFE',  
                'EFA': 'CAT ALL', 'LXE': 'CAT ALL', 'NA5': 'CAT ALL', 'NA6': 'CAT ALL',
                'NA7': 'CAT ALL', 'NA8': 'CAT ALL', 'NA9': 'CAT ALL', 'BRQ': 'CAT CAD',
                'CH2': 'CAT CAD', 'CH4': 'CAT CAD', 'CYD': 'CAT CAD', 'DCO': 'CAT CAD',
                'GAG': 'CAT CAD', 'GPY': 'CAT CAD', 'GTA': 'CAT CAD', 'LHE': 'CAT CAD',
                'LRA': 'CAT CAD', 'NB1': 'CAT CAD', 'NB3': 'CAT CAD', 'NB5': 'CAT CAD',
                'NB6': 'CAT CAD', 'NB7': 'CAT CAD', 'NB8': 'CAT CAD', 'NB9': 'CAT CAD',
                'ND6': 'CAT CAD', 'ND7': 'CAT CAD', 'RXY': 'CAT CAD', 'SNJ': 'CAT CAD',
                'YGO': 'CAT CAD', 'YGP': 'CAT CAD', 'ROP': 'CAT CON', 'RTZ': 'CAT CON',
                'RBF': 'CAT ECE', 'AHF': 'CAT GES', 'DGN': 'CAT GES', 'HIS': 'CAT GES',
                'HDN': 'CAT LAS', 'HZI': 'CAT LAS', 'YRE': 'CAT LAS', 'AAM': 'CAT LIN',
                'CH5': 'CAT LIN', 'CH6': 'CAT LIN', 'EL9': 'CAT LIN', 'GBD': 'CAT LIN',
                'GDE': 'CAT LIN', 'GNZ': 'CAT LIN', 'ITR': 'CAT LIN', 'KS4': 'CAT LIN',
                'KS5': 'CAT LIN', 'KS6': 'CAT LIN', 'KS7': 'CAT LIN', 'LAI': 'CAT LIN',
                'MGU': 'CAT LIN', 'NC7': 'CAT LIN', 'NC8': 'CAT LIN', 'ND8': 'CAT LIN',
                'ND9': 'CAT LIN', 'NE0': 'CAT LIN', 'NE1': 'CAT LIN', 'NE2': 'CAT LIN',
                'NRI': 'CAT LIN', 'OOS': 'CAT LIN', 'OWP': 'CAT LIN', 'QA4': 'CAT LIN',
                'QN2': 'CAT LIN', 'QN3': 'CAT LIN', 'QN4': 'CAT LIN', 'QN5': 'CAT LIN',
                'QN6': 'CAT LIN', 'QN7': 'CAT LIN', 'QN8': 'CAT LIN', 'QN9': 'CAT LIN',
                'QO0': 'CAT LIN', 'QO1': 'CAT LIN', 'QO2': 'CAT LIN', 'QO3': 'CAT LIN',
                'QO4': 'CAT LIN', 'QO5': 'CAT LIN', 'QO6': 'CAT LIN', 'QO7': 'CAT LIN',
                'QO8': 'CAT LIN', 'QO9': 'CAT LIN', 'QP0': 'CAT LIN', 'QP1': 'CAT LIN',
                'QP2': 'CAT LIN', 'QP3': 'CAT LIN', 'QP4': 'CAT LIN', 'QP5': 'CAT LIN',
                'QP6': 'CAT LIN', 'QP7': 'CAT LIN', 'QP8': 'CAT LIN', 'QP9': 'CAT LIN',
                'QQ0': 'CAT LIN', 'QQ1': 'CAT LIN', 'QQ2': 'CAT LIN', 'QQ3': 'CAT LIN',
                'QQ4': 'CAT LIN', 'RFA': 'CAT LIN', 'RFY': 'CAT LIN', 'RJW': 'CAT LIN',
                'RNX': 'CAT LIN', 'S6D': 'CAT LIN', 'S6F': 'CAT LIN', 'SM9': 'CAT LIN',
                'SN0': 'CAT LIN', 'SN2': 'CAT LIN', 'SN5': 'CAT LIN', 'SN7': 'CAT LIN',
                'SN8': 'CAT LIN', 'SN9': 'CAT LIN', 'SO0': 'CAT LIN', 'SO1': 'CAT LIN',
                'SO2': 'CAT LIN', 'SO3': 'CAT LIN', 'SO4': 'CAT LIN', 'SO6': 'CAT LIN',
                'SO7': 'CAT LIN', 'SO9': 'CAT LIN', 'VF5': 'CAT LIN', 'VH2': 'CAT LIN',
                'VMI': 'CAT LIN', 'VX0': 'CAT LIN', 'VX1': 'CAT LIN', 'VX2': 'CAT LIN',
                'VX4': 'CAT LIN', 'VX5': 'CAT LIN', 'VX6': 'CAT LIN', 'GTN': 'CAT MOM',
                'MMF': 'CAT MOM', 'NC1': 'CAT MOM', 'NC2': 'CAT MOM', 'NC3': 'CAT MOM',
                'NC4': 'CAT MOM', 'NC5': 'CAT MOM', 'NC6': 'CAT MOM', 'NC9': 'CAT MOM',
                'ND0': 'CAT MOM', 'ND1': 'CAT MOM', 'ND2': 'CAT MOM', 'ND3': 'CAT MOM',
                'ND4': 'CAT MOM', 'ND5': 'CAT MOM', 'QB4': 'CAT MOM', 'RYS': 'CAT MOM',
                'EOX': 'CAT SCA', 'JCK': 'CAT SCA', 'RGQ': 'CAT SFE', 'SOI': 'CAT VVE',
                'ZPJ': 'CAT CAD'
            }

            # =========================================================================
            # 🛡️ EXTRACCIÓN Y MAPEO (BLINDADO CON 3 NIVELES DE RESPALDO)
            # =========================================================================
            def asignar_cat_definitivo(row):
                distrito = str(row.get('DISTRITO', '')).strip().upper()
                ct = str(row.get('CT', '')).strip().upper()
                area = str(row.get('AREA_CORREGIDA', '')).strip().upper()

                # 🧹 1. Limpiar nulos y falsos vacíos que genera Excel/Pandas
                if distrito == 'NAN': distrito = ''
                if ct == 'NAN': ct = ''

                # 🥇 2. Intento principal: Por Distrito (Exactitud de 3 letras)
                if distrito and not distrito.startswith('SIN'):
                    siglas = distrito[:3]
                    if siglas in diccionario_tiendas:
                        return diccionario_tiendas[siglas]

                # 🥈 3. Respaldo secundario: Por CT
                # Usamos palabras clave para que coincida aunque tenga espacios extras o prefijos
                diccionario_respaldo_ct = {
                    'MONTEMORELOS': 'CAT MOM',
                    'APODACA': 'CAT STD',
                    'ESCOBEDO': 'CAT STD', 
                    'CADEREYTA': 'CAT CAD',
                    'LINARES': 'CAT LIN',
                    'GONZALITOS': 'CAT CON',
                    'LINCOLN': 'CAT VVE',
                    'REVOLUCION': 'CAT BRI',
                    'SAN PEDRO': 'CAT VAE',
                    'COLON': 'CAT CUA',
                    'SANTA CATARINA': 'CAT SCA',
                    'PUENTES': 'CAT PUN',
                    'SANTA FE': 'CAT SFE',
                    'LA SILLA': 'CAT LAS',
                    'UNIVERSIDAD': 'CAT GES'
                }
                if ct and not ct.startswith('SIN'):
                    for clave, cat in diccionario_respaldo_ct.items():
                        if clave in ct:
                            return cat

                # 🥉 4. Último recurso: Fondo de Red por Área
                # Si el folio viene 100% en blanco (Sin Distrito Y Sin CT), lo mandamos 
                # a la tienda matriz del área para que NUNCA aparezca "SIN ASIGNAR".
                diccionario_respaldo_area = {
                    'MONTERREY 1': 'CAT BRI',
                    'MONTERREY 2': 'CAT GES',
                    'MONTERREY 3': 'CAT STD'
                }
                if area in diccionario_respaldo_area:
                    return diccionario_respaldo_area[area]

                return 'CAT SIN ASIGNAR'

            df['TIENDA'] = df.apply(asignar_cat_definitivo, axis=1)
            # =========================================================================

            # -----------------------------------------------------
            # 🛠️ FUNCIONES DE FORMATO Y LÓGICA
            # -----------------------------------------------------
            def ordenar_numerico(texto):
                if texto == 'Total': return 9999
                match = re.search(r'^(\d+)', str(texto))
                return int(match.group(1)) if match else 999

            def aplicar_subtotales(pt):
                if not isinstance(pt.index, pd.MultiIndex) or pt.empty: return pt
                if 'Total' in pt.index.get_level_values(0):
                    pt_sin_total = pt.drop('Total', level=0)
                    total_gen = pt.loc[['Total']]
                else:
                    pt_sin_total = pt
                    total_gen = pd.DataFrame()

                subtotales = pt_sin_total.groupby(level=0).sum()
                subtotales.index = pd.MultiIndex.from_arrays([subtotales.index, ['ZZZ_SUBTOTAL'] * len(subtotales.index)])
                pt_completa = pd.concat([pt_sin_total, subtotales]).sort_index()
                pt_completa = pt_completa.rename(index={'ZZZ_SUBTOTAL': '👉 TOTAL ÁREA'})

                if not total_gen.empty: 
                    pt_completa = pd.concat([pt_completa, total_gen])
                return pt_completa

            def estilo_resaltado(df):
                estilo = df.style.apply(
                    lambda x: ['background-color: #ADD8E6; font-weight: bold' if isinstance(x.name, tuple) and len(x.name) > 1 and x.name[1] == '👉 TOTAL ÁREA' else '' for _ in x], 
                    axis=1
                )
                return estilo

            def generar_boton_descarga(df_datos, base_nombre, btn_key):
                nombre_final = f"{base_nombre}_{region_seleccionada.lower()}.csv"
                csv = df_datos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Descargar Folios",
                    data=csv,
                    file_name=nombre_final,
                    mime='text/csv',
                    key=btn_key
                )

            def estilo_tabla_1(df):
                def aplicar_colores(row):
                    nombre = str(row.name).replace('\u200b', '')
                    nombre_limpio = nombre.strip().upper()
                    es_subtotal_n2 = not nombre.startswith('\xa0') and nombre_limpio != 'TOTAL GENERAL'

                    if es_subtotal_n2 and '4 EN VALIDACION' in nombre_limpio:
                        return ['background-color: #FF0000; color: white; font-weight: bold'] * len(row)
                    elif es_subtotal_n2 and '9 VENTAS' in nombre_limpio:
                        return ['background-color: #F4A460; color: black; font-weight: bold'] * len(row)
                    elif '6.3 EN PROCESO' in nombre_limpio:
                        return ['background-color: #FFFF00; color: black; font-weight: bold'] * len(row)
                    elif '6.4 MANTENIMIENTO' in nombre_limpio:
                        return ['background-color: #FFE4B5; color: black'] * len(row)
                    elif es_subtotal_n2:
                        return ['background-color: #ADD8E6; color: black; font-weight: bold'] * len(row)
                    elif nombre_limpio == 'TOTAL GENERAL':
                        return ['font-weight: bold; background-color: #EFEFEF'] * len(row)
                    return [''] * len(row)
                return df.style.apply(aplicar_colores, axis=1)

            # =========================================================
            # 🎛️ SELECTORES LATERALES DE VISTA Y ÁREA
            # =========================================================
            st.sidebar.divider()
            opciones_vista = ["🏢 Operativa (Por CT)"]
            if region_seleccionada == "Monterrey":
                opciones_vista.append("🏪 Comercial (Por CAT)")

            vista_seleccionada = st.sidebar.selectbox(
                "👁️ Vista:",
                opciones_vista,
                index=1 if region_seleccionada == "Monterrey" else 0,
                key=f"tablero_vista_{region_seleccionada}"
            )

            # Usamos contenedores para conservar la lógica actual, pero ya sin pestañas.
            if vista_seleccionada.startswith("🏢"):
                tab_operativa = st.container()
                tab_comercial = None
            else:
                tab_operativa = None
                tab_comercial = st.container()

            st.caption(f"Filtros activos → Región: {region_seleccionada} | {vista_seleccionada.replace('🏢 ', '').replace('🏪 ', '')}")

            # =========================================================
            # PESTAÑA 1: VISTA OPERATIVA
            # =========================================================
            if tab_operativa is not None:
                with tab_operativa:
                    pass
                # 1. Obtener la lista de áreas únicas ya procesadas/corregidas
                # Se usa dropna() para evitar que valores nulos rompan el filtro y sorted() para orden alfabético
                areas_disponibles = sorted(df['AREA_CORREGIDA'].dropna().unique())

                # 2. Filtro lateral. Por defecto arranca en MONTERREY 2.
                if region_seleccionada == "Monterrey" and "MONTERREY 2" in areas_disponibles:
                    default_areas = ["MONTERREY 2"]
                else:
                    default_areas = [areas_disponibles[0]] if areas_disponibles else []

                areas_seleccionadas = st.sidebar.multiselect(
                    "🏢 Área / CT:",
                    options=areas_disponibles,
                    default=default_areas,
                    key=f"tablero_areas_{region_seleccionada}"
                )

                # 3. Filtrar el DataFrame original con las áreas que el usuario dejó en el selector
                if areas_seleccionadas:
                    df_filtrado = df[df['AREA_CORREGIDA'].isin(areas_seleccionadas)]
                else:
                    # Si el usuario borra todas las áreas, mostramos el df vacío
                    df_filtrado = df.iloc[0:0] 
                    st.warning("⚠️ Por favor, selecciona al menos un área para visualizar los datos.")

                # A PARTIR DE AQUÍ, TODAS LAS TABLAS LEEN 'df_filtrado' EN LUGAR DE 'df'

                st.subheader(f"📑 1. Últimos 6 Meses (Demanda por Bolsa) - {region_seleccionada}")
                df_6m = df_filtrado[df_filtrado['ULTIMOS_6_MESES'] == 'SI']
                estatus_excluidos = ["7. ASPECTOS TÉCNICOS", "8 PENDIENTES BOLSA VENTAS + CD", "10 NO VENTAS + CD"]
                df_6m = df_6m[~df_6m['ESTATUS_AGR_N2'].isin(estatus_excluidos)]

                if not df_6m.empty:
                    td_6m = pd.pivot_table(df_6m, index=['ESTATUS_AGR_N2', 'ESTATUS_AGR_N1'], columns='AREA_CORREGIDA', values='FOLIO', aggfunc='count', fill_value=0, margins=True, margins_name='Total')

                    total_gen_6m = td_6m.loc[['Total']] if 'Total' in td_6m.index.get_level_values(0) else pd.DataFrame()
                    td_6m_sin_total = td_6m.drop('Total', level=0) if 'Total' in td_6m.index.get_level_values(0) else td_6m

                    subtotales_n2 = td_6m_sin_total.groupby(level=0).sum()
                    subtotales_n2.index = pd.MultiIndex.from_arrays([subtotales_n2.index, [''] * len(subtotales_n2.index)])

                    td_6m_final = pd.concat([td_6m_sin_total, subtotales_n2])
                    nuevo_indice = sorted(td_6m_final.index, key=lambda x: (ordenar_numerico(x[0]), str(x[1])))
                    td_6m_final = td_6m_final.reindex(nuevo_indice)

                    if not total_gen_6m.empty:
                        td_6m_final = pd.concat([td_6m_final, total_gen_6m])

                    td_6m_final.index.names = ['ESTATUS_AGR_N2', 'ESTATUS_AGR_N1']
                    td_6m_final = td_6m_final.reset_index()

                    vistos = {}
                    def unificar_estatus(fila):
                        n2 = str(fila['ESTATUS_AGR_N2']) if pd.notna(fila['ESTATUS_AGR_N2']) else ''
                        n1 = str(fila['ESTATUS_AGR_N1']) if pd.notna(fila['ESTATUS_AGR_N1']) else ''
                        if n2 == 'Total': texto = 'Total General'
                        elif n1 == '': texto = n2  
                        else: texto = '\xa0\xa0\xa0\xa0\xa0\xa0' + n1
                        if texto in vistos: vistos[texto] += 1
                        else: vistos[texto] = 0
                        return texto + ('\u200b' * vistos[texto])

                    td_6m_final['ESTATUS_AGR'] = td_6m_final.apply(unificar_estatus, axis=1)
                    td_6m_final = td_6m_final.set_index('ESTATUS_AGR').drop(columns=['ESTATUS_AGR_N2', 'ESTATUS_AGR_N1'])

                    st.table(estilo_tabla_1(td_6m_final))
                    generar_boton_descarga(df_6m, 'folios_t1_6m', btn_key='btn1')
                else:
                    st.info("No hay datos para esta tabla.")

                st.divider()

                st.subheader("✔ 2. Ult 6 Meses (BOLSA 4xDIL2)")
                df_b4 = df_filtrado[df_filtrado['ESTATUS_AGR_N2'].str.contains('4', case=False, na=False)]
                if not df_b4.empty:
                    td_b4 = pd.pivot_table(df_b4, index=['AREA_CORREGIDA', 'ESTATUS_AGR_N1'], columns='Rango x Dil', values='FOLIO', aggfunc='count', fill_value=0, margins=True, margins_name='Total')
                    cols = [c for c in orden_columnas if c in td_b4.columns] + [c for c in td_b4.columns if c not in orden_columnas]
                    st.table(estilo_resaltado(aplicar_subtotales(td_b4[cols])))
                    generar_boton_descarga(df_b4, 'folios_t2_bolsa4', btn_key='btn2')
                else: st.info("No hay datos.")

                st.divider()

                st.subheader("🛠 3. Ult 6 Meses (BOLSA 5xDIL2 - Solo PS)")
                df_b5_ps = df_filtrado[(df_filtrado['ESTATUS_AGR_N2'].str.contains('5', case=False, na=False)) & (df_filtrado['ETAPA_OS'] == 'PS')]
                if not df_b5_ps.empty:
                    td_b5_ps = pd.pivot_table(df_b5_ps, index=['AREA_CORREGIDA', 'CT'], columns='Rango x Dil', values='FOLIO', aggfunc='count', fill_value=0, margins=True, margins_name='Total')
                    cols = [c for c in orden_columnas if c in td_b5_ps.columns] + [c for c in td_b5_ps.columns if c not in orden_columnas]
                    st.table(estilo_resaltado(aplicar_subtotales(td_b5_ps[cols])))
                    generar_boton_descarga(df_b5_ps, 'folios_t3_bolsa5_ps', btn_key='btn3')
                else: st.info("No hay datos.")

                st.divider()

                st.subheader("⚙ 4. Ult 6 Meses (BOLSA 5 por Etapa)")
                df_b5 = df_filtrado[df_filtrado['ESTATUS_AGR_N2'].str.contains('5', case=False, na=False)]
                if not df_b5.empty:
                    td_b5 = pd.pivot_table(df_b5, index=['AREA_CORREGIDA', 'CT'], columns='ETAPA_OS', values='FOLIO', aggfunc='count', fill_value=0, margins=True, margins_name='Total')
                    st.table(estilo_resaltado(aplicar_subtotales(td_b5)))
                    generar_boton_descarga(df_b5, 'folios_t4_bolsa5_etapas', btn_key='btn4')
                else: st.info("No hay datos.")

                st.divider()

                st.subheader("📞 5. Ult 6 Meses (PORTAS)")
                df_p = df_filtrado[(df_filtrado['PORTABILIDAD']=='SI') & (df_filtrado['ULTIMOS_6_MESES']=='SI') & (df_filtrado['ETAPA_OS']=='PS')]
                if not df_p.empty:
                    td_p = pd.pivot_table(df_p, index=['AREA_CORREGIDA', 'CT'], columns='Rango x Dil', values='FOLIO', aggfunc='count', fill_value=0, margins=True, margins_name='Total')
                    cols = [c for c in orden_columnas if c in td_p.columns] + [c for c in td_p.columns if c not in orden_columnas]
                    st.table(estilo_resaltado(aplicar_subtotales(td_p[cols])))
                    generar_boton_descarga(df_p, 'folios_t5_portas', btn_key='btn5')
                else: st.info("No hay datos.")

                st.divider()

                st.subheader("🛠 6. BOLSA 6.9 PENDIENTE PAGO GI x COPE")

                # 1. Se define correctamente la variable usando guiones bajos, sin puntos (df_b69_cp en lugar de df_b5_ps o df_b6.9_cp)
                df_b69_cp = df_filtrado[(df_filtrado['ESTATUS_AGR_N1'].str.contains('6.9', case=False, na=False)) & (df_filtrado['ETAPA_OS'] == 'CP')]

                if not df_b69_cp.empty:
                    # 2. Se usa la misma variable para crear la tabla dinámica
                    td_b69_cp = pd.pivot_table(df_b69_cp, index=['AREA_CORREGIDA', 'CT'], columns='Rango x Dil', values='FOLIO', aggfunc='count', fill_value=0, margins=True, margins_name='Total')

                    # 3. Se alinean los nombres en la definición de columnas
                    cols = [c for c in orden_columnas if c in td_b69_cp.columns] + [c for c in td_b69_cp.columns if c not in orden_columnas]

                    # 4. Se imprime la tabla dinámica correcta (td_b69_cp)
                    st.table(estilo_resaltado(aplicar_subtotales(td_b69_cp[cols])))

                    # 5. Se manda llamar la función de descarga con la variable sin el punto
                    generar_boton_descarga(df_b69_cp, 'folios_t6_bolsa69', btn_key='btn_bolsa_69')
                else: 
                    st.info("No hay datos.")

                st.divider()

                st.subheader("🏠 7. Ult 6 Meses (CAMB DOM)")        
                df_cd = df_filtrado[df_filtrado['TIPO_MOVIMIENTO'].str.contains('CAMB DOM', case=False, na=False)]
                if not df_cd.empty:
                    td_cd = pd.pivot_table(df_cd, index=['AREA_CORREGIDA', 'CT'], columns='ETAPA_OS', values='FOLIO', aggfunc='count', fill_value=0, margins=True, margins_name='Total')
                    st.table(estilo_resaltado(aplicar_subtotales(td_cd)))
                    generar_boton_descarga(df_cd, 'folios_t7_cambio_domicilio', btn_key='btn7')
                else: st.info("No hay datos.")

            # =========================================================
            # PESTAÑA 2: VISTA COMERCIAL (Por CAT) - Solo para Monterrey
            # =========================================================
            if region_seleccionada == "Monterrey" and tab_comercial is not None:
                with tab_comercial:
                    st.subheader("📊 Análisis General por CAT")

                    # Submenú horizontal (Áreas)
                    areas_disponibles = sorted(df['AREA_CORREGIDA'].dropna().unique().tolist())
                    opciones_filtro = ["Todas las Áreas"] + areas_disponibles

                    area_default_index = (
                        opciones_filtro.index("MONTERREY 2")
                        if "MONTERREY 2" in opciones_filtro else 0
                    )

                    area_seleccionada_com = st.sidebar.selectbox(
                        "🔎 Área comercial:",
                        opciones_filtro,
                        index=area_default_index,
                        key=f"tablero_area_com_{region_seleccionada}"
                    )

                    # --- NUEVO: SELECTOR DINÁMICO DE TIENDAS ---
                    # Obtener tiendas únicas dependiendo del área previamente seleccionada
                    if area_seleccionada_com == "Todas las Áreas":
                        opciones_tiendas = sorted(df['TIENDA'].dropna().unique().tolist())
                    else:
                        opciones_tiendas = sorted(df[df['AREA_CORREGIDA'] == area_seleccionada_com]['TIENDA'].dropna().unique().tolist())

                    tiendas_seleccionadas = st.sidebar.multiselect(
                        "🏪 Tienda / CAT:",
                        options=opciones_tiendas,
                        default=[],
                        key=f"tablero_tiendas_{region_seleccionada}_{area_seleccionada_com}"
                    )

                    st.divider()

                    # --- 🧹 LÓGICA EXCLUSIVA COMERCIAL ---
                    df_com = df.copy()

                    # 1. Regla: Sin folios Posteados
                    if 'ESTATUS_OS' in df_com.columns:
                        df_com = df_com[df_com['ESTATUS_OS'].astype(str).str.upper() != 'POSTEADA']

                    # 2. Regla: Sin Estatus Basura
                    if 'ESTATUS_AGR_N2' in df_com.columns:
                        excluir_n2 = '10 NO VENTAS|8 PENDIENTES BOLSA'
                        df_com = df_com[~df_com['ESTATUS_AGR_N2'].astype(str).str.contains(excluir_n2, case=False, na=False, regex=True)]

                    # --- ✂️ APLICAR FILTRO DEL SUBMENÚ ---
                    # Filtro Nivel 1: Área
                    if area_seleccionada_com != "Todas las Áreas":
                        df_com = df_com[df_com['AREA_CORREGIDA'] == area_seleccionada_com]

                    # Filtro Nivel 2: Tiendas (Solo filtra si el usuario escogió alguna opción)
                    if tiendas_seleccionadas:
                        df_com = df_com[df_com['TIENDA'].isin(tiendas_seleccionadas)]

                    # --- 📉 TABLA 1: Demanda cruzada por Tienda ---
                    st.subheader(f"📑 1. Últimos 6 Meses (Demanda por Bolsa) - {region_seleccionada}")
                    df_t1_com = df_com[df_com['ULTIMOS_6_MESES'] == 'SI']
                    df_t1_com = df_t1_com[~df_t1_com['ESTATUS_AGR_N2'].astype(str).str.contains('7. ASPECTOS TÉCNICOS', case=False, na=False)]

                    if not df_t1_com.empty:
                        td_t1_com = pd.pivot_table(df_t1_com, index=['ESTATUS_AGR_N2', 'ESTATUS_AGR_N1'], columns='TIENDA', values='FOLIO', aggfunc='count', fill_value=0, margins=True, margins_name='Total')

                        total_gen = td_t1_com.loc[['Total']] if 'Total' in td_t1_com.index.get_level_values(0) else pd.DataFrame()
                        td_sin_total = td_t1_com.drop('Total', level=0) if 'Total' in td_t1_com.index.get_level_values(0) else td_t1_com

                        subtotales = td_sin_total.groupby(level=0).sum()
                        subtotales.index = pd.MultiIndex.from_arrays([subtotales.index, [''] * len(subtotales.index)])

                        td_final = pd.concat([td_sin_total, subtotales])
                        td_final = td_final.reindex(sorted(td_final.index, key=lambda x: (ordenar_numerico(x[0]), str(x[1]))))

                        if not total_gen.empty:
                            td_final = pd.concat([td_final, total_gen])

                        td_final.index.names = ['ESTATUS_AGR_N2', 'ESTATUS_AGR_N1']
                        td_final = td_final.reset_index()

                        vistos_c = {}
                        def unificar_estatus_c(fila):
                            n2 = str(fila['ESTATUS_AGR_N2']) if pd.notna(fila['ESTATUS_AGR_N2']) else ''
                            n1 = str(fila['ESTATUS_AGR_N1']) if pd.notna(fila['ESTATUS_AGR_N1']) else ''
                            if n2 == 'Total': texto = 'Total General'
                            elif n1 == '': texto = n2  
                            else: texto = '\xa0\xa0\xa0\xa0\xa0\xa0' + n1
                            if texto in vistos_c: vistos_c[texto] += 1
                            else: vistos_c[texto] = 0
                            return texto + ('\u200b' * vistos_c[texto])

                        td_final['ESTATUS_AGR'] = td_final.apply(unificar_estatus_c, axis=1)
                        td_final = td_final.set_index('ESTATUS_AGR').drop(columns=['ESTATUS_AGR_N2', 'ESTATUS_AGR_N1'])

                        st.table(estilo_tabla_1(td_final))
                        # ⬇️ BOTÓN DE DESCARGA AÑADIDO ⬇️
                        generar_boton_descarga(df_t1_com, 'folios_comercial_t1', btn_key='btn_com_1')
                    else:
                        st.info("No hay datos para la Tabla 1 Comercial.")

                    st.divider()

                    # --- 📉 TABLA 2: Bolsa 4xDIL2 (Únicamente 4.2 Cliente en Contactación) ---
                    st.subheader("✔ 2. Ult 6 Meses (BOLSA 4xDIL2) - Contactación")
                    df_t2_com = df_com[df_com['ESTATUS_AGR_N1'].astype(str).str.contains(r'4\.2 CLIENTE EN CONTACTACION', case=False, na=False, regex=True)]

                    if not df_t2_com.empty:
                        td_t2_com = pd.pivot_table(df_t2_com, index=['AREA_CORREGIDA', 'TIENDA'], columns='Rango x Dil', values='FOLIO', aggfunc='count', fill_value=0, margins=True, margins_name='Total')
                        cols_t2 = [c for c in orden_columnas if c in td_t2_com.columns] + [c for c in td_t2_com.columns if c not in orden_columnas]
                        st.table(estilo_resaltado(aplicar_subtotales(td_t2_com[cols_t2])))
                        # ⬇️ BOTÓN DE DESCARGA AÑADIDO ⬇️
                        generar_boton_descarga(df_t2_com, 'folios_comercial_t2_contacto', btn_key='btn_com_2')
                    else:
                        st.info("No hay folios en 4.2 Cliente en Contactación.")

                    st.divider()

                    # --- 📉 TABLA 3: OS Comerciales ---
                    st.subheader("💼 3. OS Comerciales")

                    # Filtramos por las etapas comerciales requeridas
                    etapas_comerciales = ['C8', 'CD', 'CE', 'CL', 'CO', 'CP', 'CW', 'OQ', 'SN']
                    df_t3_com = df_com[df_com['ETAPA_OS'].isin(etapas_comerciales)]

                    if not df_t3_com.empty:
                        td_t3_com = pd.pivot_table(
                            df_t3_com, 
                            index=['AREA_CORREGIDA', 'TIENDA'], 
                            columns='Rango x Dil', 
                            values='FOLIO', 
                            aggfunc='count', 
                            fill_value=0, 
                            margins=True, 
                            margins_name='Total'
                        )
                        cols_t3 = [c for c in orden_columnas if c in td_t3_com.columns] + [c for c in td_t3_com.columns if c not in orden_columnas]
                        st.table(estilo_resaltado(aplicar_subtotales(td_t3_com[cols_t3])))
                        # ⬇️ BOTÓN DE DESCARGA AÑADIDO ⬇️
                        generar_boton_descarga(df_t3_com, 'folios_comercial_t3_631', btn_key='btn_com_3')
                    else:
                        st.info("No hay folios para las OS Comerciales seleccionadas.")

                    st.divider()

                    # --- 📉 TABLA 4: Portabilidad en TL ---
                    st.subheader("💼 4. Portabilidad en TL")

                    # Filtramos por la etapa 'TL'. 
                    # (Opcional: Agregué la condición de PORTABILIDAD == 'SI' basándome en el título. Si no aplica, puedes borrar ese fragmento).
                    df_t4_tl_com = df_com[(df_com['ETAPA_OS'] == 'TL') & (df_com['PORTABILIDAD'] == 'SI')]

                    # Validación correcta utilizando el dataframe de la Tabla 4
                    if not df_t4_tl_com.empty:
                        td_t4_com = pd.pivot_table(
                            df_t4_tl_com, 
                            index=['AREA_CORREGIDA', 'TIENDA'], 
                            columns='Rango x Dil', 
                            values='FOLIO', 
                            aggfunc='count', 
                            fill_value=0, 
                            margins=True, 
                            margins_name='Total'
                        )

                        # Acomodo de columnas respetando las variables de la Tabla 4
                        cols_t4 = [c for c in orden_columnas if c in td_t4_com.columns] + [c for c in td_t4_com.columns if c not in orden_columnas]

                        # Dibujado de la tabla
                        st.table(estilo_resaltado(aplicar_subtotales(td_t4_com[cols_t4])))

                        # ⬇️ BOTÓN DE DESCARGA AÑADIDO ⬇️
                        generar_boton_descarga(df_t4_tl_com, 'folios_comercial_t4_tl', btn_key='btn_com_4')
                    else:
                        st.info("No hay folios para las Portabilidades en TL.")

                    st.divider()

                    # --- 🛠 5. BOLSA 6.9 PENDIENTE PAGO GI x COPE ---
                    st.subheader("🛠 5. BOLSA 6.9 PENDIENTE PAGO GI x COPE")

                    # Filtro principal de la base (se mantiene igual)
                    df_b69_cp = df_com[(df_com['ESTATUS_AGR_N1'].str.contains('6.9', case=False, na=False)) & (df_com['ETAPA_OS'] == 'CP')]

                    if not df_b69_cp.empty:
                        # TABLA A: Vista Original (Por CT)
                        st.markdown("**Desglose por CT:**")
                        td_b69_cp = pd.pivot_table(df_b69_cp, index=['AREA_CORREGIDA', 'TIENDA'], columns='CT', values='FOLIO', aggfunc='count', fill_value=0, margins=True, margins_name='Total')
                        cols_ct = [c for c in orden_columnas if c in td_b69_cp.columns] + [c for c in td_b69_cp.columns if c not in orden_columnas]
                        st.table(estilo_resaltado(aplicar_subtotales(td_b69_cp[cols_ct])))

                        # TABLA B: Nueva Vista (Por CANAL)
                        st.markdown("**Desglose por CANAL:**")
                        td_b69_canal = pd.pivot_table(
                            df_b69_cp, 
                            index=['AREA_CORREGIDA', 'TIENDA'], 
                            columns='CANAL', 
                            values='FOLIO', 
                            aggfunc='count', 
                            fill_value=0, 
                            margins=True, 
                            margins_name='Total'  # <-- Corrección: Se regresa a 'Total' para que tu función lo reconozca
                        )
                        # Imprimimos la subtabla aplicando el mismo formato de estilos
                        st.table(estilo_resaltado(aplicar_subtotales(td_b69_canal)))

                        # Botón de descarga unificado para ambas vistas
                        generar_boton_descarga(df_b69_cp, 'folios_t5_bolsa69', btn_key='btn_com_bolsa_69') 

                    # TABLA C: Nueva Vista (FIELDERS por Empresa Externa)
                        st.markdown("**Desglose FIELDERS por Empresa:**")

                        # El checkbox sirve como interruptor manual
                        if st.checkbox("🚀 Generar y Cruzar Base de Empresas (Clarodrive)"):
                            with st.spinner("Paso 1: Conectando con Clarodrive y descargando archivo..."):
                                try:
                                    # Verificamos que la función exista en tu código
                                    if 'obtener_base_fielders_clarodrive' not in globals():
                                        st.error("❌ ERROR FATAL: No se encontró la función de extracción.")
                                    else:
                                        # 1. Ejecutamos la extracción
                                        df_empresas = obtener_base_fielders_clarodrive()
                                        st.success(f"✅ Archivo de Clarodrive descargado con éxito. Se encontraron {len(df_empresas)} registros.")

                                        # 2. Filtramos df_b69_cp para dejar estrictamente al canal Fielder
                                        df_fielders_b69 = df_b69_cp[df_b69_cp['CANAL'].astype(str).str.upper().str.contains('FIELDER', na=False)].copy()

                                        if not df_fielders_b69.empty:
                                            st.info(f"🔍 Cruzando {len(df_fielders_b69)} folios Fielder locales contra la base de Clarodrive...")

                                            # Normalizamos los folios para asegurar un Match perfecto
                                            df_fielders_b69['FOLIO'] = df_fielders_b69['FOLIO'].astype(str).str.strip()
                                            df_empresas['osalta'] = df_empresas['osalta'].astype(str).str.strip()

                                            # 3. Cruzamos nuestra tabla con la base de Clarodrive
                                            df_merge = pd.merge(
                                                df_fielders_b69, 
                                                df_empresas, 
                                                left_on='FOLIO', 
                                                right_on='osalta', 
                                                how='left'
                                            )

                                            # 4. Regla de vacíos
                                            df_merge['NOM_ESTRATEGIA'] = df_merge['NOM_ESTRATEGIA'].fillna('Empresa por definir')
                                            df_merge.loc[df_merge['NOM_ESTRATEGIA'].str.strip() == '', 'NOM_ESTRATEGIA'] = 'Empresa por definir'

                                            td_b69_empresas = pd.pivot_table(
                                                df_merge, 
                                                index=['AREA_CORREGIDA', 'TIENDA'], 
                                                columns='NOM_ESTRATEGIA', 
                                                values='FOLIO', 
                                                aggfunc='count', 
                                                fill_value=0, 
                                                margins=True, 
                                                margins_name='Total'
                                            )

                                            # --- NUEVO: Ordenar columnas de mayor a menor ---
                                            if 'Total' in td_b69_empresas.columns:
                                                # Separamos las columnas de las empresas, excluyendo la columna 'Total'
                                                cols_empresas = [c for c in td_b69_empresas.columns if c != 'Total']

                                                # Ordenamos las empresas basándonos en los valores de la última fila (iloc[-1])
                                                cols_ordenadas = td_b69_empresas[cols_empresas].iloc[-1].sort_values(ascending=False).index.tolist()

                                                # Aplicamos el nuevo orden a la tabla y regresamos la columna 'Total' al final
                                                td_b69_empresas = td_b69_empresas[cols_ordenadas + ['Total']]

                                            # Dibujamos en pantalla
                                            st.table(estilo_resaltado(aplicar_subtotales(td_b69_empresas)))

                                            # Botón de descarga exclusivo para la nueva subtabla cruzada
                                            generar_boton_descarga(df_merge, 'folios_t5_empresas_fielder', btn_key='btn_com_fielder_emp')
                                        else:
                                            st.warning("⚠️ No hay folios marcados como 'FIELDER' en la Bolsa 6.9 actual para cruzar.")

                                except Exception as e:
                                    st.error(f"❌ Error interno al procesar: {e}")
        #


# ============================================================
# 5. RUTEO PRINCIPAL
# ============================================================

if seleccion == "Resultados Diarios":
    mostrar_resultados_diarios()

elif seleccion == "Reporte Telcel":
    mostrar_reporte_telcel()

elif seleccion == "Tablero Bolsas":
    mostrar_tablero_bolsas()
