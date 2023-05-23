import os


# Guardar datos del formulario en un diccionario dentro de un archivo Python

def creardict(*args):
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{BASE_DIR}\Simulacion\dic\dict.py'
    
    with open(file, 'w', encoding="utf-8") as f:
        f.write(str(*args))


