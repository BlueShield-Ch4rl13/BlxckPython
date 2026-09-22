"""
sniffer_with_icmp.py - Sniffer con decodificación de cabecera IP e ICMP
=========================================================================
Extiende sniffer_ip_header_decode.py añadiendo la decodificación de la
cabecera ICMP (type, code) para los paquetes que correspondan al
protocolo ICMP.

REQUISITOS:
    - Python 3.x
    - Root / administrador para raw sockets.

EJEMPLOS DE EJECUCIÓN:
    sudo python sniffer_with_icmp.py               # escucha en 0.0.0.0
    sudo python sniffer_with_icmp.py 192.168.1.10  # interfaz específica
    # Pulsa Ctrl+C para detener.
"""

import ipaddress
import os
import struct
import socket
import sys

# Tamaño de la cabecera ICMP: Type(1) + Code(1) + Checksum(2) + ID(2) + Seq(2)
ICMP_HEADER_SIZE = struct.calcsize('<BBHHH')


class IP:
    """
    Deserializa los primeros 20 bytes de un paquete IPv4.
    Ver sniffer_ip_header_decode.py para documentación completa.
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
            self.protocol = str(self.protocol_num)


class ICMP:
    """
    Deserializa la cabecera ICMP (8 bytes mínimo).

    Atributos:
        type (int): Tipo de mensaje ICMP (0=echo reply, 8=echo request, etc.).
        code (int): Código subordinado al tipo.
        sum  (int): Checksum.
        id   (int): Identificador.
        seq  (int): Número de secuencia.
    """

    def __init__(self, buff: bytes):
        header   = struct.unpack('<BBHHH', buff)
        self.type = header[0]
        self.code = header[1]
        self.sum  = header[2]
        self.id   = header[3]
        self.seq  = header[4]


def sniff(host: str):
    """
    Captura paquetes y, si son ICMP, muestra tipo y código.

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

            # Mostrar todos los paquetes con su protocolo e IPs
            print(f'Protocol: {ip_header.protocol:5s}  '
                  f'{ip_header.src_address} → {ip_header.dst_address}')

            # Si es ICMP, decodificar también la cabecera ICMP
            if ip_header.protocol == "ICMP":
                # La cabecera ICMP empieza después de la cabecera IP
                offset      = ip_header.ihl * 4
                buf         = raw_buffer[offset: offset + ICMP_HEADER_SIZE]
                icmp_header = ICMP(buf)
                print(f'  └─ ICMP Type: {icmp_header.type}  Code: {icmp_header.code}')
                print(f'     Version: {ip_header.ver}  Header Length: {ip_header.ihl}  TTL: {ip_header.ttl}')

    except KeyboardInterrupt:
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        print("\n[*] Sniffer stopped.")
        sys.exit()


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) == 2 else '0.0.0.0'
    sniff(host)
