"""
urllib2GET.py - Petición HTTP GET con urllib (Python 3)
=======================================================
Recupera el contenido de una URL usando solo la biblioteca estándar
de Python 3 (urllib.request). El nombre del archivo referencia urllib2,
el módulo equivalente de Python 2, que se fusionó en urllib en Python 3.

ERRORES CORREGIDOS:
    1. `import urllib2` → módulo de Python 2. En Python 3 se usa
       `import urllib.request` y `urllib.request.urlopen(url)`.
    2. URL personal reemplazada por dominio de ejemplo.

REQUISITOS:
    - Python 3.x (solo biblioteca estándar)

EJEMPLOS DE EJECUCIÓN:
    python urllib2GET.py

    # Con URL personalizada:
    python -c "import urllib.request; print(urllib.request.urlopen('https://httpbin.org/get').read().decode())"
"""

import urllib.request  # FIX: en Python 3 no existe urllib2; usar urllib.request

# -------------------------------------------------------------------
# URL de destino — cambiar por la URL de tu lab
# -------------------------------------------------------------------
URL = 'https://httpbin.org/get'

# Petición GET — urlopen devuelve un objeto de respuesta similar a un fichero
response = urllib.request.urlopen(URL)
print(response.read().decode('utf-8'))
response.close()
