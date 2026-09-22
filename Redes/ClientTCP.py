"""
ClientTCP.py - Cliente TCP básico con socket
==============================================
Abre una conexión TCP a un host/puerto, envía una petición HTTP GET
y muestra la respuesta del servidor.

REQUISITOS:
    - Python 3.x
    - No requiere librerías externas.

EJEMPLOS DE EJECUCIÓN:
    # Conectar al puerto 80 de google.com
    python ClientTCP.py

    # Para cambiar el host/puerto, edita las variables target_host y target_port
    # antes de ejecutar.
"""

import socket

# -------------------------------------------------------------------
# Parámetros de conexión - ajusta según el objetivo de lab
# -------------------------------------------------------------------
TARGET_HOST = "www.google.com"   # Host al que conectarse
TARGET_PORT = 80                  # Puerto HTTP estándar

# Crear el socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar al servidor
client.connect((TARGET_HOST, TARGET_PORT))

# Enviar petición HTTP GET mínima
client.send(b"GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n")

# Recibir hasta 4096 bytes de respuesta
response = client.recv(4096)

print(response.decode(errors="replace"))
client.close()
