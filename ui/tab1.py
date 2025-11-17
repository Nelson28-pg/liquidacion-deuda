import streamlit as st
import pandas as pd
from datetime import datetime
import re
from utils.calculos import calcular_monto_actualizado
from utils.contador import get_contador, generar_numero_liquidacion, incrementar_contador
from services.pdf_generator import generar_pdf_liquidacion
from services.state_manager import limpiar_busqueda

def render_tab1(df_principal):
    """Renderiza la pestaña de cálculo de liquidación."""

    # Verificar si se debe limpiar después de descargar
    if st.session_state.get('trigger_clean_after_download', False):
        st.session_state.trigger_clean_after_download = False
        limpiar_busqueda()

    # Inicializar estados si no existen
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    if 'expediente_no_encontrado' not in st.session_state:
        st.session_state.expediente_no_encontrado = False
    
    # --- 1. Búsqueda del Expediente ---
    st.markdown("")
    st.subheader("🔍 1. Búsqueda del Expediente de Ejecución de Multa")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    
    with col1:
        st.text_input(
            "Correlativo del EEM", 
            max_chars=5, 
            key="tab1_correlativo",
            disabled=st.session_state.search_performed  # 🔒 Bloquear después de búsqueda exitosa
        )
    
    with col2:
        st.text_input(
            "Año del EEM", 
            max_chars=4, 
            key="tab1_anio",
            disabled=st.session_state.search_performed  # 🔒 Bloquear después de búsqueda exitosa
        )
    
    with col3:
        st.text_input(
            "Intendencia del EEM", 
            max_chars=3, 
            key="tab1_intendencia",
            disabled=st.session_state.search_performed  # 🔒 Bloquear después de búsqueda exitosa
        )
    
    with col4:
        st.write("")
        st.write("")
        if st.button(
            "🔎 Buscar Expediente", 
            key="btn_buscar_expediente", 
            use_container_width=True,
            disabled=st.session_state.search_performed  # 🔒 Bloquear después de búsqueda exitosa
        ):
            # Validaciones
            if not (st.session_state.tab1_correlativo.strip() and 
                   st.session_state.tab1_anio.strip() and 
                   st.session_state.tab1_intendencia.strip()):
                st.session_state.search_message = ("warning", "⚠️ Por favor, complete todos los campos del EEM.")
            
            elif not st.session_state.tab1_correlativo.isdigit() or len(st.session_state.tab1_correlativo) > 5:
                st.session_state.search_message = ("warning", "⚠️ El correlativo solo debe contener números (máx. 5 dígitos).")
            
            elif not st.session_state.tab1_anio.isdigit() or len(st.session_state.tab1_anio) != 4:
                st.session_state.search_message = ("warning", "⚠️ El año debe ser un número de 4 dígitos.")
            
            elif len(st.session_state.tab1_intendencia) != 3 or not st.session_state.tab1_intendencia.isalpha():
                st.session_state.search_message = ("warning", "⚠️ La intendencia debe contener exactamente 3 letras.")
            
            else:
                # Búsqueda
                with st.spinner("🔍 Buscando expediente..."):
                    correlativo_norm = st.session_state.tab1_correlativo.zfill(5)
                    anio_norm = st.session_state.tab1_anio
                    intend_norm = st.session_state.tab1_intendencia.upper()
                    eem_buscado = f"{correlativo_norm}{anio_norm}{intend_norm}"
                    
                    resultado = df_principal[df_principal["EEM_ABREV"] == eem_buscado]

                    if not resultado.empty:
                        if len(resultado) == 1:
                            st.session_state.found_eem_record = resultado.iloc[0].to_dict()
                            st.session_state.search_performed = True  # ✅ Marcar búsqueda exitosa
                            st.session_state.expediente_no_encontrado = False
                            
                        else:
                            st.session_state.multiple_results = resultado
                            st.session_state.search_message = ("info", f"ℹ️ Se encontraron **{len(resultado)}** expedientes coincidentes.")
                            st.session_state.search_performed = True  # ✅ Marcar búsqueda exitosa
                            st.session_state.expediente_no_encontrado = False
                    else:
                        st.session_state.search_message = ("error", f"❌ Expediente no encontrado en la base de datos.")
                        st.session_state.expediente_no_encontrado = True  # ❌ Expediente no encontrado

    # Mostrar mensajes de búsqueda
    if 'search_message' in st.session_state and st.session_state.search_message:
        msg_type, msg_text = st.session_state.search_message
        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "warning":
            st.warning(msg_text)
        elif msg_type == "error":
            st.error(msg_text)
        elif msg_type == "info":
            st.info(msg_text)
        # Limpiar mensaje
        st.session_state.search_message = None

    # 🆕 Mostrar botón limpiar si el expediente no fue encontrado
    if st.session_state.expediente_no_encontrado:
        st.markdown("---")
        col_reset = st.columns([3, 1, 3])[1]
        with col_reset:
            if st.button("🗑️ Nueva Búsqueda", key="btn_limpiar_no_encontrado", use_container_width=True):
                limpiar_busqueda()
                st.session_state.search_performed = False
                st.session_state.expediente_no_encontrado = False
                st.rerun()

    # --- Selección de EEM (múltiples resultados) ---
    if st.session_state.multiple_results is not None and st.session_state.found_eem_record is None:
        st.markdown("---")
        eem_options = ["-- Seleccione un EEM --"] + st.session_state.multiple_results['EEM'].tolist()
        
        selected_eem = st.selectbox(
            "📋 Se encontraron los siguientes EEM. Elija uno para continuar:", 
            options=eem_options, 
            index=0, 
            key="selected_eem_from_multiple"
        )
        
        if selected_eem != "-- Seleccione un EEM --":
            selected_record_df = st.session_state.multiple_results[
                st.session_state.multiple_results['EEM'] == selected_eem
            ]
            if not selected_record_df.empty:
                st.session_state.found_eem_record = selected_record_df.iloc[0].to_dict()
                #st.success(f"✅ Ha seleccionado el expediente **{selected_eem}**.")

    # --- 2. Visualización y Validación ---
    if st.session_state.found_eem_record:
        st.markdown("---")
        st.subheader("📄 2. Información del Expediente")
        
        record = st.session_state.found_eem_record
        
        col_eem, col_estado = st.columns(2)
        col_eem.text_input(
            "EEM Encontrado", 
            value=record.get('EEM', ''), 
            disabled=True, 
            key="tab1_eem_encontrado"
        )
        
        estado = record.get('ESTADO', 'No disponible')
        col_estado.text_input(
            "Estado del Expediente", 
            value=estado, 
            disabled=True, 
            key="tab1_estado_expediente"
        )
        
        # Validar estado y saldo
        saldo_deudor = float(record.get('SALDO DEUDOR', 0.00))
        estados_finalizados = r'(cancelado|anulado|caducidad|nulidad|pérdida)'
        
        if saldo_deudor < 0.1 or re.search(estados_finalizados, str(estado), re.IGNORECASE):
            st.warning(f"⚠️ No se puede calcular la liquidación. **Estado**: '{estado}' | **Saldo Deudor**: S/ {saldo_deudor:,.2f}")
            st.markdown("---")
            col_reset2 = st.columns([3, 1, 3])[1]
            with col_reset2:
                if st.button("🗑️ Nueva Búsqueda", key="btn_limpiar_estado_invalido", use_container_width=True):
                    limpiar_busqueda()
                    st.session_state.search_performed = False
                    st.session_state.expediente_no_encontrado = False
                    st.rerun()
        else:
            st.markdown("---")
            st.subheader("🧮 3. Calcular Liquidación")
            
            # Fecha de liquidación
            fecha_actualizacion = st.date_input(
                "📅 Selecciona la Fecha de Liquidación", 
                value=datetime.now(), 
                min_value=datetime(2000, 1, 1), 
                max_value=datetime(2100, 12, 31), 
                help="La fecha hasta la cual se calcularán los intereses moratorios.",
                key="fecha_liquidacion_input"
            )
            
            # Guardar fecha en session_state
            st.session_state.fecha_liquidacion_seleccionada = fecha_actualizacion
            
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 3])
            
            with btn_col1:
                if st.button("🧮 Calcular", key="btn_calcular", use_container_width=True):
                    with st.spinner("⏳ Calculando liquidación..."):
                        try:
                            df_record = pd.DataFrame([record])
                            df_actualizado = calcular_monto_actualizado(df_record, fecha_actualizacion)
                            st.session_state.calculation_data = df_actualizado.iloc[0].to_dict()
                            st.session_state.show_results = True
                            # ✅ NO bloquear el botón de descarga aquí
                        except Exception as e:
                            st.session_state.calculation_message = f"❌ Error al calcular: {str(e)}"
            
            with btn_col2:
                if st.button("🗑️ Limpiar", key="btn_limpiar_calculo", use_container_width=True):
                    limpiar_busqueda()
                    st.session_state.search_performed = False
                    st.session_state.expediente_no_encontrado = False
                    st.rerun()

    # Mostrar mensajes de cálculo
    if 'calculation_message' in st.session_state and st.session_state.calculation_message:
        if "✅" in st.session_state.calculation_message:
            st.success(st.session_state.calculation_message)
        else:
            st.error(st.session_state.calculation_message)
        st.session_state.calculation_message = None

    # --- 4. Visualización de Resultados y Generación de PDF ---
    if st.session_state.show_results and st.session_state.calculation_data:
        st.markdown("---")
        st.subheader("📊 4. Resultados de la Liquidación")
        
        data = st.session_state.calculation_data
        
        # Métricas
        col_sd, col_dt, col_it, col_sa = st.columns(4)
        
        with col_sd:
            st.metric(
                "💰 Saldo Deudor", 
                f"S/ {float(data.get('SALDO DEUDOR', 0)):,.2f}",
                help="Monto original de la deuda"
            )
        
        with col_dt:
            st.metric(
                "📅 Días Transcurridos", 
                f"{data.get('DIAS_TRANSCURRIDOS', 0)}",
                help="Días desde el consentimiento hasta la fecha de liquidación"
            )
        
        with col_it:
            st.metric(
                "📈 Interés Moratorio", 
                f"S/ {float(data.get('INTERES_MORATORIO', 0)):,.2f}",
                help="Interés calculado por días de mora"
            )
        
        with col_sa:
            st.metric(
                "💵 Saldo Actualizado", 
                f"S/ {float(data.get('MONTO_ACTUALIZADO', 0)):,.2f}",
                delta=f"+ S/ {float(data.get('INTERES_MORATORIO', 0)):,.2f}",
                help="Monto total a pagar (Saldo + Interés)"
            )

        st.markdown("---")
        
        # --- Generación y Descarga de PDF ---
        if 'download_disabled' not in st.session_state:
            st.session_state.download_disabled = False

        def download_action_callback():
            """Callback al descargar el PDF."""
            incrementar_contador()
            st.session_state.download_disabled = True
            st.session_state.download_message = "✅ PDF descargado exitosamente. Contador actualizado."
            st.session_state.trigger_clean_after_download = True

        # Generar número de liquidación
        current_counter_val = get_contador()
        num_liquidacion_para_pdf = generar_numero_liquidacion(current_counter_val)

        # Preparar datos para el PDF
        df_display = pd.DataFrame([{
            'Saldo Deudor': f"S/ {float(data.get('SALDO DEUDOR', 0)):,.2f}",
            'Dias transcurridos': data.get('DIAS_TRANSCURRIDOS', 0),
            'Interes': f"S/ {float(data.get('INTERES_MORATORIO', 0)):,.2f}",
            'Saldo Actualizado': f"S/ {float(data.get('MONTO_ACTUALIZADO', 0)):,.2f}"
        }])

        # Recuperar fecha guardada
        fecha_para_pdf = st.session_state.get('fecha_liquidacion_seleccionada', datetime.now().date())

        # Generar PDF
        try:
            pdf_buffer = generar_pdf_liquidacion(
                df_display=df_display,
                saldo_deudor=f"S/ {float(data.get('SALDO DEUDOR', 0)):,.2f}",
                interes_moratorio=f"S/ {float(data.get('INTERES_MORATORIO', 0)):,.2f}",
                monto_actualizado=f"S/ {float(data.get('MONTO_ACTUALIZADO', 0)):,.2f}",
                num_liquidacion=num_liquidacion_para_pdf,
                fecha_liquidacion=fecha_para_pdf,
                razon_social=st.session_state.found_eem_record.get('OBLIGADO', ''),
                ruc_obligado=st.session_state.found_eem_record.get('RUC', ''),
                expediente_eem=st.session_state.found_eem_record.get('EEM', ''),
                resolucion_subintendencia=st.session_state.found_eem_record.get('RESOL_SUBINTENDENCIA', ''),
                fec_notif_rsi=st.session_state.found_eem_record.get('FEC_NOTI_RSI', ''),
                fecha_consentimiento=st.session_state.found_eem_record.get('FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA', '')
            )

            # Mostrar información del PDF
            col_info, col_download = st.columns([2, 1])
            
            with col_info:
                st.info(f"📄 **Número de Liquidación**: {num_liquidacion_para_pdf}")
                st.caption(f"📅 Fecha de generación: {fecha_para_pdf.strftime('%d/%m/%Y')}")
            
            with col_download:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_buffer,
                    file_name=f"liquidacion_{num_liquidacion_para_pdf.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    on_click=download_action_callback,
                    disabled=st.session_state.download_disabled,
                    use_container_width=True
                )
            
            # Mostrar mensaje de descarga
            if 'download_message' in st.session_state and st.session_state.download_message:
                st.success(st.session_state.download_message)
                st.session_state.download_message = None
                
        except Exception as e:
            st.error(f"❌ Error al generar el PDF: {str(e)}")
            with st.expander("🔍 Ver detalles del error"):
                st.exception(e)