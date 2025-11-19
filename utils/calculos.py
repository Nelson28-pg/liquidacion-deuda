from datetime import date, timedelta
import pandas as pd
import locale

def calcular_interes(f_inicio, f_act, saldo):
    """
    Calcula el interés moratorio según tramos SUNAT
    
    Args:
        f_inicio: Fecha de inicio del cálculo
        f_act: Fecha de actualización
        saldo: Saldo deudor
    
    Returns:
        float: Interés moratorio calculado
    """
    saldo = float(saldo)
    
    # Validar fechas
    if f_inicio is None or f_act is None:
        return 0.0
    
    if f_inicio >= f_act:
        return 0.0
    
    tramos = [
        {"desde": date(2010, 3, 1), "hasta": date(2020, 3, 31), "tasa": 0.0004},
        {"desde": date(2020, 4, 1), "hasta": date(2021, 3, 31), "tasa": 0.00033},
        {"desde": date(2021, 4, 1), "hasta": date(2099, 12, 31), "tasa": 0.00030},
    ]
    
    interes_total = 0
    
    for tramo in tramos:
        # Calcular la intersección del período con el tramo
        inicio = max(f_inicio, tramo["desde"])
        fin = min(f_act, tramo["hasta"])
        
        if inicio <= fin:
            dias = (fin - inicio).days
            interes_tramo = saldo * tramo["tasa"] * dias
            interes_total += interes_tramo
    
    return round(interes_total, 2)


def parse_date_robustly(date_str):
    """Parsea fechas en múltiples formatos"""
    if pd.isna(date_str) or date_str is None or date_str == '':
        return None
    
    if isinstance(date_str, date):
        return date_str
    
    # Formato "DD de MMMM de YYYY"
    try:
        return pd.to_datetime(date_str, format="%d de %B de %Y", errors='raise').date()
    except (ValueError, TypeError):
        pass
    
    # Formato "D/M/YYYY" o "DD/MM/YYYY"
    try:
        return pd.to_datetime(date_str, format="%d/%m/%Y", errors='raise').date()
    except (ValueError, TypeError):
        pass
    
    # Dejar que pandas infiera
    try:
        parsed = pd.to_datetime(date_str, errors='raise')
        return parsed.date() if hasattr(parsed, 'date') else parsed
    except (ValueError, TypeError):
        return None


def calcular_monto_actualizado(df, fecha_actualizacion, debug=False):
    """
    Calcula el monto actualizado considerando:
    - Si existe ULTIMA FEC_PAGO: usa SALDO DEUDOR desde día siguiente al pago
    - Si NO existe ULTIMA FEC_PAGO: usa SALDO INICIAL desde fecha de consentimiento
    
    Args:
        df: DataFrame con los expedientes
        fecha_actualizacion: Fecha hasta la cual calcular
        debug: Si True, imprime información de depuración
    
    Returns:
        DataFrame: DataFrame con columnas calculadas
    """
    
    # Convertir fecha_actualizacion
    if isinstance(fecha_actualizacion, str):
        fecha_actualizacion = pd.to_datetime(fecha_actualizacion).date()
    elif isinstance(fecha_actualizacion, pd.Timestamp):
        fecha_actualizacion = fecha_actualizacion.date()
    
    # Establecer locale español
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
            except locale.Error:
                pass
    
    df = df.copy()
    
    # Convertir fecha de consentimiento
    df["FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA"] = df[
        "FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA"
    ].apply(parse_date_robustly)
    
    # Función para calcular cada fila
    def calcular_fila(row):
        eem = row.get('EEM', 'N/A')
        fecha_consentimiento = row["FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA"]
        
        # Obtener SALDO INICIAL y SALDO DEUDOR
        saldo_inicial = float(row.get('SALDO INICIAL', row.get('SALDO DEUDOR', 0)))
        saldo_deudor = float(row.get('SALDO DEUDOR', 0))
        
        # Verificar si existe ULTIMA FEC_PAGO
        ultima_fec_pago_str = row.get('ULTIMA FEC_PAGO', '')
        ultima_fec_pago = parse_date_robustly(ultima_fec_pago_str)
        
        # ============================================
        # LÓGICA PRINCIPAL
        # ============================================
        if ultima_fec_pago is not None and ultima_fec_pago != '':
            # ✅ HAY ÚLTIMO PAGO: usar SALDO DEUDOR desde día siguiente
            fecha_inicio_calculo = ultima_fec_pago + timedelta(days=1)
            capital_para_calculo = saldo_deudor
            hay_pago_previo = True
            amortizacion_previa = saldo_inicial - saldo_deudor
            
            if debug:
                print(f"\n{'='*60}")
                print(f"🔍 EEM: {eem}")
                print(f"✅ CON PAGO PREVIO")
                print(f"📅 Último pago: {ultima_fec_pago}")
                print(f"📅 Fecha inicio cálculo: {fecha_inicio_calculo}")
                print(f"💰 Capital para cálculo: S/ {capital_para_calculo:,.2f}")
                print(f"💸 Amortización previa: S/ {amortizacion_previa:,.2f}")
        else:
            # ✅ NO HAY PAGO: usar SALDO INICIAL desde fecha de consentimiento
            fecha_inicio_calculo = fecha_consentimiento
            capital_para_calculo = saldo_inicial
            hay_pago_previo = False
            amortizacion_previa = 0.0
            
            if debug:
                print(f"\n{'='*60}")
                print(f"🔍 EEM: {eem}")
                print(f"⭕ SIN PAGOS PREVIOS")
                print(f"📅 Fecha consentimiento: {fecha_consentimiento}")
                print(f"📅 Fecha inicio cálculo: {fecha_inicio_calculo}")
                print(f"💰 Capital para cálculo: S/ {capital_para_calculo:,.2f}")
        
        # Validar fechas
        if fecha_inicio_calculo is None or fecha_consentimiento is None:
            return pd.Series({
                'DIAS_TRANSCURRIDOS': 0,
                'DIAS_CALCULADOS': 0,
                'FECHA_INICIO_CALCULO': None,
                'CAPITAL_PARA_CALCULO': capital_para_calculo,
                'INTERES_MORATORIO': 0.0,
                'MONTO_ACTUALIZADO': capital_para_calculo,
                'SALDO_INICIAL': saldo_inicial,
                'SALDO_DEUDOR': saldo_deudor,
                'HAY_PAGO_PREVIO': hay_pago_previo,
                'AMORTIZACION_PREVIA': amortizacion_previa,
                'ULTIMO_PAGO_FECHA': ultima_fec_pago
            })
        
        # Validar que fecha de inicio sea anterior a la de actualización
        if fecha_inicio_calculo > fecha_actualizacion:
            dias_calculados = 0
            interes_moratorio = 0.0
        else:
            # ✅ Calcular días transcurridos DESDE fecha_inicio_calculo
            dias_calculados = (fecha_actualizacion - fecha_inicio_calculo).days
            dias_calculados = max(0, dias_calculados)
            
            # ✅ Calcular interés DESDE fecha_inicio_calculo
            if capital_para_calculo > 0 and dias_calculados > 0:
                interes_moratorio = calcular_interes(
                    fecha_inicio_calculo,  # ✅ Usa la fecha correcta
                    fecha_actualizacion,
                    capital_para_calculo
                )
                
                if debug:
                    print(f"📊 Días calculados: {dias_calculados}")
                    print(f"📈 Interés moratorio: S/ {interes_moratorio:,.2f}")
                    
                    # Verificación manual
                    interes_manual = capital_para_calculo * 0.00030 * dias_calculados
                    print(f"🧮 Verificación (manual): S/ {interes_manual:,.2f}")
                    print(f"✅ ¿Coincide?: {'SÍ' if abs(interes_manual - interes_moratorio) < 0.01 else 'NO'}")
            else:
                interes_moratorio = 0.0
        
        # Calcular días totales desde consentimiento (para referencia)
        dias_totales = (fecha_actualizacion - fecha_consentimiento).days if fecha_consentimiento else 0
        dias_totales = max(0, dias_totales)
        
        # Calcular monto total
        monto_actualizado = round(capital_para_calculo + interes_moratorio, 2)
        
        if debug:
            print(f"💵 Monto actualizado: S/ {monto_actualizado:,.2f}")
            print(f"{'='*60}\n")
        
        return pd.Series({
            'DIAS_TRANSCURRIDOS': dias_totales,  # Días totales desde consentimiento
            'DIAS_CALCULADOS': dias_calculados,  # Días usados en el cálculo
            'FECHA_INICIO_CALCULO': fecha_inicio_calculo,
            'CAPITAL_PARA_CALCULO': round(capital_para_calculo, 2),
            'INTERES_MORATORIO': interes_moratorio,
            'MONTO_ACTUALIZADO': monto_actualizado,
            'SALDO_INICIAL': round(saldo_inicial, 2),
            'SALDO_DEUDOR': round(saldo_deudor, 2),
            'HAY_PAGO_PREVIO': hay_pago_previo,
            'AMORTIZACION_PREVIA': round(amortizacion_previa, 2),
            'ULTIMO_PAGO_FECHA': ultima_fec_pago
        })
    
    # Aplicar cálculo a cada fila
    resultados = df.apply(calcular_fila, axis=1)
    
    # Agregar columnas calculadas
    df = pd.concat([df, resultados], axis=1)
    
    return df


def generar_detalle_calculo(row, fecha_actualizacion):
    """
    Genera un detalle del cálculo realizado
    
    Returns:
        dict: Información detallada del cálculo
    """
    
    return {
        'expediente': row.get('EEM', 'N/A'),
        'fecha_consentimiento': row.get('FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA', 'N/A'),
        'ultimo_pago_fecha': row.get('ULTIMO_PAGO_FECHA', None),
        'fecha_inicio_calculo': row.get('FECHA_INICIO_CALCULO', 'N/A'),
        'fecha_liquidacion': fecha_actualizacion,
        'saldo_inicial': row.get('SALDO_INICIAL', 0),
        'saldo_deudor': row.get('SALDO_DEUDOR', 0),
        'capital_usado': row.get('CAPITAL_PARA_CALCULO', 0),
        'hay_pago_previo': row.get('HAY_PAGO_PREVIO', False),
        'amortizacion_previa': row.get('AMORTIZACION_PREVIA', 0),
        'dias_calculados': row.get('DIAS_CALCULADOS', 0),
        'interes_moratorio': row.get('INTERES_MORATORIO', 0),
        'monto_total': row.get('MONTO_ACTUALIZADO', 0)
    }


def verificar_calculo_interes(fecha_inicio, fecha_fin, capital, interes_calculado):
    """
    Verifica si el interés calculado es correcto
    
    Returns:
        dict: Resultado de la verificación
    """
    if fecha_inicio is None or fecha_fin is None:
        return {
            'correcto': False,
            'mensaje': 'Fechas inválidas'
        }
    
    if fecha_inicio >= fecha_fin:
        return {
            'correcto': True,
            'mensaje': 'Sin días para calcular'
        }
    
    dias = (fecha_fin - fecha_inicio).days
    interes_esperado = capital * 0.00030 * dias
    diferencia = abs(interes_calculado - interes_esperado)
    
    return {
        'correcto': diferencia < 0.01,
        'dias': dias,
        'interes_esperado': round(interes_esperado, 2),
        'interes_calculado': interes_calculado,
        'diferencia': round(diferencia, 2),
        'mensaje': 'Cálculo correcto' if diferencia < 0.01 else f'Diferencia de S/ {diferencia:.2f}'
    }