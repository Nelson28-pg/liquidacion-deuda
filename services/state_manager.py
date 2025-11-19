import streamlit as st
import uuid

def init_session_state():
    """Inicializa todas las variables del session_state."""
    
    # ===== Autenticación =====
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'show_matrix_loading' not in st.session_state:
        st.session_state.show_matrix_loading = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'loading_start_time' not in st.session_state:
        st.session_state.loading_start_time = None

    # ===== Búsqueda EEM (Tab 1) =====
    if 'tab1_correlativo' not in st.session_state:
        st.session_state.tab1_correlativo = ""
    if 'tab1_anio' not in st.session_state:
        st.session_state.tab1_anio = ""
    if 'tab1_intendencia' not in st.session_state:
        st.session_state.tab1_intendencia = ""
    if 'found_eem_record' not in st.session_state:
        st.session_state.found_eem_record = None
    if 'multiple_results' not in st.session_state:
        st.session_state.multiple_results = None
    if 'selected_eem' not in st.session_state:
        st.session_state.selected_eem = None
    if 'search_reset_key' not in st.session_state:
        st.session_state.search_reset_key = str(uuid.uuid4())
    if 'search_message' not in st.session_state:
        st.session_state.search_message = None
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    if 'expediente_no_encontrado' not in st.session_state:
        st.session_state.expediente_no_encontrado = False
    
    # ===== Cálculo (Tab 1) =====
    if 'calculation_data' not in st.session_state:
        st.session_state.calculation_data = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'calculation_message' not in st.session_state:
        st.session_state.calculation_message = None
    if 'fecha_liquidacion_seleccionada' not in st.session_state:
        st.session_state.fecha_liquidacion_seleccionada = None

    # ===== PDF =====
    if 'pdf_buffer' not in st.session_state:
        st.session_state.pdf_buffer = None
    if 'num_liquidacion_generado' not in st.session_state:
        st.session_state.num_liquidacion_generado = None
    if 'download_disabled' not in st.session_state:
        st.session_state.download_disabled = False
    if 'download_message' not in st.session_state:
        st.session_state.download_message = None
    if 'trigger_clean_after_download' not in st.session_state:
        st.session_state.trigger_clean_after_download = False

    # ===== Formulario Nuevo Dato (Tab 2) =====
    # NO inicializar ruc_input_search_tab2 aquí si es una key de widget
    
    # ===== Control del formulario Tab 2 =====
    if 'form_tab2_reset_key' not in st.session_state:
        st.session_state.form_tab2_reset_key = str(uuid.uuid4())
    if 'form_tab2_success_message' not in st.session_state:
        st.session_state.form_tab2_success_message = None
    if 'form_tab2_error_message' not in st.session_state:
        st.session_state.form_tab2_error_message = None
    if 'autocomplete_data' not in st.session_state:
        st.session_state.autocomplete_data = None

    
    
    """Inicializa estados de Tab 3 (Modificar Expediente)."""
    if 'tab3_search_performed' not in st.session_state:
        st.session_state.tab3_search_performed = False
    if 'tab3_expediente_encontrado' not in st.session_state:
        st.session_state.tab3_expediente_encontrado = None
    if 'tab3_success_message' not in st.session_state:
        st.session_state.tab3_success_message = None
    if 'tab3_error_message' not in st.session_state:
        st.session_state.tab3_error_message = None
    if 'tab3_reset_key' not in st.session_state:
        st.session_state.tab3_reset_key = str(uuid.uuid4())


def limpiar_busqueda():
    """Limpia la búsqueda de expedientes en Tab 1."""
    # Eliminar keys de widgets (NO asignar valores)
    keys_to_delete = [
        'tab1_correlativo',
        'tab1_anio',
        'tab1_intendencia',
        'fecha_liquidacion_input',
        'selected_eem_from_multiple',
        'tab1_eem_encontrado',
        'tab1_estado_expediente'
    ]
    
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    
    # Resetear variables de estado (NO son widgets)
    st.session_state.found_eem_record = None
    st.session_state.multiple_results = None
    st.session_state.selected_eem = None
    st.session_state.show_results = False
    st.session_state.calculation_data = None
    st.session_state.calculation_message = None
    st.session_state.fecha_liquidacion_seleccionada = None
    st.session_state.pdf_buffer = None
    st.session_state.num_liquidacion_generado = None
    st.session_state.download_disabled = False
    st.session_state.download_message = None
    st.session_state.search_message = None
    st.session_state.search_reset_key = str(uuid.uuid4())
    st.session_state.search_performed = False 
    st.session_state.expediente_no_encontrado = False


def limpiar_form_nuevo_dato():
    """
    Limpia el formulario de Tab 2 cambiando la key del formulario.
    NO intenta modificar directamente los valores de los widgets.
    """
    # Cambiar la key del formulario para forzar su recreación
    st.session_state.form_tab2_reset_key = str(uuid.uuid4())
    
    # ✅ ELIMINAR las keys de widgets (NO asignar valores)
    widget_keys_to_delete = ['ruc_input_search_tab2']
    
    for key in widget_keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    
    # Limpiar datos de autocompletado (NO es widget)
    st.session_state.autocomplete_data = None
    
    # Limpiar mensajes (NO son widgets)
    st.session_state.form_tab2_success_message = None
    st.session_state.form_tab2_error_message = None

def limpiar_busqueda_tab3():
    """Limpia los estados de búsqueda de Tab 3."""
    keys_to_delete = [
        'eem_input_search_tab3',
        'select_nuevo_estado',
        'input_nuevo_saldo'
    ]
    
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state.tab3_search_performed = False
    st.session_state.tab3_expediente_encontrado = None
    st.session_state.tab3_success_message = None
    st.session_state.tab3_error_message = None
    st.session_state.tab3_reset_key = str(uuid.uuid4())


def limpiar_todo():
    """Limpia completamente el session_state excepto datos de autenticación."""
    keys_to_keep = ['logged_in', 'username', 'show_matrix_loading', 'loading_start_time']
    keys_to_delete = [key for key in st.session_state.keys() if key not in keys_to_keep]
    
    for key in keys_to_delete:
        del st.session_state[key]
    
    # Reinicializar después de limpiar
    init_session_state()


def reset_download_state():
    """Resetea el estado del botón de descarga."""
    st.session_state.download_disabled = False
    st.session_state.download_message = None


def get_session_info():
    """Retorna información del estado actual de la sesión."""
    info = {
        'logged_in': st.session_state.get('logged_in', False),
        'username': st.session_state.get('username', 'N/A'),
        'has_search': st.session_state.get('found_eem_record') is not None,
        'has_calculation': st.session_state.get('calculation_data') is not None,
        'showing_results': st.session_state.get('show_results', False),
    }
    return info