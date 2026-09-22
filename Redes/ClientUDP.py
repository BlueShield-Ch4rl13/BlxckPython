"""
ClientUDP.py - Cliente UDP básico con socket
=============================================
Envía un mensaje UDP a un host/puerto y espera respuesta.
UDP no establece conexión: el datagrama se envía y se espera respuesta.

REQUISITOS:
    - Python 3.x
    - El servidor UDP debe estar escuchando en target_host:target_port.

EJEMPLOS DE EJECUCIÓN:
    # Iniciar primero un listener UDP en otro terminal:
    #   nc -u -l -p 9999
    # Luego ejecutar:
    python ClientUDP.py
"""

import socket

# -------------------------------------------------------------------
# Parámetros de conexión
# -------------------------------------------------------------------
TARGET_HOST = "127.0.0.1"  # Loopback para pruebas locales
TARGET_PORT = 9999

# Crear socket UDP (SOCK_DGRAM = UDP)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enviar datos al destino (sin conexión previa)
client.sendto(b"Hello!", (TARGET_HOST, TARGET_PORT))

# Recibir respuesta (máx. 4096 bytes); addr = dirección del remitente
data, addr = client.recvfrom(4096)

print(data.decode())
client.close()
