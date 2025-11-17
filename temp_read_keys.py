import ijson
import json
import os

def get_json_keys(file_path):
    keys = set()
    try:
        with open(file_path, 'rb') as f:
            parser = ijson.parse(f)
            for prefix, event, value in parser:
                if event == 'map_key':
                    keys.add(value)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo JSON en la ruta: {file_path}")
    except Exception as e:
        print(f"Error al leer o procesar el archivo JSON: {e}")
    return sorted(list(keys))

if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'base_ucec.json')
    all_keys = get_json_keys(file_path)
    print(json.dumps(all_keys, indent=2))
