"""
BeautifulSoup.py - Scraping de enlaces con BeautifulSoup4
==========================================================
Descarga una página web con `requests` y extrae todos los hipervínculos
(<a href="...">) usando BeautifulSoup con el parser HTML estándar.

ERRORES CORREGIDOS:
    1. `tree.fin_all(...)` → `tree.find_all(...)` (typo en el nombre del método).
    2. El selector `'//a'` es sintaxis XPath, no válida en BeautifulSoup.
       Corregido a `'a'` (selector de etiqueta CSS/BS4).
    3. URL personal reemplazada por dominio de ejemplo.

REQUISITOS:
    pip install requests beautifulsoup4

EJEMPLOS DE EJECUCIÓN:
    python BeautifulSoup.py

    # Importando como módulo:
    from bs4 import BeautifulSoup as bs
    import requests
    tree = bs(requests.get('https://httpbin.org').text, 'html.parser')
    for link in tree.find_all('a'):
        print(link.get('href'), '->', link.text)
"""

from bs4 import BeautifulSoup as bs
import requests

# -------------------------------------------------------------------
# URL de destino — cambiar por la URL de tu lab
# -------------------------------------------------------------------
URL = 'https://httpbin.org'  # FIX: URL personal eliminada

r = requests.get(URL)  # Petición GET a la URL objetivo

# Parsear el HTML de la respuesta con el parser estándar de Python
tree = bs(r.text, 'html.parser')

# FIX: 'fin_all' → 'find_all' (typo)
# FIX: '//a' (XPath) → 'a' (selector BS4 por nombre de etiqueta)
for link in tree.find_all('a'):
    print(f"{link.get('href')} -> {link.text}")
