import streamlit as st
import base64
import os

# ============================================
# USUARIOS DEL SISTEMA
# ============================================
USERS = {
    "analista01": "analista2020*",
    "analista02": "analista2021*",
    "analista03": "analista2022*",
    "analista04": "analista2023*",
    "analista05": "analista2024*",
    "invitado01": "invitadoucec*"
}

def check_login(username, password):
    """Verifica si el usuario y la contraseña son válidos."""
    return USERS.get(username) == password

# ============================================
# PÁGINA DE LOGIN
# ============================================
def set_background(image_path):
    """Convierte una imagen local a base64 y la usa como fondo del sitio."""
    if not os.path.exists(image_path):
        # Usar fondo gradiente por defecto
        css = """
        <style>
            .stApp > header, #MainMenu, footer {
                visibility: hidden;
            }
            .stApp {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
        return
    
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    css = f"""
    <style>
        .stApp > header, #MainMenu, footer {{
            visibility: hidden;
        }}
        .stApp {{
            background: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_login_page():
    """Muestra el login centrado con fondo elegante."""
    if st.session_state.get('logged_in', False):
        return True

    set_background("./img/workspace.jpg")

    login_css = """
    <style>
        /* Ocultar scrollbar y expandir a pantalla completa */
        #root > div:nth-child(1) > div > div > div > div > section.main {
            overflow: hidden !important;
            height: 100vh !important;
        }
        
        /* Ocultar header de Streamlit */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Contenedor principal */
        div[data-testid="stVerticalBlock"] {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            min-height: 100vh !important;
            height: 100vh !important;
            overflow: hidden !important;
        }
        
        div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
            width: 100%;
        }
        
        /* Formulario de login */
        div[data-testid="stForm"] {
            background-color: rgba(0, 0, 0, 0.65); 
            padding: 2.5rem 3rem;
            border-radius: 12px; 
            width: 460px;
            height: 560px;
            align-items: center; 
            display: flex; 
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
            backdrop-filter: blur(5px); 
            animation: fade-in 0.9s ease-out;
            position: relative;
            margin-top: -5vh;
        }
        
        /* Inputs de texto - TEXTO NEGRO */
        .stTextInput > div > div > input {
            background-color: rgba(255,255,255,0.9) !important; 
            color: #000000 !important; /* ✅ TEXTO NEGRO */
            border-radius: 6px; 
            padding: 10px;
            border: 1px solid rgba(3, 169, 244, 0.3);
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #666666 !important; /* Placeholder gris oscuro */
        }
        
        .stTextInput > div > div > input:focus {
            border: 2px solid #03a9f4 !important;
            background-color: rgba(255,255,255,1) !important;
        }
        
        /* Labels de inputs */
        .stTextInput > label {
            color: #ffffff !important;
            font-weight: 500;
        }
        
        /* Botón de login */
        .stButton > button {
            background-color: #03a9f4; 
            color: white; 
            width: 100%;
            height: 45px; 
            border-radius: 6px;
            font-size: 16px; 
            font-weight: 600;
            margin-top: 1rem;
            transition: all 0.3s ease;
            border: none;
        }
        
        .stButton > button:hover {
            background-color: #0288d1;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(3, 169, 244, 0.4);
        }
        
        /* Título personalizado */
        .custom-title {
            color: #03a9f4; 
            text-align: center; 
            font-size: 28px;
            font-weight: 700; 
            margin-bottom: 2rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        /* Mensajes de error */
        .stAlert {
            animation: shake 0.5s ease-out;
            border-radius: 8px;
        }
        
        /* Animaciones */
        @keyframes fade-in {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        /* Ocultar scrollbar */
        ::-webkit-scrollbar {
            display: none;
        }
        
        * {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
    </style>
    """
    st.markdown(login_css, unsafe_allow_html=True)

    # Contenedor para centrar
    _, col_form, _ = st.columns([1, 1.5, 1])

    with col_form:
        with st.form("login_form"):
            st.markdown("<div class='custom-title'>🔐 Iniciar Sesión</div>", unsafe_allow_html=True)
            
            username = st.text_input(
                "Usuario", 
                key="login_username", 
                placeholder="analista01",
                help="Ingrese su nombre de usuario"
            )
            
            password = st.text_input(
                "Contraseña", 
                type="password", 
                key="login_password", 
                placeholder="********",
                help="Ingrese su contraseña"
            )
            
            submitted = st.form_submit_button("🚀 Ingresar")

            if submitted:
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    from datetime import datetime
                    st.session_state.last_activity = datetime.now()
                    st.success("✅ Acceso concedido")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
    
    # Footer del login
    st.markdown("""
        <div style='position: fixed; bottom: 20px; width: 100%; text-align: center;'>
            <p style='color: rgba(255,255,255,0.6); font-size: 12px;'>
                Sistema de Liquidaciones v2.5 | © 2025
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    return False

# ============================================
# LOGOUT
# ============================================
def logout():
    """Cierra la sesión y limpia todos los datos."""
    critical_keys = {
        'logged_in': False,
        'username': "",
        'dark_mode': False
    }
    
    # Eliminar todas las keys
    keys_to_delete = list(st.session_state.keys())
    for key in keys_to_delete:
        del st.session_state[key]
    
    # Reinicializar keys críticas
    for key, value in critical_keys.items():
        st.session_state[key] = value
    
    st.success("👋 Sesión cerrada exitosamente")
    st.rerun()