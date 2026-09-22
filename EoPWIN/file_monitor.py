"""
file_monitor.py - Monitor de cambios en el sistema de ficheros (Windows)
=========================================================================
Vigila uno o varios directorios de Windows en busca de cambios (creación,
eliminación, modificación, renombrado de ficheros). Cuando se detecta una
modificación, vuelca el contenido del fichero por consola.

Usa la API win32file.ReadDirectoryChangesW para recibir notificaciones del
kernel en tiempo real sin sondeo activo.

ERRORES CORREGIDOS:
    1. Indentación incorrecta del bloque `try:` dentro de `while True:`.
       El `try` estaba al mismo nivel que el `while` (fuera del bucle),
       por lo que el bucle solo ejecutaba una iteración y luego salía.
       Corregido: el `try` debe estar indentado dentro del `while True:`.

REQUISITOS:
    pip install pywin32

EJEMPLOS DE EJECUCIÓN:
    python file_monitor.py
    # Monitorizará C:\WINDOWS\Temp y el directorio temporal del sistema.
"""

import os
import tempfile
import threading

import win32con
import win32file

# Constantes de acción devueltas por ReadDirectoryChangesW
FILE_CREATED      = 1
FILE_DELETE       = 2
FILE_MODIFIED     = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO   = 5

FILE_LIST_DIRECTORY = 0x0001

# Directorios a vigilar
PATHS = ['C:\\WINDOWS\\Temp', tempfile.gettempdir()]


def monitor(path_to_watch):
    """
    Vigila `path_to_watch` de forma indefinida e imprime cada cambio detectado.
    Cuando un fichero se modifica, vuelca su contenido por consola.

    Args:
        path_to_watch (str): Ruta del directorio a monitorizar.
    """
    h_directory = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    while True:
        # FIX: el bloque `try` estaba fuera del `while True` (mismo nivel de indentación),
        #      por lo que el bucle terminaba tras la primera iteración.
        #      Corregido: el `try` va DENTRO del `while True`.
        try:
            results = win32file.ReadDirectoryChangesW(
                h_directory,
                1024,
                True,
                (win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES   |
                 win32con.FILE_NOTIFY_CHANGE_DIR_NAME     |
                 win32con.FILE_NOTIFY_CHANGE_FILE_NAME    |
                 win32con.FILE_NOTIFY_CHANGE_LAST_WRITE   |
                 win32con.FILE_NOTIFY_CHANGE_SECURITY     |
                 win32con.FILE_NOTIFY_CHANGE_SIZE),
                None,
                None
            )
            for action, file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)
                if action == FILE_CREATED:
                    print(f'[+] Creado: {full_filename}')
                elif action == FILE_DELETE:
                    print(f'[-] Eliminado: {full_filename}')
                elif action == FILE_MODIFIED:
                    print(f'[*] Modificado: {full_filename}')
                    try:
                        print('[vvv] Volcando contenido ... ')
                        with open(full_filename) as f:
                            contents = f.read()
                        print(contents)
                        print('[^^^] Volcado completo.')
                    except Exception as e:
                        print(f'[!!!] Error al volcar: {e}')
                elif action == FILE_RENAMED_FROM:
                    print(f'[>] Renombrado desde: {full_filename}')
                elif action == FILE_RENAMED_TO:
                    print(f'[<] Renombrado a: {full_filename}')
                else:
                    print(f'[?] Acción desconocida en: {full_filename}')

        except Exception:
            pass


if __name__ == '__main__':
    for path in PATHS:
        monitor_thread = threading.Thread(target=monitor, args=(path,))
        monitor_thread.daemon = True
        monitor_thread.start()
    # Mantener el hilo principal vivo
    import time
    while True:
        time.sleep(1)
