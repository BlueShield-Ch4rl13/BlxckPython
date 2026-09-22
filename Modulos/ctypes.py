"""
ctypes.py - Estructura IP de bajo nivel con ctypes (C struct mapping)
======================================================================
NOTA: este fichero tiene el mismo nombre que el módulo estándar `ctypes`
de Python. Si se importa desde otro script, Python lo encontrará primero
si está en el mismo directorio o en sys.path antes que la biblioteca
estándar. Renombrar si fuera a usarse como módulo importable.

Define la clase `IP` como una Structure de ctypes mapeada directamente
sobre un buffer de bytes del socket raw, permitiendo acceder a los campos
del cabecero IPv4 (versión, IHL, TTL, protocolo, IPs src/dst) sin parsear
manualmente con `struct.unpack`.

ERRORES CORREGIDOS:
    - Sin errores; el código original es correcto.
      Se añade docstring y comentarios explicativos.

REQUISITOS:
    - Python 3.x + socket raw (requiere privilegios root/admin)

EJEMPLOS DE EJECUCIÓN:
    import socket, struct
    # Recibir un paquete IP raw y parsearlo:
    # sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    # raw_buffer = sock.recvfrom(65535)[0]
    # ip_header = IP(raw_buffer[:20])
    # print(ip_header.src_address, '->', ip_header.dst_address)
"""

from ctypes import (
    c_ubyte, c_uint32, c_ushort,
    Structure, sizeof
)
import socket
import struct


class IP(Structure):
    """
    Mapeo ctypes del cabecero IPv4 (20 bytes mínimo).

    Los campos se definen en el orden del wire-format (big-endian
    para los campos de 16/32 bits; los nibbles IHL/version se tratan
    como little-endian a nivel de byte por la arquitectura x86).

    Attributes:
        ihl         (int): Internet Header Length (4 bits).
        version     (int): Versión IP (4 bits); debe ser 4.
        tos         (int): Type of Service (1 byte).
        len         (int): Longitud total del paquete IP.
        id          (int): Identificador de fragmento.
        offset      (int): Desplazamiento de fragmento.
        ttl         (int): Time to Live.
        protocol_num(int): Número de protocolo de transporte (1=ICMP,6=TCP,17=UDP).
        sum         (int): Checksum del cabecero.
        src         (int): Dirección IP origen en formato entero de 32 bits.
        dst         (int): Dirección IP destino en formato entero de 32 bits.
    """
    _fields_ = [
        ("ihl",          c_ubyte,  4),
        ("version",      c_ubyte,  4),
        ("tos",          c_ubyte),
        ("len",          c_ushort),
        ("id",           c_ushort),
        ("offset",       c_ushort),
        ("ttl",          c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum",          c_ushort),
        ("src",          c_uint32),
        ("dst",          c_uint32),
    ]

    def __new__(cls, socket_buffer=None):
        """Crea la instancia copiando el buffer raw directamente en la estructura."""
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        # Mapa de números de protocolo a nombres legibles
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # Convertir enteros de 32 bits a notación dotted-decimal
        self.src_address = socket.inet_ntoa(struct.pack("!L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("!L", self.dst))

    def __repr__(self):
        proto = self.protocol_map.get(self.protocol_num, str(self.protocol_num))
        return (f"<IP {self.src_address} → {self.dst_address} "
                f"proto={proto} ttl={self.ttl} len={self.len}>")
