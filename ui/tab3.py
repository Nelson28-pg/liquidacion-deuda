import streamlit as st
import pandas as pd
from datetime import datetime
from services.data_manager import update_expediente_in_json, get_expediente_by_eem_abrev
import json
import os

def render_tab3(df_principal, ruta_json):
    """Renderiza la pestaña para modificar expedientes existentes."""
    
    # Inicializar estados
    if 'tab3_search_performed' not in st.session_state:
        st.session_state.tab3_search_performed = False
    if 'tab3_expediente_encontrado' not in st.session_state:
        st.session_state.tab3_expediente_encontrado = None
    if 'tab3_success_message' not in st.session_state:
        st.session_state.tab3_success_message = None
    if 'tab3_error_message' not in st.session_state:
        st.session_state.tab3_error_message = None
    
    # Mostrar mensajes
    if st.session_state.tab3_success_message:
        st.success(st.session_state.tab3_success_message)
        st.session_state.tab3_success_message = None
    
    if st.session_state.tab3_error_message:
        st.error(st.session_state.tab3_error_message)
        st.session_state.tab3_error_message = None
    
    # --- Búsqueda por EEM Abreviado ---
    st.markdown("### 🔍 Buscar por Multa (EEM)")
    
    col_eem_search, col_btn_search = st.columns([3, 1])
    
    with col_eem_search:
        eem_search = st.text_input(
            "Digite el EEM Abreviado", 
            key="eem_input_search_tab3",
            placeholder="Ej: 123452024LIM",
            disabled=st.session_state.tab3_search_performed
        )
    
    with col_btn_search:
        st.write("")
        st.write("")
        if st.button("🔎 Buscar", key="btn_eem_search", use_container_width=True,
                    disabled=st.session_state.tab3_search_performed):
            if eem_search and eem_search.strip():
                if df_principal is not None and 'EEM_ABREV' in df_principal.columns:
                    found_record = df_principal[df_principal['EEM_ABREV'] == eem_search.strip().upper().zfill(12)]
                    if not found_record.empty:
                        expediente = found_record.iloc[0].to_dict()
                        
                        # Verificar si está cancelado
                        if expediente.get('ESTADO', '').upper() == 'CANCELADO':
                            st.session_state.tab3_error_message = "❌ No se puede modificar un expediente CANCELADO"
                            st.rerun()
                        else:
                            st.session_state.tab3_expediente_encontrado = expediente
                            st.session_state.tab3_search_performed = True
                            st.success(f"✅ Expediente encontrado: {expediente['EEM']}")
                            st.rerun()
                    else:
                        st.warning(f"⚠️ EEM '{eem_search}' no encontrado en la base de datos")
                else:
                    st.error("❌ Error: La columna 'EEM_ABREV' no existe en la base de datos")
            else:
                st.warning("⚠️ Por favor, ingrese un EEM para buscar")
    
    # Botón de nueva búsqueda
    if st.session_state.tab3_search_performed:
        if st.button("🔄 Nueva Búsqueda", key="btn_new_search"):
            st.session_state.tab3_search_performed = False
            st.session_state.tab3_expediente_encontrado = None
            if 'eem_input_search_tab3' in st.session_state:
                del st.session_state['eem_input_search_tab3']
            st.rerun()
    
    st.markdown("---")
    
    # --- Formulario de Modificación ---
    if st.session_state.tab3_expediente_encontrado:
        expediente = st.session_state.tab3_expediente_encontrado
        
        st.markdown("### 📝 Modificar Datos del Expediente")
        st.info(f"**EEM:** {expediente.get('EEM', 'N/A')} | **Obligado:** {expediente.get('OBLIGADO', 'N/A')}")
        
        with st.form("modify_expediente_form", clear_on_submit=False):
            
            # Mostrar datos actuales en dos columnas
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Datos Actuales")
                st.text_input("Estado Actual", value=expediente.get('ESTADO', 'N/A'), disabled=True)
                st.text_input("Saldo Inicial Actual", value=f"S/ {expediente.get('SALDO INICIAL', 0):,.2f}", disabled=True)
            
            with col2:
                st.markdown("#### Nuevos Datos")
                
                # Campo para modificar Estado
                estado_actual = expediente.get('ESTADO', '')
                estados_disponibles = [
                    "ANULADO",
                    "CADUCIDAD",
                    "CANCELADO",
                    "COBRANZA COACTIVA",
                    "DERIVADO",
                    "DEVUELTO",
                    "FRACCIONAMIENTO",
                    "JUDICIALIZADO",
                    "NULIDAD",
                    "PENDIENTE DE PAGO",
                    "PERDIDAD DE EXIGIBILIDAD",
                    "SALDO A FAVOR"
                ]
                
                # Encontrar el índice del estado actual
                try:
                    index_actual = estados_disponibles.index(estado_actual)
                except ValueError:
                    index_actual = 0
                
                nuevo_estado = st.selectbox(
                    "Nuevo Estado",
                    options=estados_disponibles,
                    index=index_actual,
                    key="select_nuevo_estado"
                )
                
                # Campo para modificar Saldo Inicial
                nuevo_saldo = st.number_input(
                    "Nuevo Saldo Inicial (S/)",
                    min_value=0.0,
                    value=float(expediente.get('SALDO INICIAL', 0)),
                    step=0.01,
                    format="%.2f",
                    key="input_nuevo_saldo"
                )
            
            st.markdown("---")
            
            # Botones del formulario
            col_submit, col_cancel, col_space = st.columns([1, 1, 3])
            
            with col_submit:
                submitted = st.form_submit_button(
                    "💾 Guardar Cambios",
                    use_container_width=True
                )
            
            with col_cancel:
                cancelled = st.form_submit_button(
                    "❌ Cancelar",
                    use_container_width=True
                )
            
            # Procesar formulario
            if submitted:
                # Verificar si hubo cambios
                estado_cambio = nuevo_estado != expediente.get('ESTADO', '')
                saldo_cambio = abs(nuevo_saldo - float(expediente.get('SALDO INICIAL', 0))) > 0.01
                
                if not estado_cambio and not saldo_cambio:
                    st.session_state.tab3_error_message = "⚠️ No se detectaron cambios en los datos"
                    st.rerun()
                
                # Validaciones
                if nuevo_saldo <= 0:
                    st.session_state.tab3_error_message = "❌ El saldo inicial debe ser mayor a 0"
                    st.rerun()
                
                try:
                    # Preparar datos de cambio
                    cambios = {
                        'ESTADO': nuevo_estado,
                        'SALDO INICIAL': float(nuevo_saldo),
                        'FECHA_MODIFICACION': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'USUARIO_MODIFICACION': st.session_state.get('username', 'desconocido')
                    }
                    
                    # Guardar cambios
                    resultado = update_expediente_in_json(
                        ruta_json=ruta_json,
                        eem_abrev=expediente['EEM_ABREV'],
                        cambios=cambios,
                        estado_anterior=expediente.get('ESTADO', ''),
                        saldo_anterior=float(expediente.get('SALDO INICIAL', 0))
                    )
                    
                    if resultado['success']:
                        # Registrar en log de cambios
                        registrar_cambio_log(
                            ruta_json=ruta_json,
                            eem=expediente['EEM'],
                            eem_abrev=expediente['EEM_ABREV'],
                            campo_modificado="ESTADO/SALDO INICIAL",
                            valor_anterior=f"{expediente.get('ESTADO', '')}/{expediente.get('SALDO INICIAL', 0):.2f}",
                            valor_nuevo=f"{nuevo_estado}/{nuevo_saldo:.2f}",
                            usuario=st.session_state.get('username', 'desconocido')
                        )
                        
                        # Limpiar caché
                        st.cache_data.clear()
                        
                        st.session_state.tab3_success_message = f"✅ Expediente {expediente['EEM']} modificado exitosamente"
                        st.session_state.tab3_search_performed = False
                        st.session_state.tab3_expediente_encontrado = None
                        st.rerun()
                    else:
                        st.session_state.tab3_error_message = f"❌ {resultado['message']}"
                        st.rerun()
                
                except Exception as e:
                    st.session_state.tab3_error_message = f"❌ Error al guardar cambios: {str(e)}"
                    st.rerun()
            
            if cancelled:
                st.session_state.tab3_search_performed = False
                st.session_state.tab3_expediente_encontrado = None
                st.rerun()
    
    # --- Mostrar últimos 10 cambios realizados ---
    st.markdown("---")
    st.subheader("📊 Últimos 10 Cambios Realizados")
    
    # Cargar log de cambios
    cambios_log = cargar_log_cambios(ruta_json)
    
    if cambios_log and len(cambios_log) > 0:
        df_cambios = pd.DataFrame(cambios_log)
        
        # Ordenar por fecha descendente
        if 'FECHA_CAMBIO' in df_cambios.columns:
            df_cambios = df_cambios.sort_values('FECHA_CAMBIO', ascending=False).head(10)
        else:
            df_cambios = df_cambios.tail(10)
        
        # Seleccionar columnas para mostrar
        columns_to_show = ['EEM', 'CAMPO_MODIFICADO', 'VALOR_ANTERIOR', 'VALOR_NUEVO', 
                          'FECHA_CAMBIO', 'USUARIO']
        
        available_columns = [col for col in columns_to_show if col in df_cambios.columns]
        
        if available_columns:
            st.dataframe(
                df_cambios[available_columns],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("ℹ️ No hay cambios registrados")
    else:
        st.info("ℹ️ No hay cambios registrados en el sistema")


def registrar_cambio_log(ruta_json, eem, eem_abrev, campo_modificado, valor_anterior, valor_nuevo, usuario):
    """Registra un cambio en el log de modificaciones."""
    try:
        # Ruta del archivo de log
        log_dir = os.path.dirname(ruta_json)
        log_file = os.path.join(log_dir, 'cambios_log.json')
        
        # Cargar log existente
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        else:
            log_data = []
        
        # Crear nuevo registro
        nuevo_registro = {
            'EEM': eem,
            'EEM_ABREV': eem_abrev,
            'CAMPO_MODIFICADO': campo_modificado,
            'VALOR_ANTERIOR': valor_anterior,
            'VALOR_NUEVO': valor_nuevo,
            'FECHA_CAMBIO': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'USUARIO': usuario
        }
        
        # Agregar al log
        log_data.append(nuevo_registro)
        
        # Mantener solo los últimos 100 cambios
        if len(log_data) > 100:
            log_data = log_data[-100:]
        
        # Guardar log
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=4)
        
        return True
    
    except Exception as e:
        print(f"Error al registrar cambio en log: {e}")
        return False


def cargar_log_cambios(ruta_json):
    """Carga el log de cambios realizados."""
    try:
        log_dir = os.path.dirname(ruta_json)
        log_file = os.path.join(log_dir, 'cambios_log.json')
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    
    except Exception as e:
        print(f"Error al cargar log de cambios: {e}")
        return []