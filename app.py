import streamlit as st
import os
from services.data_manager import load_json_as_df
from services.state_manager import init_session_state
from services.auth import render_login_page, render_loading_page, logout
from ui.tab1 import render_tab1
from ui.tab2 import render_tab2
from ui.tab3 import render_tab3

# Al inicio de la app.py
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- Configuración de la página ---
st.set_page_config(
    page_title="Cálculo de Liquidación de Deuda", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Inicialización del Estado de la Sesión ---
init_session_state()

# --- Lógica de Autenticación y Carga ---

# 1. Si el usuario no está logueado, mostrar la página de login y detener
if not st.session_state.get('logged_in', False):
    render_login_page()
    st.stop()

# 2. Si está logueado y debe mostrar el loading, mostrar pantalla de carga y detener
if st.session_state.get("show_matrix_loading", False):
    render_loading_page()
    st.stop()

# 3. Usuario logueado y sin loading - Mostrar la aplicación principal

# --- Estilos CSS Globales ---
st.markdown("""
    <style>
        /* Asegurar visibilidad de elementos */
        .stApp > header, #MainMenu, footer {
            visibility: visible !important;
        }
        
        /* Estilos para pestañas */
        button[data-baseweb="tab"][aria-selected="true"] {
            font-size: 1.2rem !important;
            font-weight: bold !important;
            color: #03a9f4 !important;
        }
        
        button[data-baseweb="tab"] {
            font-size: 1rem;
        }
        
        /* Botón de descarga destacado */
        .stDownloadButton > button {
            border: 2px solid #39FF14 !important;
            box-shadow: 0 0 12px #39FF14 !important;
            transition: all 0.3s ease;
        }
        
        .stDownloadButton > button:hover {
            box-shadow: 0 0 20px #39FF14 !important;
            transform: scale(1.02);
        }
        
        /* Ajuste de pestañas */
        .stTabs [data-baseweb="tab-list"] {
            margin-top: -25px;
            gap: 10px;
        }
        
        /* Botón de cerrar sesión */
        .logout-button {
            position: fixed;
            top: 10px;
            right: 20px;
            z-index: 999;
        }
        
        /* Estilo del título principal */
        h1 {
            color: #03a9f4;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Métricas con mejor diseño */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        /* Inputs deshabilitados más legibles */
        input:disabled {
            opacity: 0.7 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header con botón de cerrar sesión ---
col_title, col_logout = st.columns([6, 1])

with col_title:
    st.title("🧾 Cálculo de Liquidación de Deuda")

with col_logout:
    st.write("")  # Espaciado
    if st.button("🚪 Cerrar Sesión", key="btn_logout", help="Volver al login"):
        logout()

st.markdown("")
st.markdown("")

# --- Carga de Datos ---
script_dir = os.path.dirname(os.path.abspath(__file__))
ruta_json = os.path.join(script_dir, 'data', 'base_ucec.json')

# Mostrar spinner mientras carga los datos
with st.spinner("Cargando base de datos..."):
    df_principal = load_json_as_df(ruta_json)

# Verificar si se cargó correctamente
if df_principal is None:
    st.error("❌ No se pudo cargar la base de datos. Verifica que el archivo 'base_ucec.json' exista en la carpeta 'data'.")
    st.info("📁 Ruta esperada: " + ruta_json)
    st.stop()

# Mostrar info del usuario logueado
st.sidebar.success(f"👤 Usuario: **{st.session_state.username}**")
st.sidebar.info(f"📊 Registros cargados: **{len(df_principal):,}**")
st.sidebar.markdown("---")

# --- Interfaz con Pestañas ---
tab1, tab2, tab3 = st.tabs([
    "| Calcular Liquidación", 
    "| Agregar Nuevo EEM", 
    "| Administración"
])

with tab1:
    render_tab1(df_principal)

with tab2:
    render_tab2(df_principal, ruta_json)

with tab3:
    render_tab3()