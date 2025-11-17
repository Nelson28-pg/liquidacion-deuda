import streamlit as st
import base64
import os
import streamlit.components.v1 as components
from datetime import datetime
import time

# --- Authentication ---

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

# --- UI Rendering ---

def set_background(image_path):
    """Convierte una imagen local a base64 y la usa como fondo del sitio."""
    if not os.path.exists(image_path):
        # Usar fondo gradiente por defecto si no existe la imagen
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
        /* Ocultar elementos de Streamlit en la página de login */
        .stApp > header, #MainMenu, footer {{
            visibility: hidden;
        }}
        /* Aplicar fondo */
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
    """Muestra el login centrado y con fondo elegante."""
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
        
        /* Formulario de login centrado */
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
            margin-top: -5vh; /* Ajusta posición vertical (hacia arriba) */
        }
        
        /* Inputs de texto */
        .stTextInput > div > div > input {
            background-color: rgba(255,255,255,0.15); 
            color: white;
            border-radius: 6px; 
            padding: 10px;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(255,255,255,0.5);
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
            transition: background-color 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #0288d1;
        }
        
        /* Título personalizado */
        .custom-title {
            color: #03a9f4; 
            text-align: center; 
            font-size: 28px;
            font-weight: 700; 
            margin-bottom: 2rem;
        }
        
        /* Animaciones */
        @keyframes fade-in {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        
        .stAlert {
            animation: fade-in 0.3s ease-out;
        }
        
        /* Ocultar scrollbar en todos los navegadores */
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

    # Contenedor para centrar el formulario
    _, col_form, _ = st.columns([1, 1.5, 1])

    with col_form:
        with st.form("login_form"):
            st.markdown("<div class='custom-title'>Iniciar Sesión</div>", unsafe_allow_html=True)
            username = st.text_input("Usuario", key="login_username", placeholder="analista01")
            password = st.text_input("Contraseña", type="password", key="login_password", placeholder="********")
            submitted = st.form_submit_button("Ingresar")

            if submitted:
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.show_matrix_loading = True
                    st.session_state.loading_start_time = time.time()
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
    
    return False

def render_loading_page():
    """
    Muestra una pantalla de carga que ocupa toda la pantalla por 6 segundos.
    """
    current_hour = datetime.now().hour
    greeting = "Buenas noches"
    if 5 <= current_hour < 12:
        greeting = "Buenos días"
    elif 12 <= current_hour < 19:
        greeting = "Buenas tardes"

    username = st.session_state.get('username', 'Usuario')

    # Ocultar completamente todos los elementos de Streamlit
    st.markdown("""
        <style>
            .stApp > header, #MainMenu, footer, [data-testid="stToolbar"] {
                visibility: hidden !important;
                display: none !important;
            }
            iframe {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                border: none !important;
                z-index: 999999 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    loading_html = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cargando...</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body, html {{ 
                width: 100vw;
                height: 100vh;
                overflow: hidden; 
                background-color: #000; /* 🎨 Color de fondo principal */
                font-family: 'Courier New', Courier, monospace; /* 🎨 Fuente del texto */
            }}
            
            #loading-container {{
                position: fixed; 
                top: 0; 
                left: 0; 
                width: 100vw; 
                height: 100vh;
                display: flex; 
                flex-direction: column;
                justify-content: center; 
                align-items: center;
                z-index: 9999;
            }}
            
            #matrix-canvas {{
                position: absolute; 
                top: 0; 
                left: 0; 
                width: 100%; 
                height: 100%;
                z-index: 1; 
                opacity: 0.25; /* 🎨 Transparencia del efecto Matrix (0.1 = muy transparente, 1.0 = opaco) */
            }}
            
            .welcome-text, .subtitle-text {{
                position: relative; 
                z-index: 2;
                text-align: center;
                animation: fade-in 1.2s ease-out; /* 🎨 Duración de la animación de aparición */
            }}
            
            .welcome-text {{ 
                color: #fff; /* 🎨 Color del título principal (blanco) */
                font-size: 3.5rem; /* 🎨 Tamaño del título */
                font-weight: bold; /* ✅ Título en negrita */
                text-shadow: 0 0 20px rgba(255, 255, 255, 0.8), 
                             0 0 30px rgba(255, 255, 255, 0.6); /* 🎨 Resplandor del título */
                margin-bottom: 20px; /* 🎨 Espacio entre título y subtítulo */
                letter-spacing: 2px; /* 🎨 Espaciado entre letras */
            }}
            
            .subtitle-text {{ 
                color: #0f0; /* 🎨 Color del subtítulo (verde Matrix) */
                font-size: 1.8rem; /* 🎨 Tamaño del subtítulo */
                font-weight: 500; /* 🎨 Grosor del subtítulo */
                text-shadow: 0 0 10px #0f0, 0 0 20px #0f0; /* 🎨 Resplandor del subtítulo */
            }}
            
            @keyframes fade-in {{
                from {{ opacity: 0; transform: translateY(-30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>
    </head>
    <body>
        <div id="loading-container">
            <canvas id="matrix-canvas"></canvas>
            <div class="welcome-text">Bienvenido, {username.capitalize()}</div>
            <div class="subtitle-text">{greeting}</div>
        </div>
        <script>
            (function() {{
                try {{
                    // ========== CONFIGURACIÓN DEL EFECTO MATRIX ==========
                    const canvas = document.getElementById('matrix-canvas');
                    const ctx = canvas.getContext('2d');
                    
                    // Ajustar canvas al tamaño de la ventana
                    canvas.width = window.innerWidth;
                    canvas.height = window.innerHeight;
                    
                    // 🎨 Caracteres que caerán (puedes agregar o quitar caracteres)
                    const alphabet = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッンABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
                    
                    // 🎨 Tamaño de la fuente (afecta la densidad del efecto)
                    const fontSize = 16;
                    
                    const columns = Math.floor(canvas.width / fontSize);
                    const rainDrops = [];
                    
                    // Inicializar gotas de lluvia en posiciones aleatorias
                    for (let x = 0; x < columns; x++) {{ 
                        rainDrops[x] = Math.floor(Math.random() * canvas.height / fontSize); 
                    }}
                    
                    // ========== FUNCIÓN DE DIBUJO DEL EFECTO MATRIX ==========
                    function draw() {{
                        // 🎨 Transparencia del rastro (0.05 = rastro más largo, 0.1 = rastro más corto)
                        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        
                        // 🎨 Color de los caracteres Matrix (verde)
                        ctx.fillStyle = '#0F0';
                        ctx.font = fontSize + 'px monospace';
                        
                        // Dibujar cada columna de caracteres
                        for (let i = 0; i < rainDrops.length; i++) {{
                            const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
                            ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
                            
                            // 🎨 Probabilidad de reinicio de columna (0.975 = más frecuente, 0.99 = menos frecuente)
                            if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {{
                                rainDrops[i] = 0;
                            }}
                            rainDrops[i]++;
                        }}
                    }}
                    
                    // ========== INICIAR ANIMACIÓN ==========
                    // 🎨 Velocidad del efecto (33ms = ~30fps, 16ms = ~60fps)
                    const animationInterval = setInterval(draw, 33);
                    
                    // ========== DURACIÓN DE LA PANTALLA DE CARGA ==========
                    // 🎨 Tiempo en milisegundos (3000 = 3 segundos)
                    setTimeout(function() {{
                        clearInterval(animationInterval);
                        console.log('Pantalla de carga completada');
                    }}, 3000);
                    
                }} catch (e) {{
                    console.error('Error en pantalla de carga:', e);
                }}
            }})();
        </script>
    </body>
    </html>
    '''
    
    # Renderizar HTML con altura completa
    components.html(loading_html, height=900, scrolling=False)
    
    # Control de tiempo usando session_state
    if 'loading_start_time' not in st.session_state:
        st.session_state.loading_start_time = time.time()
    
    elapsed_time = time.time() - st.session_state.loading_start_time
    
    # Después de 6 segundos, desactivar el loading
    if elapsed_time >= 6:
        st.session_state.show_matrix_loading = False
        if 'loading_start_time' in st.session_state:
            del st.session_state.loading_start_time
        st.rerun()
    else:
        # Verificar cada segundo
        time.sleep(1)
        st.rerun()

def logout():
    """Cierra la sesión y limpia todos los datos."""
    # Lista de keys críticas que deben reinicializarse
    critical_keys = {
        'logged_in': False,
        'username': "",
        'user_role': ""
    }
    
    # Eliminar todas las keys
    keys_to_delete = list(st.session_state.keys())
    for key in keys_to_delete:
        del st.session_state[key]
    
    # Reinicializar keys críticas
    for key, value in critical_keys.items():
        st.session_state[key] = value
    
    st.rerun()
    