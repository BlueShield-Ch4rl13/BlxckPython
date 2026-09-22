"""
struct.py - Parseado de cabecero IPv4 con struct.unpack (Python puro)
======================================================================
NOTA: este fichero tiene el mismo nombre que el módulo estándar `struct`
de Python. Si se importa desde otro script, Python lo encontrará primero
si está en el mismo directorio o en sys.path antes que la biblioteca
estándar. Renombrar si fuera a usarse como módulo importable.

Define la clase `IP` que parsea manualmente el cabecero IPv4 de 20 bytes
usando `struct.unpack` (Python puro, sin ctypes). Este enfoque es
multiplataforma y no depende del layout de memoria del C-struct.

ERRORES CORREGIDOS:
    - Sin errores; el código original es correcto.
      Se añaden docstrings y comentarios explicativos.

REQUISITOS:
    - Python 3.x (solo biblioteca estándar)

EJEMPLOS DE EJECUCIÓN:
    import socket, ipaddress
    # sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    # raw = sock.recvfrom(65535)[0]
    # ip = IP(raw[:20])
    # print(ip.src_address, '->', ip.dst_address, 'proto:', ip.protocol_num)
"""

import ipaddress
import struct


class IP:
    """
    Parsea el cabecero IPv4 desde un buffer de bytes raw.

    El formato de `struct.unpack` es `<BBHHHBBH4s4s`:
      - '<'  : little-endian (byte order del wire para el primer byte)
      - 'B'  : ver+ihl (1 byte)
      - 'B'  : tos     (1 byte)
      - 'H'  : len     (2 bytes)
      - 'H'  : id      (2 bytes)
      - 'H'  : offset  (2 bytes, incluye flags)
      - 'B'  : ttl     (1 byte)
      - 'B'  : protocol(1 byte)
      - 'H'  : checksum(2 bytes)
      - '4s' : src IP  (4 bytes)
      - '4s' : dst IP  (4 bytes)

    Attributes:
        ver          (int): Versión IP (campo alto de primer byte).
        ihl          (int): Internet Header Length en palabras de 32 bits.
        tos          (int): Type of Service.
        len          (int): Longitud total del paquete.
        id           (int): Identificador de fragmento.
        offset       (int): Desplazamiento de fragmento.
        ttl          (int): Time to Live.
        protocol_num (int): Protocolo de transporte (1=ICMP, 6=TCP, 17=UDP).
        sum          (int): Checksum del cabecero.
        src          (bytes): IP origen en formato de 4 bytes.
        dst          (bytes): IP destino en formato de 4 bytes.
        src_address  (IPv4Address): IP origen legible.
        dst_address  (IPv4Address): IP destino legible.
        protocol_map (dict): Mapa número de protocolo → nombre.
    """

    def __init__(self, buff=None):
        header = struct.unpack('<BBHHHBBH4s4s', buff)

        # Extraer versión (nibble alto) e IHL (nibble bajo) del primer byte
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

        # Convertir bytes a objetos IPv4Address para notación dotted-decimal
        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        # Mapa de protocolos más comunes
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

    def __repr__(self):
        proto = self.protocol_map.get(self.protocol_num, str(self.protocol_num))
        return (f"<IP {self.src_address} → {self.dst_address} "
                f"proto={proto} ttl={self.ttl} len={self.len}>")
