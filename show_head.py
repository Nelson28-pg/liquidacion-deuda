import pandas as pd
import os

# Construir la ruta al archivo CSV (que está en el directorio superior)
ruta_csv_absoluta = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base_ucec_31102025.csv')

columnas_deseadas = ['EEM', 'OBLIGADO', 'RUC', 'RESOL_SUBINTENDENCIA', 'FEC_NOTI_RSI', 'RESOL_INTENDENCIA', 'FEC_NOTI_RI', 
                     'SALDO DEUDOR']

try:
    df = pd.read_csv(ruta_csv_absoluta, sep=';', nrows=7)
    df_filtrado = df[columnas_deseadas]
    json_data = df_filtrado.to_json(orient='records', indent=4)
    print(json_data)
except Exception as e:
    print(e)