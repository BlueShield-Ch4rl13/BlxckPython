"""
mapperWP.py - Mapper de rutas de instalación WordPress
=======================================================
Recorre una instalación local de WordPress (o cualquier directorio web),
genera la lista de rutas de ficheros existentes filtrando archivos estáticos
y verifica cuáles de esas rutas son accesibles en el servidor remoto.

ERRORES CORREGIDOS:
    1. Ruta personal `/home/ch4rl13/Downloads/wordpress` reemplazada por
       variable de entorno WP_PATH con valor por defecto genérico.
    2. URL personal reemplazada por constante TARGET configurable.

REQUISITOS:
    pip install requests

EJEMPLOS DE EJECUCIÓN:
    # Indicando la ruta local de WordPress y el servidor objetivo:
    WP_PATH=/var/www/html/wordpress TARGET=https://tu-servidor-lab python mapperWP.py

    # O editar WP_PATH y TARGET directamente en el script.
"""

import contextlib
import os
import queue
import sys
import threading
import time

import requests

# -------------------------------------------------------------------
# Configuración — ajustar para tu entorno de lab
# -------------------------------------------------------------------
FILTERED  = [".jpg", ".gif", ".png", ".css"]
TARGET    = os.environ.get('TARGET', 'https://target-example.com/wordpress')   # FIX: URL personal eliminada
WP_PATH   = os.environ.get('WP_PATH', './wordpress')  # FIX: ruta personal eliminada
THREADS   = 10

answers   = queue.Queue()
web_paths = queue.Queue()


def gather_paths():
    """
    Recorre el directorio WP_PATH y encola todas las rutas de ficheros
    que no sean imágenes ni hojas de estilo.
    """
    for root, _, files in os.walk('.'):
        for fname in files:
            if os.path.splitext(fname)[1] in FILTERED:
                continue
            path = os.path.join(root, fname)
            if path.startswith('.'):
                path = path[1:]
            print(path)
            web_paths.put(path)


@contextlib.contextmanager
def chdir(path):
    """
    Context manager que cambia al directorio indicado durante el bloque
    `with` y lo restaura al salir.

    Args:
        path (str): Directorio al que cambiar temporalmente.
    """
    this_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(this_dir)


def test_remote():
    """
    Consume la Queue de rutas y comprueba si cada una existe en el servidor
    remoto (respuesta 200). Introduce una pausa de 2 s para evitar bloqueos.
    """
    while not web_paths.empty():
        path = web_paths.get()
        url  = f'{TARGET}{path}'
        time.sleep(2)  # Pausa para evitar rate-limiting/lockout del servidor
        r = requests.get(url)
        if r.status_code == 200:
            answers.put(url)
            sys.stdout.write('+')
        else:
            sys.stdout.write('x')
        sys.stdout.flush()


def run():
    """Lanza THREADS hilos para probar todas las rutas en paralelo."""
    mythreads = []
    for i in range(THREADS):
        print(f'Lanzando hilo {i}')
        t = threading.Thread(target=test_remote)
        mythreads.append(t)
        t.start()
    for thread in mythreads:
        thread.join()


if __name__ == '__main__':
    # FIX: ruta personal `/home/ch4rl13/Downloads/wordpress` → variable WP_PATH
    with chdir(WP_PATH):
        gather_paths()
    input('Presiona Enter para continuar.')

    run()
    with open('myanswers.txt', 'w') as f:
        while not answers.empty():
            f.write(f'{answers.get()}\n')
    print('done')
