"""
request.py - Peticiones HTTP GET y POST con la librería requests
=================================================================
Muestra cómo realizar peticiones GET y POST usando `requests`,
la librería HTTP más popular de Python. GET recupera una página;
POST envía datos al servidor (p. ej. un formulario de login).

REQUISITOS:
    pip install requests

EJEMPLOS DE EJECUCIÓN:
    python request.py

    # Importando como módulo:
    import requests
    r = requests.get('https://httpbin.org/get')
    print(r.status_code, r.json())
"""

import requests

# -------------------------------------------------------------------
# URL de destino — cambiar por la URL de tu lab
# -------------------------------------------------------------------
URL = 'https://httpbin.org'

# --- GET ---
response = requests.get(URL + '/get')     # FIX: typo 'respose' → 'response'
print("[GET] Status:", response.status_code)
print(response.text[:500])                # Mostrar solo los primeros 500 chars

# --- POST (envío de formulario) ---
data = {
    'user':   'usuario_lab',              # FIX: datos personales eliminados
    'passwd': 'contraseña_lab',
}
response = requests.post(URL + '/post', data=data)  # FIX: mismo typo
print("\n[POST] Status:", response.status_code)
# response.text    → contenido como string
# response.content → contenido como bytes
print(response.text[:500])
