from datetime import date
import pandas as pd
import locale

def calcular_interes(f_inicio, f_act, saldo):
    """Calcula el interés moratorio según tramos SUNAT"""
    saldo = float(saldo) # Convertir saldo a float para evitar TypeError con decimal.Decimal
    tramos = [
        {"desde": date(2010,3,1), "hasta": date(2020,3,31), "tasa": 0.0004},
        {"desde": date(2020,4,1), "hasta": date(2021,3,31), "tasa": 0.00033},
        {"desde": date(2021,4,1), "hasta": date(2099,12,31), "tasa": 0.00030},
    ]
    interes_total = 0
    for tramo in tramos:
        inicio = max(f_inicio, tramo["desde"])
        fin = min(f_act, tramo["hasta"])
        if inicio <= fin:
            dias = (fin - inicio).days 
            interes_total += saldo * tramo["tasa"] * dias
    return round(interes_total, 2)

# Helper function for robust date parsing
def parse_date_robustly(date_str):
    if pd.isna(date_str) or date_str is None:
        return date(1900, 1, 1)

    # Try "DD de MMMM de YYYY" format (e.g., "04 de diciembre de 2024")
    try:
        return pd.to_datetime(date_str, format="%d de %B de %Y", errors='raise').date()
    except (ValueError, TypeError):
        pass # Fall through to next format

    # Try "D/M/YYYY" or "DD/MM/YYYY" format (e.g., "4/12/2024" or "25/07/2014")
    try:
        return pd.to_datetime(date_str, format="%d/%m/%Y", errors='raise').date()
    except (ValueError, TypeError):
        pass # Fall through to next format

    # Let pandas infer (as a fallback for other formats)
    try:
        return pd.to_datetime(date_str, errors='raise').date()
    except (ValueError, TypeError):
        return date(1900, 1, 1) # Default if all parsing fails

def calcular_monto_actualizado(df, fecha_actualizacion):

    # Convertir fecha_actualizacion si llega en string
    fecha_actualizacion = pd.to_datetime(fecha_actualizacion).date()

    # Intentar establecer el locale a español para el parseo de fechas
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252') # Para Windows
            except locale.Error:
                print("Advertencia: No se pudo establecer el locale a español para el parseo de fechas.")

    # Convertir columnas del DF usando la función robusta
    df["FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA"] = df["FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA"].apply(parse_date_robustly)

    # Cálculo de días transcurridos
    df["DIAS_TRANSCURRIDOS"] = df["FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA"].apply(
        lambda x: (fecha_actualizacion - x).days if pd.notna(x) else 0
    )

    # Cálculo de interés
    df["INTERES_MORATORIO"] = df.apply(
        lambda row: calcular_interes(
            row["FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA"],
            fecha_actualizacion,
            row["SALDO DEUDOR"]
        ),
        axis=1
    )

    df["MONTO_ACTUALIZADO"] = (
        df["SALDO DEUDOR"].fillna(0).astype(float) + df["INTERES_MORATORIO"]
    ).round(2)

    return df