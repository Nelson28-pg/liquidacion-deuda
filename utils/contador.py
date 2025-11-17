import os
from datetime import datetime

# La ruta del archivo del contador estará en el directorio raíz del proyecto
CONTADOR_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'contador.txt'))

def get_contador():
    """Lee el valor actual del contador desde el archivo."""
    if not os.path.exists(CONTADOR_FILE):
        with open(CONTADOR_FILE, 'w', encoding='utf-8') as f:
            f.write('1')
        return 1
    else:
        with open(CONTADOR_FILE, 'r', encoding='utf-8') as f:
            try:
                content = f.read().strip()
                if not content: # Si el archivo está vacío
                    with open(CONTADOR_FILE, 'w', encoding='utf-8') as f_fix:
                        f_fix.write('0')
                    return 0
                return int(content)
            except (ValueError, TypeError):
                # Si el archivo está corrupto, empezar de 1 y arreglarlo
                with open(CONTADOR_FILE, 'w', encoding='utf-8') as f_fix:
                    f_fix.write('0')
                return 0

def incrementar_contador():
    """Incrementa el contador y guarda el nuevo valor. Devuelve el nuevo valor."""
    valor = get_contador() + 1
    with open(CONTADOR_FILE, 'w', encoding='utf-8') as f:
        f.write(str(valor))
    return valor

def set_contador(nuevo_valor):
    """Establece un nuevo valor para el contador (solo para admin)."""
    try:
        nuevo_valor = int(nuevo_valor)
        if nuevo_valor > 0:
            with open(CONTADOR_FILE, 'w', encoding='utf-8') as f:
                f.write(str(nuevo_valor))
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False

def generar_numero_liquidacion(valor_contador=None):
    """
    Genera el número de liquidación formateado.
    Usa el valor_contador proporcionado o el actual si es None.
    """
    if valor_contador is None:
        valor_contador = get_contador()
    
    anio_actual = datetime.now().year
    # Formato: 002-00001-2025-SUNAFIL/GG/OAD/UCEC
    return f"002-{valor_contador:05d}-{anio_actual}-SUNAFIL/GG/OAD/UCEC"
