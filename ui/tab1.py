import streamlit as st
import pandas as pd
from datetime import datetime
import re
from utils.calculos import calcular_monto_actualizado, generar_detalle_calculo
from utils.contador import get_contador, generar_numero_liquidacion, incrementar_contador
from services.pdf_generator import generar_pdf_liquidacion
from services.state_manager import limpiar_busqueda

def render_tab1(df_principal):
    """Renderiza la pestaña de cálculo de liquidación - OPTIMIZADA."""
    
    # Verificar limpieza después de descarga
    if st.session_state.get('trigger_clean_after_download', False):
        st.session_state.trigger_clean_after_download = False
        limpiar_busqueda()
    
    # Inicializar estados
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    if 'expediente_no_encontrado' not in st.session_state:
        st.session_state.expediente_no_encontrado = False
    
    # ============================================
    # 1. BÚSQUEDA DEL EXPEDIENTE
    # ============================================
    st.subheader("🔍 Búsqueda por Multa (EEM)")
    
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        
        with col1:
            correlativo = st.text_input(
                "Correlativo del EEM", 
                max_chars=5, 
                key="tab1_correlativo",
                disabled=st.session_state.search_performed,
                placeholder="12345"
            )
        
        with col2:
            anio = st.text_input(
                "Año del EEM", 
                max_chars=4, 
                key="tab1_anio",
                disabled=st.session_state.search_performed,
                placeholder="2024"
            )
        
        with col3:
            intendencia = st.text_input(
                "Intendencia del EEM", 
                max_chars=3, 
                key="tab1_intendencia",
                disabled=st.session_state.search_performed,
                placeholder="LIM"
            )
        
        with col4:
            st.write("")
            st.write("")
            buscar_btn = st.button(
                "🔎 Buscar", 
                key="btn_buscar", 
                use_container_width=True,
                disabled=st.session_state.search_performed,
                type="primary"
            )
    
    # Procesar búsqueda
    if buscar_btn:
        # Validaciones rápidas
        if not (correlativo.strip() and anio.strip() and intendencia.strip()):
            st.warning("⚠️ Complete todos los campos")
        elif not correlativo.isdigit() or len(correlativo) > 5:
            st.warning("⚠️ Correlativo: solo números (máx. 5)")
        elif not anio.isdigit() or len(anio) != 4:
            st.warning("⚠️ Año: 4 dígitos")
        elif len(intendencia) != 3 or not intendencia.isalpha():
            st.warning("⚠️ Intendencia: 3 letras")
        else:
            # Búsqueda optimizada
            with st.spinner("🔍 Buscando..."):
                eem_buscado = f"{correlativo.zfill(5)}{anio}{intendencia.upper()}"
                resultado = df_principal[df_principal["EEM_ABREV"] == eem_buscado]
                
                if not resultado.empty:
                    st.session_state.found_eem_record = resultado.iloc[0].to_dict()
                    st.session_state.search_performed = True
                    st.session_state.expediente_no_encontrado = False
                    st.success("✅ Expediente encontrado")
                else:
                    st.error("❌ Expediente no encontrado")
                    st.session_state.expediente_no_encontrado = True
    
    # Botón nueva búsqueda
    if st.session_state.expediente_no_encontrado:
        st.markdown("---")
        if st.button("🔄 Nueva Búsqueda", use_container_width=True):
            limpiar_busqueda()
            st.rerun()
    
    # ============================================
    # 2. INFORMACIÓN DEL EXPEDIENTE
    # ============================================
    if st.session_state.get('found_eem_record'):
        st.markdown("---")
        st.subheader("📄 Información del Expediente")
        
        record = st.session_state.found_eem_record
        
        # Mostrar info principal
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.text_input("EEM", value=record.get('EEM', ''), disabled=True)
            st.text_input("Obligado", value=record.get('OBLIGADO', ''), disabled=True)
        
        with col_info2:
            st.text_input("Estado", value=record.get('ESTADO', ''), disabled=True)
            st.text_input("RUC", value=record.get('RUC', ''), disabled=True)
        
        # Validar estado
        saldo_deudor = float(record.get('SALDO DEUDOR', 0))
        estado = record.get('ESTADO', '')
        estados_finalizados = r'(cancelado|anulado|caducidad|nulidad|perdida de exigibilidad)'
        
        if saldo_deudor < 0.1 or re.search(estados_finalizados, str(estado), re.IGNORECASE):
            st.warning(f"⚠️ No se puede calcular. Estado: {estado} | Saldo: S/ {saldo_deudor:,.2f}")
            
            if st.button("🔄 Nueva Búsqueda", key="btn_nueva_busqueda_estado"):
                limpiar_busqueda()
                st.rerun()
        else:
            # Mostrar información adicional de pagos si existe
            ultima_fec_pago = record.get('ULTIMA FEC_PAGO', '')
            saldo_inicial = float(record.get('SALDO INICIAL', 0))
            
            if ultima_fec_pago:
                st.info(f"💳 **Último Pago Registrado**: {ultima_fec_pago}")
                col_si, col_sd = st.columns(2)
                with col_si:
                    st.metric("Saldo Inicial", f"S/ {saldo_inicial:,.2f}")
                with col_sd:
                    st.metric("Saldo Deudor (Actual)", f"S/ {saldo_deudor:,.2f}")
                st.caption("💡 El cálculo se realizará desde el día siguiente al último pago")
            else:
                st.info("ℹ️ No hay pagos registrados. Se usará el saldo inicial")
                st.metric("Saldo Inicial", f"S/ {saldo_inicial:,.2f}")
            
            st.markdown("---")
            
            # ============================================
            # 3. CALCULAR LIQUIDACIÓN
            # ============================================
            st.subheader("🧮 Calcular Liquidación")
            
            col_fecha, col_btns = st.columns([2, 2])
            
            with col_fecha:
                fecha_liquidacion = st.date_input(
                    "📅 Fecha de Liquidación", 
                    value=datetime.now(),
                    min_value=datetime(2000, 1, 1),
                    max_value=datetime(2100, 12, 31),
                    key="fecha_liq"
                )
                st.session_state.fecha_liquidacion_seleccionada = fecha_liquidacion
            
            with col_btns:
                st.write("")
                st.write("")
                col_calc, col_clean = st.columns(2)
                
                with col_calc:
                    if st.button("🧮 Calcular", key="btn_calc", use_container_width=True, type="primary"):
                        with st.spinner("⏳ Calculando..."):
                            try:
                                df_record = pd.DataFrame([record])
                                df_actualizado = calcular_monto_actualizado(df_record, fecha_liquidacion)
                                st.session_state.calculation_data = df_actualizado.iloc[0].to_dict()
                                st.session_state.show_results = True
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                
                with col_clean:
                    if st.button("🗑️ Limpiar", key="btn_clean", use_container_width=True):
                        limpiar_busqueda()
                        st.rerun()
    
    # ============================================
    # 4. RESULTADOS
    # ============================================
    if st.session_state.get('show_results') and st.session_state.get('calculation_data'):
        st.markdown("---")
        st.subheader("📊 Resultados")
        
        data = st.session_state.calculation_data
        
        # Información del cálculo
        if data.get('HAY_PAGO_PREVIO', False):
            st.success(f"✅ Cálculo desde: **{data.get('FECHA_INICIO_CALCULO')}** (día siguiente al último pago)")
            
        
        # Métricas principales
        col_cap, col_dias, col_int, col_tot = st.columns(4)
        
        with col_cap:
            st.metric(
                "💰 Capital", 
                f"S/ {data.get('CAPITAL_PARA_CALCULO', 0):,.2f}",
                help="Capital sobre el cual se calcula el interés"
            )
        
        with col_dias:
            st.metric(
                "📅 Días", 
                f"{data.get('DIAS_CALCULADOS', 0):,}",
                help="Días calculados para el interés"
            )
        
        with col_int:
            st.metric(
                "📈 Interés", 
                f"S/ {data.get('INTERES_MORATORIO', 0):,.2f}",
                help="Interés moratorio calculado"
            )
        
        with col_tot:
            st.metric(
                "💵 Total", 
                f"S/ {data.get('MONTO_ACTUALIZADO', 0):,.2f}",
                delta=f"+ S/ {data.get('INTERES_MORATORIO', 0):,.2f}",
                help="Monto total a pagar"
            )
        
        st.markdown("---")
        
        # ============================================
        # 5. GENERAR PDF
        # ============================================
        if 'download_disabled' not in st.session_state:
            st.session_state.download_disabled = False
        
        def download_callback():
            incrementar_contador()
            st.session_state.download_disabled = True
            st.session_state.download_message = "✅ PDF generado"
            st.session_state.trigger_clean_after_download = True
        
        # Generar número de liquidación
        contador = get_contador()
        num_liquidacion = generar_numero_liquidacion(contador)
        
        # Preparar datos para PDF
        df_display = pd.DataFrame([{
            'Saldo Deudor': f"S/ {data.get('CAPITAL_PARA_CALCULO', 0):,.2f}",
            'Dias transcurridos': data.get('DIAS_CALCULADOS', 0),
            'Interes': f"S/ {data.get('INTERES_MORATORIO', 0):,.2f}",
            'Saldo Actualizado': f"S/ {data.get('MONTO_ACTUALIZADO', 0):,.2f}"
        }])
        
        fecha_para_pdf = st.session_state.get('fecha_liquidacion_seleccionada', datetime.now().date())
        
        try:
            pdf_buffer = generar_pdf_liquidacion(
                df_display=df_display,
                saldo_deudor=f"S/ {data.get('CAPITAL_PARA_CALCULO', 0):,.2f}",
                interes_moratorio=f"S/ {data.get('INTERES_MORATORIO', 0):,.2f}",
                monto_actualizado=f"S/ {data.get('MONTO_ACTUALIZADO', 0):,.2f}",
                num_liquidacion=num_liquidacion,
                fecha_liquidacion=fecha_para_pdf,
                razon_social=st.session_state.found_eem_record.get('OBLIGADO', ''),
                ruc_obligado=st.session_state.found_eem_record.get('RUC', ''),
                expediente_eem=st.session_state.found_eem_record.get('EEM', ''),
                resolucion_subintendencia=st.session_state.found_eem_record.get('RESOL_SUBINTENDENCIA', ''),
                fec_notif_rsi=st.session_state.found_eem_record.get('FEC_NOTI_RSI', ''),
                fecha_consentimiento=st.session_state.found_eem_record.get('FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA', '')
            )
            
            col_pdf_info, col_pdf_btn = st.columns([2, 1])
            
            with col_pdf_info:
                st.info(f"📄 **N° Liquidación**: {num_liquidacion}")
                st.caption(f"📅 Generado: {fecha_para_pdf.strftime('%d/%m/%Y')}")
            
            with col_pdf_btn:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_buffer,
                    file_name=f"liquidacion_{num_liquidacion.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    on_click=download_callback,
                    disabled=st.session_state.download_disabled,
                    use_container_width=True,
                    type="primary"
                )
            
            if st.session_state.get('download_message'):
                st.success(st.session_state.download_message)
                st.session_state.download_message = None
        
        except Exception as e:
            st.error(f"❌ Error al generar PDF: {str(e)}")