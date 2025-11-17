import ijson
import json

file_path = 'c:\\Users\\pisci\\Desktop\\practica_agente-gemini\\liquidacion_deuda\\data\\base_ucec.json'

try:
    with open(file_path, 'rb') as f:
        parser = ijson.parse(f)
        keys = set()
        for prefix, event, value in parser:
            if event == 'map_key':
                keys.add(value)
        print(json.dumps(list(keys), indent=2))
except FileNotFoundError:
    print(f"Error: No se encontró el archivo JSON en la ruta: {file_path}")
except Exception as e:
    print(f"Error al leer o procesar el archivo JSON: {e}")
