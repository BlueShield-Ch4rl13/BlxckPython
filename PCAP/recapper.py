"""
recapper.py - Extracción de imágenes desde capturas de red (PCAP)
==================================================================
Lee un fichero PCAP con Scapy, reconstruye los flujos TCP en el puerto 80,
parsea las cabeceras HTTP de las respuestas y extrae el contenido binario
(imágenes u otros recursos) guardándolo en disco.

Flujo:
    1. Recapper.__init__: carga el PCAP y obtiene las sesiones TCP.
    2. get_responses():   reconstruye las respuestas HTTP de cada sesión.
    3. write():           extrae el contenido de un tipo dado y lo guarda.

ERRORES CORREGIDOS:
    1. `get_header()` no tenía `return header` al final.
       Sin el return, siempre devolvía None y ninguna respuesta se procesaba.
    2. `Recapper = Recapper(pfile)` → variable con el mismo nombre que la clase,
       lo que destruye la referencia a la clase en ese scope.
       Corregido a `recapper = Recapper(pfile)` (minúscula).
    3. `recapper.write('iamge')` → typo; corregido a `'image'`.
    4. `'Content_Encoding'` → clave HTTP incorrecta (guion bajo en lugar de guion).
       Corregido a `'Content-Encoding'`.
    5. Rutas personales reemplazadas por variables de entorno.

REQUISITOS:
    pip install scapy

EJEMPLOS DE EJECUCIÓN:
    PCAPS=/root/Downloads OUTDIR=/tmp/imgs python recapper.py
"""

import collections
import os
import re
import sys
import zlib

from scapy.all import TCP, rdpcap

# -------------------------------------------------------------------
# Rutas de trabajo — configurables por variables de entorno
# -------------------------------------------------------------------
OUTDIR = os.environ.get('OUTDIR', '/root/Desktop/pictures')  # Directorio de salida para imágenes
PCAPS  = os.environ.get('PCAPS',  '/root/Downloads')         # Directorio de ficheros PCAP

# Named tuple para empaquetar cabecera y payload de cada respuesta HTTP
Response = collections.namedtuple('Response', ['header', 'payload'])


def get_header(payload):
    """
    Extrae y parsea las cabeceras HTTP de un payload TCP concatenado.

    Args:
        payload (bytes): Bytes crudos de la sesión TCP.

    Returns:
        dict | None: Diccionario {nombre_cabecera: valor} o None si el
                     payload no contiene cabeceras HTTP válidas o no tiene
                     'Content-Type'.
    """
    try:
        header_raw = payload[:payload.index(b'\r\n\r\n') + 2]
    except ValueError:
        sys.stdout.write('-')
        sys.stdout.flush()
        return None

    header = dict(re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n',
                              header_raw.decode()))
    if 'Content-Type' not in header:
        return None

    return header  # FIX: faltaba esta línea — sin return siempre devolvía None


def extract_content(response, content_name='image'):
    """
    Extrae el cuerpo de una respuesta HTTP si su Content-Type coincide
    con `content_name`. Descomprime gzip/deflate si fuera necesario.

    Args:
        response     (Response): Named tuple con .header y .payload.
        content_name (str):      Tipo de contenido a buscar (p. ej. 'image').

    Returns:
        tuple: (content: bytes | None, content_type: str | None)
    """
    content, content_type = None, None

    if content_name in response.header.get('Content-Type', ''):
        content_type = response.header['Content-Type'].split('/')[1]
        content = response.payload[response.payload.index(b'\r\n\r\n') + 4:]

        # FIX: 'Content_Encoding' → 'Content-Encoding' (guion, no guion bajo)
        if 'Content-Encoding' in response.header:
            encoding = response.header['Content-Encoding']
            if encoding == 'gzip':
                content = zlib.decompress(response.payload, zlib.MAX_WBITS | 32)
            elif encoding == 'deflate':
                content = zlib.decompress(response.payload)

    return content, content_type


class Recapper:
    """Lee un PCAP, reconstruye respuestas HTTP y extrae su contenido."""

    def __init__(self, fname):
        """
        Carga el fichero PCAP y prepara las sesiones TCP.

        Args:
            fname (str): Ruta al fichero .pcap.
        """
        pcap = rdpcap(fname)
        self.sessions  = pcap.sessions()
        self.responses = []

    def get_responses(self):
        """
        Recorre las sesiones TCP del PCAP, concatena los payloads del
        puerto 80 y parsea las cabeceras HTTP de cada respuesta encontrada.
        """
        for session in self.sessions:
            payload = b''
            for packet in self.sessions[session]:
                try:
                    if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                        payload += bytes(packet[TCP].payload)
                except IndexError:
                    sys.stdout.write('x')
                    sys.stdout.flush()

            if payload:
                header = get_header(payload)
                if header is None:
                    continue
                self.responses.append(Response(header=header, payload=payload))

    def write(self, content_name):
        """
        Extrae y guarda en OUTDIR el contenido de las respuestas cuyo
        Content-Type coincida con `content_name`.

        Args:
            content_name (str): Tipo de contenido a extraer (p. ej. 'image').
        """
        for i, response in enumerate(self.responses):
            content, content_type = extract_content(response, content_name)
            if content and content_type:
                fname = os.path.join(OUTDIR, f'ex_{i}.{content_type}')
                print(f'Escribiendo {fname}')
                with open(fname, 'wb') as f:
                    f.write(content)


if __name__ == '__main__':
    pfile = os.path.join(PCAPS, 'pcap.pcap')
    # FIX: `Recapper = Recapper(pfile)` → `recapper = Recapper(pfile)`
    #      (nombre en minúscula para no sobrescribir la clase)
    recapper = Recapper(pfile)
    recapper.get_responses()
    recapper.write('image')   # FIX: 'iamge' → 'image'
