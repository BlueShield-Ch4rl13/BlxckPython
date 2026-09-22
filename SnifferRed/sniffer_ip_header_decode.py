"""
sniffer_ip_header_decode.py - Sniffer con decodificación de cabecera IP
=========================================================================
Captura paquetes raw y deserializa la cabecera IP (20 bytes) mostrando
protocolo, IP origen e IP destino de cada paquete.

ERRORES CORREGIDOS:
    - Sin errores; archivo correcto en el original.

REQUISITOS:
    - Python 3.x
    - Root / administrador para raw sockets.

EJEMPLOS DE EJECUCIÓN:
    sudo python sniffer_ip_header_decode.py               # escucha en 0.0.0.0
    sudo python sniffer_ip_header_decode.py 192.168.1.10  # interfaz específica
    # Pulsa Ctrl+C para detener.
"""

import ipaddress
import os
import struct
import socket
import sys


class IP:
    """
    Deserializa los primeros 20 bytes de un paquete IPv4.

    Atributos:
        ver          (int)  : Versión del protocolo IP (4).
        ihl          (int)  : Longitud de cabecera en palabras de 4 bytes.
        tos          (int)  : Type of Service.
        len          (int)  : Longitud total del datagrama.
        id           (int)  : Identificador del fragmento.
        offset       (int)  : Offset de fragmento.
        ttl          (int)  : Time To Live.
        protocol_num (int)  : Número de protocolo (1=ICMP, 6=TCP, 17=UDP).
        sum          (int)  : Checksum de cabecera.
        src_address  (IPv4Address): IP de origen.
        dst_address  (IPv4Address): IP de destino.
        protocol     (str)  : Nombre del protocolo o número si desconocido.
    """

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
            print(f'[!] Unknown protocol number: {self.protocol_num}')
            self.protocol = str(self.protocol_num)


def sniff(host: str):
    """
    Abre un raw socket y captura indefinidamente, imprimiendo cada paquete.

    Args:
        host (str): IP de la interfaz donde escuchar.
    """
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    print(f"[*] Sniffing on {host}. Press Ctrl+C to stop.")
    try:
        while True:
            raw_buffer = sniffer.recvfrom(65565)[0]
            ip_header  = IP(raw_buffer[0:20])
            print(f'Protocol: {ip_header.protocol:5s}  '
                  f'{ip_header.src_address} → {ip_header.dst_address}')
    except KeyboardInterrupt:
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        print("\n[*] Sniffer stopped.")
        sys.exit()


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) == 2 else '0.0.0.0'
    sniff(host)
