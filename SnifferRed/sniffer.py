"""
sniffer.py - Sniffer de paquetes crudos (raw socket)
======================================================
Captura un único paquete de red en la interfaz indicada usando
raw sockets. En Windows habilita el modo promiscuo; en Linux
captura solo ICMP (sin privilegios de promiscuo).

REQUISITOS:
    - Python 3.x
    - Ejecutar con privilegios de root / administrador.

EJEMPLOS DE EJECUCIÓN:
    # Linux (captura ICMP en la interfaz con IP 192.168.1.10):
    sudo python sniffer.py 192.168.1.10

    # Linux con IP por defecto (0.0.0.0):
    sudo python sniffer.py

    # Windows (captura todos los protocolos):
    python sniffer.py 192.168.1.10
"""

import os
import socket
import sys


def main(host: str = '0.0.0.0'):
    """
    Crea un raw socket, captura un paquete y lo imprime.

    Args:
        host (str): Dirección IP de la interfaz en la que escuchar.
    """
    # En Windows se usa IPPROTO_IP para capturar todo el tráfico IP
    # En Linux solo se puede capturar ICMP sin promiscuous mode
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))
    # Incluir la cabecera IP en los datos capturados
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == 'nt':
        # Activar modo promiscuo en Windows
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    print(f"[*] Listening on {host} — waiting for one packet...")
    print(sniffer.recvfrom(65565))

    if os.name == 'nt':
        # Desactivar modo promiscuo al finalizar
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) == 2 else '0.0.0.0'
    main(host)
