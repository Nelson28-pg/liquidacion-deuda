import streamlit as st
import pandas as pd
from datetime import datetime
from services.data_manager import save_record_to_json
from services.state_manager import limpiar_form_nuevo_dato

def render_tab2(df_principal, ruta_json):
    """Renderiza la pestaña para agregar nuevos EEM."""
    
    # Mostrar mensajes si existen
    if st.session_state.get('form_tab2_success_message'):
        st.success(st.session_state.form_tab2_success_message)
        st.session_state.form_tab2_success_message = None
    
    if st.session_state.get('form_tab2_error_message'):
        st.error(st.session_state.form_tab2_error_message)
        st.session_state.form_tab2_error_message = None
    
    # --- Búsqueda por RUC para Autocompletar ---
    st.markdown("### 🔍 Buscar por RUC para Autocompletar")
    
    col_ruc_search, col_btn_ruc_search = st.columns([3, 1])
    
    with col_ruc_search:
        ruc_search = st.text_input(
            "Digite el RUC", 
            key="ruc_input_search_tab2",
            max_chars=11,
            placeholder="Ingrese 11 dígitos del RUC"
        )
    
    with col_btn_ruc_search:
        st.write("")
        st.write("")
        if st.button("🔎 Buscar", key="btn_ruc_autocomplete", use_container_width=True):
            if ruc_search and ruc_search.strip():
                if df_principal is not None and 'RUC' in df_principal.columns:
                    found_record = df_principal[df_principal['RUC'] == str(ruc_search.strip())]
                    if not found_record.empty:
                        # Guardar datos para autocompletar
                        st.session_state.autocomplete_data = {
                            'RUC': found_record['RUC'].iloc[0],
                            'OBLIGADO': found_record.get('OBLIGADO', pd.Series([''])).iloc[0]
                        }
                        #st.success(f"✅ RUC encontrado: {st.session_state.autocomplete_data['OBLIGADO']}")
                    else:
                        st.session_state.autocomplete_data = None
                        st.warning(f"⚠️ RUC '{ruc_search}' no encontrado en la base de datos.")
                else:
                    st.error("❌ Error: La columna 'RUC' no existe en la base de datos.")
            else:
                st.warning("⚠️ Por favor, ingrese un RUC para buscar.")
    
    #st.markdown("---")
    
    # --- Formulario de Nuevo Dato ---
    # Usar la key dinámica para forzar recreación del formulario cuando se limpia
    form_key = f"nuevo_dato_form_{st.session_state.get('form_tab2_reset_key', 'default')}"
    
    with st.form(form_key, clear_on_submit=False):
        st.markdown("### 📋 Datos del Expediente")
        
        # Valores por defecto desde autocompletado
        default_obligado = ""
        default_ruc = ""
        
        if st.session_state.get('autocomplete_data'):
            default_obligado = st.session_state.autocomplete_data.get('OBLIGADO', '')
            default_ruc = st.session_state.autocomplete_data.get('RUC', '')
        
        col1, col2 = st.columns(2)
        
        with col1:
            obligado = st.text_input(
                "Nombre del Obligado*", 
                value=default_obligado,
                placeholder="Razón Social o Nombre Completo",
            )
        
        with col2:
            ruc = st.text_input(
                "RUC*", 
                value=default_ruc,
                max_chars=11,
                placeholder="11 dígitos",
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            eem = st.text_input(
                "Expediente Ejecución de Multa (EEM)*", 
                placeholder="",
            )
        
        with col4:
            eem_abrev = st.text_input(
                "EEM Abreviado*", 
                placeholder="Ej: 123452024LIM",
            )
        
        col5, col6 = st.columns(2)
        
        with col5:
            saldo_inicial = st.number_input(
                "Saldo Inicial (S/)*", 
                min_value=0.0,
                step=0.01,
                format="%.2f",
            )
        
        with col6:
            fecha_consentimiento = st.date_input(
                "Fecha Consentimiento*", 
                value=None,
                min_value=datetime(2000, 1, 1),
                max_value=datetime(2100, 12, 31),
            )
        
        st.markdown("### 📄 Instancias")
        
        col7, col8 = st.columns(2)
        
        with col7:
            resol_subintendencia = st.text_input(
                "Resolución de Subintendencia (RSI)", 
                placeholder=""
            )
        
        with col8:
            fecha_noti_rsi = st.date_input(
                "Fecha de Notificación de RSI", 
                value=None,
                min_value=datetime(2000, 1, 1),
                max_value=datetime(2100, 12, 31),
            )
        
        col9, col10 = st.columns(2)
        
        with col9:
            resol_intendencia = st.text_input(
                "Resolución de Intendencia (RI)", 
                placeholder=""
            )
        
        with col10:
            fecha_noti_ri = st.date_input(
                "Fecha de Notificación de RI", 
                value=None,
                min_value=datetime(2000, 1, 1),
                max_value=datetime(2100, 12, 31)
            )
        
        estado = st.selectbox(
            "Estado del EEM*",
            options=[
                "Seleccione un estado",
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
            ],
        )
        
        st.caption("*Campos obligatorios")
        
        # Botones del formulario
        col_submit, col_clear, col_space = st.columns([1, 1, 3])
        
        with col_submit:
            submitted = st.form_submit_button(
                "✅ Guardar EEM",
                use_container_width=True
            )
        
        with col_clear:
            cleared = st.form_submit_button(
                "🗑️ Limpiar",
                use_container_width=True
            )
        
        # Procesar el formulario
        if submitted:
            # Validaciones
            if not obligado or not obligado.strip():
                st.session_state.form_tab2_error_message = "❌ El campo 'Obligado' es obligatorio"
                st.rerun()
            
            elif not ruc or not ruc.strip():
                st.session_state.form_tab2_error_message = "❌ El campo 'RUC' es obligatorio"
                st.rerun()
            
            elif len(ruc.strip()) != 11 or not ruc.strip().isdigit():
                st.session_state.form_tab2_error_message = "❌ El RUC debe tener exactamente 11 dígitos numéricos"
                st.rerun()
            
            elif not eem or not eem.strip():
                st.session_state.form_tab2_error_message = "❌ El campo 'EEM' es obligatorio"
                st.rerun()
            
            elif not eem_abrev or not eem_abrev.strip():
                st.session_state.form_tab2_error_message = "❌ El campo 'EEM Abreviado' es obligatorio"
                st.rerun()
            
            elif saldo_inicial <= 0:
                st.session_state.form_tab2_error_message = "❌ El saldo inicial debe ser mayor a 0"
                st.rerun()
            
            elif estado == "Seleccione un estado":
                st.session_state.form_tab2_error_message = "❌ Debe seleccionar un estado para el EEM"
                st.rerun()
            
            else:
                # Verificar si el EEM ya existe
                if df_principal is not None and 'EEM_ABREV' in df_principal.columns:
                    if not df_principal[df_principal["EEM_ABREV"] == eem_abrev.strip()].empty:
                        st.session_state.form_tab2_error_message = f"❌ El EEM **{eem_abrev}** ya existe en la base de datos"
                        st.rerun()
                
                # Crear nuevo registro

                try:
                    eem_abrev_procesado = eem_abrev.strip().upper().zfill(12)
                    new_record = {
                        "EEM": eem.strip().upper(),
                        "EEM_ABREV": eem_abrev_procesado,
                        "OBLIGADO": obligado.strip().upper(),
                        "RUC": ruc.strip(),
                        "SALDO INICIAL": float(saldo_inicial),
                        "ESTADO": estado,
                        "RESOL_SUBINTENDENCIA": resol_subintendencia.strip().upper() if resol_subintendencia else "",
                        "FEC_NOTI_RSI": fecha_noti_rsi.strftime("%d/%m/%Y") if fecha_noti_rsi else "",
                        "RESOL_INTENDENCIA": resol_intendencia.strip().upper() if resol_intendencia else "",
                        "FEC_NOTI_RI": fecha_noti_ri.strftime("%d/%m/%Y") if fecha_noti_ri else "",
                        "FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA": fecha_consentimiento.strftime("%d/%m/%Y"),
                        "FECHA_REGISTRO": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "USUARIO_REGISTRO": st.session_state.get('username', 'desconocido')
                    }
                    
                    # Guardar en JSON
                    save_record_to_json(new_record, ruta_json)
                    
                    # Limpiar caché para recargar datos
                    st.cache_data.clear()
                    
                    # Mensaje de éxito y limpiar formulario
                    #st.session_state.form_tab2_success_message = f"✅ EEM **{eem}** agregado exitosamente"
                    limpiar_form_nuevo_dato()
                    st.rerun()
                    
                except Exception as e:
                    st.session_state.form_tab2_error_message = f"❌ Error al guardar: {str(e)}"
                    st.rerun()
        
        # Si se presionó limpiar
        if cleared:
            limpiar_form_nuevo_dato()
            st.rerun()
    
    # --- Mostrar últimos EEM registrados ---
    st.markdown("---")
    st.subheader("📊 Últimos 10 EEM Registrados")
    
    if df_principal is not None and not df_principal.empty:
        # Verificar si existe la columna FECHA_REGISTRO
        if 'FECHA_REGISTRO' in df_principal.columns:
            df_display = df_principal.sort_values('FECHA_REGISTRO', ascending=False).head(10)
        else:
            df_display = df_principal.tail(10)
        
        # Seleccionar columnas para mostrar
        columns_to_show = ['EEM', 'OBLIGADO', 'RUC', 'ESTADO', 'SALDO INICIAL']
        
        # Agregar FECHA_REGISTRO y USUARIO_REGISTRO si existen
        if 'FECHA_REGISTRO' in df_display.columns:
            columns_to_show.append('FECHA_REGISTRO')
        if 'USUARIO_REGISTRO' in df_display.columns:
            columns_to_show.append('USUARIO_REGISTRO')
        
        available_columns = [col for col in columns_to_show if col in df_display.columns]
        
        if available_columns:
            st.dataframe(
                df_display[available_columns],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("⚠️ No hay columnas disponibles para mostrar")
    else:
        st.info("ℹ️ No hay expedientes registrados en la base de datos")