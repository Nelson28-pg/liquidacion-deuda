import streamlit as st
import pandas as pd
import os
import ijson
import json
from decimal import Decimal
import re # Importar el módulo re

@st.cache_data
def load_json_as_df(path):
    try:
        with open(path, 'rb') as f:
            records = ijson.items(f, 'item')
            df = pd.DataFrame(records)
        
        df.columns = [col.strip().upper() for col in df.columns]

        for col in ['EEM', 'RUC']:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        if 'EEM_ABREV' in df.columns:
            def normalize_eem_abrev(eem_abrev_str):
                # Intentar extraer las partes usando una expresión regular
                # Asume que EEM_ABREV es una concatenación de números (correlativo), 4 números (año) y letras (intendencia)
                match = re.match(r'(\d{1,5})(\d{4})([A-Za-z]{3})', str(eem_abrev_str))
                if match:
                    correlativo = match.group(1).zfill(5)
                    anio = match.group(2)
                    intendencia = match.group(3).upper()
                    return f"{correlativo}{anio}{intendencia}"
                return str(eem_abrev_str) # Si no coincide, devolver el original como string

            df['EEM_ABREV'] = df['EEM_ABREV'].astype(str).apply(normalize_eem_abrev)
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo JSON en la ruta: {path}")
        return None
    except Exception as e:
        st.error(f"Error al leer o procesar el archivo JSON: {e}")
        return None

def safe_load_json(ruta_json):
    """Carga JSON evitando errores si está vacío o corrupto."""
    if not os.path.exists(ruta_json) or os.path.getsize(ruta_json) == 0:
        return []
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError (f"Type {type(obj)} not serializable")

def save_record_to_json(record, path):
    """Lee un archivo JSON, añade un nuevo registro y lo guarda."""
    data = safe_load_json(path)
    data.append(record)
    
    with open(path, 'w', encoding='utf-8') as f:
        # Using json_serial to handle Decimals that might come from number_input
        json.dump(data, f, indent=4, ensure_ascii=False, default=json_serial)
