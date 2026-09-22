"""
urllib3GET.py - Petición HTTP GET con urllib.request (Python 3)
================================================================
Recupera el contenido de una URL usando el módulo estándar urllib.
El nombre del archivo hace referencia a la "tercera generación" de
urllib en Python 3, que unificó urllib, urllib2 y httplib de Python 2.

ERRORES CORREGIDOS:
    - Sin errores; el código original ya era Python 3 correcto.
      URL personal reemplazada por dominio de ejemplo.

REQUISITOS:
    - Python 3.x (solo biblioteca estándar)

EJEMPLOS DE EJECUCIÓN:
    python urllib3GET.py
"""

import urllib.parse
import urllib.request

# -------------------------------------------------------------------
# URL de destino — cambiar por la URL de tu lab
# -------------------------------------------------------------------
URL = 'https://httpbin.org/get'

with urllib.request.urlopen(URL) as response:
    content = response.read()

print(content.decode('utf-8'))
