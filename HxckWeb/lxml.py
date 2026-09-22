"""
lxml.py - Scraping de enlaces con lxml y XPath
===============================================
Descarga una página web con `requests` y extrae todos los hipervínculos
(<a href="...">) usando lxml para parsear el HTML y XPath para la búsqueda.

REQUISITOS:
    pip install lxml requests

EJEMPLOS DE EJECUCIÓN:
    python lxml.py

    # Usando solo lxml con HTML local:
    from lxml import etree
    from io import BytesIO
    html = b'<html><body><a href="/page">Enlace</a></body></html>'
    tree = etree.parse(BytesIO(html), parser=etree.HTMLParser())
    for a in tree.findall('.//a'):
        print(a.get('href'), '->', a.text)
"""

from io import BytesIO
from lxml import etree

import requests

# -------------------------------------------------------------------
# URL de destino — cambiar por la URL de tu lab
# -------------------------------------------------------------------
URL = 'https://httpbin.org'  # FIX: URL personal eliminada

r       = requests.get(URL)
content = r.content  # bytes — lxml.etree.parse necesita bytes o file-like

parser = etree.HTMLParser()

# FIX: `etree.parser(...)` → `etree.parse(...)` (nombre correcto de la función)
tree = etree.parse(BytesIO(content), parser=parser)

# FIX: `content.finall(...)` → `tree.findall('.//a')`
#      - Se usa el árbol parseado, no el objeto bytes
#      - `.//a` busca elementos <a> en cualquier nivel del árbol (XPath relativo)
for link in tree.findall('.//a'):
    print(f"{link.get('href')} -> {link.text}")
