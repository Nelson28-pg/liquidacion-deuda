import streamlit as st
import os
import time
from datetime import datetime, timedelta
from services.data_manager import load_json_as_df
from services.state_manager import init_session_state
from services.auth import render_login_page, logout
from ui.tab1 import render_tab1
from ui.tab2 import render_tab2
from ui.tab3 import render_tab3

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="Cálculo de Liquidación de Deuda", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Sistema de Liquidaciones v2.5"
    }
)

# ============================================
# INICIALIZACIÓN DEL ESTADO DE SESIÓN
# ============================================
init_session_state()

# Inicializar variables de sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = datetime.now()
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True  # Por defecto en modo oscuro

# ============================================
# CONTROL DE SESIÓN POR INACTIVIDAD (7 minutos)
# ============================================
def check_session_timeout():
    """Verifica si la sesión ha expirado por inactividad"""
    if st.session_state.get('logged_in', False):
        now = datetime.now()
        last_activity = st.session_state.get('last_activity', now)
        
        # 7 minutos de inactividad
        if now - last_activity > timedelta(minutes=7):
            st.warning("⏱️ Sesión expirada por inactividad")
            time.sleep(2)
            logout()
            st.rerun()
        else:
            # Actualizar última actividad
            st.session_state.last_activity = now

# ============================================
# VERIFICAR LOGIN
# ============================================
if not st.session_state.get('logged_in', False):
    render_login_page()
    st.stop()

# Verificar timeout de sesión
check_session_timeout()

# ============================================
# ESTILOS CSS GLOBALES (SOLO TEMA OSCURO)
# ============================================
def get_theme_styles():
    """Retorna los estilos CSS, forzando el tema oscuro."""
    
    # Tema Oscuro
    return """
    <style>
        /* Tema Oscuro */
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1a1d24;
            border-right: 1px solid #262b35;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #fafafa;
        }
        
        /* Inputs */
        .stTextInput input, .stNumberInput input, .stDateInput input {
            background-color: #262b35 !important;
            color: #fafafa !important;
            border: 1px solid #404552 !important;
        }
        
        /* Selectbox */
        .stSelectbox [data-baseweb="select"] {
            background-color: #262b35 !important;
        }
        
        /* Botones */
        .stButton > button {
            background-color: #03a9f4;
            color: white;
            border: none;
            border-radius: 6px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #0288d1;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(3, 169, 244, 0.3);
        }
        
        /* Métricas */
        [data-testid="stMetricValue"] {
            color: #03a9f4;
            font-size: 1.8rem;
            font-weight: bold;
        }
        
        [data-testid="stMetricLabel"] {
            color: #b0b0b0;
        }
        
        /* Mensajes */
        .stAlert {
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        /* Dataframes */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #03a9f4;
        }
        
        /* Tabs - Menu lateral */
        .css-1544g2n {
            padding: 1rem;
        }
        
        /* Botón de descarga */
        .stDownloadButton > button {
            border: 2px solid #39FF14 !important;
            box-shadow: 0 0 12px rgba(57, 255, 20, 0.4) !important;
        }
        
        .stDownloadButton > button:hover {
            box-shadow: 0 0 20px rgba(57, 255, 20, 0.6) !important;
        }
        
        /* Radio buttons */
        .stRadio > label {
            color: #fafafa;
        }
    </style>
    """

# Aplicar estilos según tema
st.markdown(get_theme_styles(), unsafe_allow_html=True)

# ============================================
# SIDEBAR - MENÚ PRINCIPAL (ORDEN REQUERIDO)
# ============================================
with st.sidebar:
    # 1. USUARIO
    st.markdown("### 👤 Usuario")
    st.info(f"**{st.session_state.username}**")
    
    st.markdown("---")
    
    # 2. CONFIGURACIÓN - NAVEGACIÓN
    st.markdown("### Módulos")
    st.caption("Seleccione una pestaña para operar:")
    
    # Radio buttons para navegación
    page = st.radio(
        "Navegación:",
        ["Calcular Liquidación", "Nuevo Expediente", "Modificar estado EEM"],
        key="navigation_menu",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Información de la base de datos
    st.markdown("### 📊 Base de Datos")
    
    # Mostrar info después de cargar datos
    if 'df_principal' in st.session_state and st.session_state.df_principal is not None:
        df = st.session_state.df_principal
        st.metric("Registros", f"{len(df):,}")
    
    st.markdown("---")
    
    
    # Espacio flexible antes del botón de cerrar sesión
    st.markdown("<br>" * 3, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 3. PIE DE PÁGINA - BOTÓN DE CERRAR SESIÓN
    if st.button("Salir", key="btn_logout_sidebar", use_container_width=True, type="primary"):
        logout()
        st.rerun()
    
    st.caption("v2.5 | © 2025")

# ============================================
# HEADER PRINCIPAL
# ============================================
st.title("⚙️ Sistema de Liquidaciones")
st.caption("Cálculo de deuda y operaciones adicionales") #subtitulo
st.markdown("---")

# ============================================
# CARGA DE DATOS
# ============================================
script_dir = os.path.dirname(os.path.abspath(__file__))
ruta_json = os.path.join(script_dir, 'data', 'base_ucec.json')

@st.cache_data(ttl=600)  # Cache por 10 minutos
def load_data(ruta):
    return load_json_as_df(ruta)

with st.spinner("⏳ Cargando base de datos..."):
    df_principal = load_data(ruta_json)

if df_principal is None:
    st.error("❌ No se pudo cargar la base de datos")
    st.info(f"📁 Ruta: {ruta_json}")
    st.stop()

# Guardar en session_state para uso en sidebar
st.session_state.df_principal = df_principal


# ============================================
# RENDERIZAR PÁGINA SELECCIONADA
# ============================================
if page == "Calcular Liquidación":
    render_tab1(df_principal)
elif page == "Nuevo Expediente":
    render_tab2(df_principal, ruta_json)
elif page == "Modificar estado EEM":
    render_tab3(df_principal, ruta_json)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption("Sistema de Liquidaciones v2.5 | © 2025")