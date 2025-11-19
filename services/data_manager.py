import streamlit as st
import pandas as pd
import os
import ijson
import json
import shutil # Necesario para crear copias de seguridad
from datetime import datetime # Necesario para generar la marca de tiempo del backup
from decimal import Decimal
import re 

# --- Utilitarios de Carga y Serialización ---

@st.cache_data
def load_json_as_df(path):
    """
    Carga datos JSON de manera eficiente (ijson), los normaliza y los devuelve como un DataFrame.
    """
    try:
        with open(path, 'rb') as f:
            records = ijson.items(f, 'item')
            df = pd.DataFrame(records)
        
        # Normalizar nombres de columnas
        df.columns = [col.strip().upper() for col in df.columns]

        # Asegurar tipo string para columnas clave
        for col in ['EEM', 'RUC']:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # Normalizar EEM_ABREV si existe
        if 'EEM_ABREV' in df.columns:
            def normalize_eem_abrev(eem_abrev_str):
                # Asume que EEM_ABREV es una concatenación de números (correlativo), 4 números (año) y letras (intendencia)
                match = re.match(r'(\d{1,5})(\d{4})([A-Za-z]{3})', str(eem_abrev_str))
                if match:
                    correlativo = match.group(1).zfill(5)
                    anio = match.group(2)
                    intendencia = match.group(3).upper()
                    return f"{correlativo}{anio}{intendencia}"
                return str(eem_abrev_str) 

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

# --- Funciones de Lectura y Escritura Transaccional ---

def get_expediente_by_eem_abrev(ruta_json, eem_abrev):
    """
    Obtiene un expediente específico por su EEM_ABREV.
    """
    try:
        # Usar safe_load_json para cargar los datos
        data = safe_load_json(ruta_json)
        
        # Normalizar la clave de búsqueda
        eem_abrev_upper = eem_abrev.upper()
        
        for registro in data:
            if registro.get('EEM_ABREV') == eem_abrev_upper:
                return registro
        
        return None
    
    except Exception as e:
        print(f"❌ Error al obtener expediente: {e}")
        return None


def update_expediente_in_json(ruta_json, eem_abrev, cambios, estado_anterior=None, saldo_anterior=None):
    """
    Actualiza los datos de un expediente en el JSON, y crea un backup.
    """
    try:
        # Cargar JSON actual
        data = safe_load_json(ruta_json)
        eem_abrev_upper = eem_abrev.upper()
        
        # Buscar el expediente
        expediente_encontrado = False
        
        for registro in data:
            if registro.get('EEM_ABREV') == eem_abrev_upper:
                expediente_encontrado = True
                
                # Actualizar campos
                for campo, valor in cambios.items():
                    registro[campo] = valor
                
                break
        
        if not expediente_encontrado:
            return {
                "success": False,
                "message": f"Expediente {eem_abrev} no encontrado en el JSON"
            }
        
        # 1. Crear backup (ANTES de guardar los cambios)
        if os.path.exists(ruta_json):
            backup_dir = os.path.join(os.path.dirname(ruta_json), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f'base_ucec_backup_{timestamp}.json')
            shutil.copy2(ruta_json, backup_path)
        
        # 2. Guardar JSON actualizado
        with open(ruta_json, 'w', encoding='utf-8') as f:
            # Usar json_serial para manejar Decimals (o cualquier tipo no serializable por defecto)
            json.dump(data, f, ensure_ascii=False, indent=4, default=json_serial)
        
        # 3. Preparar mensaje de éxito
        mensaje = f"Expediente {eem_abrev} actualizado correctamente"
        
        if estado_anterior:
            mensaje += f". Estado: **{estado_anterior}** → **{cambios.get('ESTADO', estado_anterior)}**"
        
        if saldo_anterior is not None:
            # Usar format para números con separador de miles
            mensaje += f". Saldo: S/ **{saldo_anterior:,.2f}** → S/ **{cambios.get('SALDO INICIAL', saldo_anterior):,.2f}**"
        
        return {
            "success": True,
            "message": mensaje
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error al actualizar expediente: {str(e)}"
        }


def save_record_to_json(new_record, ruta_json):
    """
    Guarda un nuevo registro en el archivo JSON.
    """
    try:
        data = safe_load_json(ruta_json)
        
        # Verificar si el EEM_ABREV ya existe
        eem_abrev = new_record.get('EEM_ABREV', '').upper()
        
        for registro in data:
            if registro.get('EEM_ABREV') == eem_abrev:
                return {
                    "success": False,
                    "message": f"El expediente {eem_abrev} ya existe en la base de datos"
                }
        
        # Agregar el nuevo registro
        new_record['EEM_ABREV'] = eem_abrev # Asegurar que esté en mayúsculas
        data.append(new_record)
        
        # Crear backup
        if os.path.exists(ruta_json):
            backup_dir = os.path.join(os.path.dirname(ruta_json), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f'base_ucec_backup_{timestamp}.json')
            shutil.copy2(ruta_json, backup_path)
        
        # Guardar JSON actualizado
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=json_serial)
        
        return {
            "success": True,
            "message": f"Expediente **{new_record.get('EEM', '')}** agregado exitosamente"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error al guardar registro: {str(e)}"
        }