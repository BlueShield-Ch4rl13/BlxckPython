"""
urllib3CredencialPOST.py - Petición HTTP POST con credenciales (Python 3)
=========================================================================
Envía un formulario de login mediante POST usando la biblioteca estándar
de Python 3. Los datos del formulario se codifican con urllib.parse.urlencode
y se convierten a bytes antes de pasarlos a la Request.

ERRORES CORREGIDOS:
    1. URL personal eliminada → reemplazada por dominio de ejemplo.
    2. Credenciales reales eliminadas → marcadores de posición.

REQUISITOS:
    - Python 3.x (solo biblioteca estándar)

EJEMPLOS DE EJECUCIÓN:
    python urllib3CredencialPOST.py

    # Cambiar variables para apuntar a tu lab:
    #   URL  = 'http://tu-servidor-lab/login'
    #   info = {'user': 'tu_usuario', 'passwd': 'tu_contraseña'}
"""

import urllib.parse
import urllib.request

# -------------------------------------------------------------------
# URL de destino — cambiar por la URL de tu lab
# -------------------------------------------------------------------
URL = 'https://httpbin.org/post'   # FIX: URL personal eliminada

# Credenciales de ejemplo — cambiar por las reales de tu entorno de lab
info = {
    'user':   'usuario_lab',       # FIX: credencial real eliminada
    'passwd': 'contraseña_lab',    # FIX: credencial real eliminada
}

# Codificar el diccionario como query-string y convertir a bytes (requerido por POST)
data = urllib.parse.urlencode(info).encode()

# Crear la petición POST (urllib.request.Request con `data` activa el método POST)
req = urllib.request.Request(URL, data)

with urllib.request.urlopen(req) as response:
    content = response.read()

print(content.decode('utf-8'))
