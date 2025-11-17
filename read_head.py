import os

file_path = os.path.join('data', 'base_ucec.json')

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        for i in range(7):
            line = f.readline()
            if not line:
                break
            print(line, end='')
except FileNotFoundError:
    print(f"Error: El archivo no se encuentra en {file_path}")
except Exception as e:
    print(f"Ocurrió un error: {e}")
