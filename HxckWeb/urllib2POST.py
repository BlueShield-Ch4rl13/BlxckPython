"""
urllib2POST.py - Petición HTTP GET con cabeceras personalizadas (Python 3)
===========================================================================
Realiza una petición GET enviando una cabecera User-Agent personalizada
usando solo la biblioteca estándar de Python 3.

REQUISITOS:
    - Python 3.x (solo biblioteca estándar)

EJEMPLOS DE EJECUCIÓN:
    python urllib2POST.py
"""

import urllib.request  # FIX: Python 2 `urllib2` → Python 3 `urllib.request`

# -------------------------------------------------------------------
# URL y cabeceras de ejemplo
# -------------------------------------------------------------------
URL     = 'https://httpbin.org/get'
headers = {'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'}

# Construir la petición con cabeceras personalizadas (método GET por defecto)
request  = urllib.request.Request(URL, headers=headers)
response = urllib.request.urlopen(request)

print(response.read().decode('utf-8'))
response.close()
