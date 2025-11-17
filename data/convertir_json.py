import pandas as pd
from pandas.errors import ParserError
import json
import os

def csv_columnas_a_json_pandas(ruta_csv, columnas_a_incluir, ruta_json_salida):
    """
    Convierte un CSV a JSON, incluyendo solo las columnas especificadas.
    
    :param ruta_csv: La ruta completa al archivo CSV de entrada.
    :param columnas_a_incluir: Una lista de strings con los nombres exactos de las columnas a mantener.
    :param ruta_json_salida: La ruta completa para guardar el archivo JSON de salida.
    """
    try:
        # 1. Lectura del CSV: Pandas lee el archivo completo en un DataFrame.
        #    Se especifica el separador como ';' que es común en archivos CSV en español.
        df = pd.read_csv(ruta_csv, sep=';')
        
        # Limpiar espacios en blanco de los nombres de las columnas para evitar KeyErrors
        df.columns = df.columns.str.strip()
        
        # 2. Selección de Columnas: Se crea un nuevo DataFrame solo con las columnas deseadas.
        #    Esto asegura que el código es robusto, incluso si cambias el orden de las columnas.
        df_filtrado = df[columnas_a_incluir]
        
        # 3. Conversión a JSON: Se convierte el DataFrame filtrado directamente a una string JSON
        #    con el formato 'records' (lista de objetos JSON).
        json_data = df_filtrado.to_json(orient='records', indent=4)
        
        # 4. Guardar el archivo JSON.
        with open(ruta_json_salida, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        print(f"Conversión exitosa. Datos guardados en: {ruta_json_salida}")
        
    except FileNotFoundError:
        print(f"Error: El archivo CSV no se encuentra en {ruta_csv}")
    except KeyError as e:
        print(f"Error: Una o más columnas no se encontraron en el CSV: {e}")
    except ParserError as e:
        print(f"Error al procesar el archivo CSV. Puede que el delimitador no sea el correcto o que el archivo esté malformado: {e}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


# Obtener la ruta del directorio donde se encuentra el script
# Esto hace que el script se pueda ejecutar desde cualquier lugar.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta al archivo CSV (que está en el directorio superior)
ruta_csv_absoluta = os.path.join(script_dir, '..', 'base_ucec_31102025.csv')

# Construir la ruta para el archivo JSON de salida (en el mismo directorio que el script)
ruta_json_absoluta = os.path.join(script_dir, 'base_ucec.json')


columnas_deseadas = ['EEM', 'EEM_ABREV', 'OBLIGADO', 'RUC', 'RESOL_SUBINTENDENCIA', 'FEC_NOTI_RSI', 'RESOL_INTENDENCIA', 'FEC_NOTI_RI', 
                     'FECHA EN LA CUAL QUEDA CONSENTIDA LA MULTA', 'SALDO DEUDOR', 'ESTADO']

csv_columnas_a_json_pandas(ruta_csv=ruta_csv_absoluta, columnas_a_incluir=columnas_deseadas, ruta_json_salida=ruta_json_absoluta)