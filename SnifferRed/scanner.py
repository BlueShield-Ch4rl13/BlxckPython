"""
scanner.py - Escáner de hosts activos por ICMP/UDP
=====================================================
Envía datagramas UDP a todos los hosts de una subred y detecta cuáles
responden con mensajes ICMP "Port Unreachable" (tipo 3, código 3),
lo que indica que el host está activo aunque no tenga el puerto abierto.

Funciona en dos fases:
  1. Un hilo dispara datagramas UDP con un mensaje mágico a todos los hosts.
  2. El hilo principal captura respuestas ICMP y filtra las que contienen
     el mensaje mágico para confirmar que el host está activo.

REQUISITOS:
    - Python 3.x
    - Root / administrador para raw sockets.

EJEMPLOS DE EJECUCIÓN:
    # Escanear la subred 192.168.1.0/24:
    sudo python scanner.py 192.168.1.10

    # Escanear con IP de escucha por defecto (0.0.0.0):
    sudo python scanner.py

    # Pulsa Ctrl+C al terminar para ver el resumen de hosts activos.
"""

import ipaddress
import os
import socket
import struct
import sys
import threading
import time

# -------------------------------------------------------------------
# Configuración — ajustar según el entorno de lab
# -------------------------------------------------------------------
SUBNET  = '192.168.1.0/24'   # Subred objetivo
MESSAGE = 'PYTHONRULES!'      # Cadena mágica incluida en cada UDP


class IP:
    """Deserializa cabecera IPv4 (20 bytes)."""

    def __init__(self, buff: bytes = None):
        header = struct.unpack('<BBHHHBBH4s4s', buff)
        self.ver          = header[0] >> 4
        self.ihl          = header[0] & 0xF
        self.tos          = header[1]
        self.len          = header[2]
        self.id           = header[3]
        self.offset       = header[4]
        self.ttl          = header[5]
        self.protocol_num = header[6]
        self.sum          = header[7]
        self.src          = header[8]
        self.dst          = header[9]

        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except KeyError:
            print(f'{self.protocol_num} not in protocol_map')
            self.protocol = str(self.protocol_num)


class ICMP:
    """Deserializa cabecera ICMP (8 bytes)."""

    def __init__(self, buff: bytes):
        header    = struct.unpack('<BBHHH', buff)
        self.type = header[0]
        self.code = header[1]
        self.sum  = header[2]
        self.id   = header[3]
        self.seq  = header[4]


def udp_sender():
    """Envía datagramas UDP con el mensaje mágico a todos los hosts de SUBNET."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(SUBNET).hosts():
            sender.sendto(MESSAGE.encode('utf-8'), (str(ip), 65212))


class Scanner:
    """Escáner ICMP que detecta hosts activos a partir de respuestas Port Unreachable."""

    def __init__(self, host: str):
        self.host = host
        socket_protocol = socket.IPPROTO_IP if os.name == 'nt' else socket.IPPROTO_ICMP

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        self.socket.bind((host, 0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if os.name == 'nt':
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def sniff(self):
        """Captura paquetes e identifica hosts activos."""
        hosts_up = {f'{str(self.host)} *'}   # Incluir el propio host

        try:
            while True:
                raw_buffer = self.socket.recvfrom(65535)[0]
                ip_header  = IP(raw_buffer[0:20])

                if ip_header.protocol == "ICMP":
                    offset      = ip_header.ihl * 4
                    buf         = raw_buffer[offset:offset + 8]
                    icmp_header = ICMP(buf)

                    # ICMP Type 3 Code 3 = Port Unreachable → host activo
                    if icmp_header.type == 3 and icmp_header.code == 3:
                        if ipaddress.ip_address(ip_header.src_address) in \
                                ipaddress.ip_network(SUBNET):
                            # Verificar que la respuesta contiene nuestro mensaje
                            if raw_buffer[len(raw_buffer) - len(MESSAGE):] == \
                                    MESSAGE.encode('utf-8'):
                                tgt = str(ip_header.src_address)
                                if tgt != self.host and tgt not in hosts_up:
                                    hosts_up.add(tgt)
                                    print(f'Host UP: {tgt}')

        except KeyboardInterrupt:
            if os.name == 'nt':
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            print('\n[*] User interrupted.')
            if hosts_up:
                print(f'\nSummary — hosts up on {SUBNET}:')
                for h in sorted(hosts_up):
                    print(f'  {h}')
            sys.exit()


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) == 2 else '0.0.0.0'
    s = Scanner(host)
    print(f"[*] Waiting 5 seconds before sending UDP probes to {SUBNET}…")
    time.sleep(5)
    t = threading.Thread(target=udp_sender)
    t.start()
    s.sniff()
