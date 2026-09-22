"""
bruter.py - Fuerza bruta de directorios web (directory brute-forcer)
=====================================================================
Lee una wordlist de rutas potenciales, genera variaciones con extensiones
comunes y lanza peticiones HTTP GET concurrentes para descubrir rutas
existentes en un servidor web (respuesta 200).

REQUISITOS:
    pip install requests

EJEMPLOS DE EJECUCIÓN:
    # Apuntar a tu servidor de lab:
    TARGET="https://tu-servidor-lab" WORDLIST="/ruta/wordlist.txt" python bruter.py

    # O editar las constantes TARGET y WORDLIST directamente en el script.
"""

import os
import queue
import sys
import threading

import requests

# -------------------------------------------------------------------
# Configuración — ajustar para tu entorno de lab
# -------------------------------------------------------------------
AGENT     = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
EXTENSIONS = ['.php', '.bak', '.orig', '.inc']
TARGET    = os.environ.get('TARGET', 'https://target-example.com')   # FIX: URL personal eliminada
THREADS   = 50
WORDLIST  = os.environ.get('WORDLIST', '/usr/share/wordlists/dirb/common.txt')  # FIX: ruta personal eliminada


def get_words(resume=None):
    """
    Lee el wordlist y genera una Queue con todas las rutas a probar,
    añadiendo variantes con extensiones comunes.

    Args:
        resume (str | None): Si se indica una palabra, se omiten todas
                             las anteriores (modo reanudación).
    Returns:
        queue.Queue: Cola con las rutas generadas.
    """
    words = queue.Queue()

    def extend_words(word):
        """Añade la ruta base y sus variantes con extensiones a la Queue."""
        words.put(f'/{word}')           # FIX: antes era `word.put(...)` (str no tiene .put)
        for extension in EXTENSIONS:
            words.put(f'/{word}{extension}')

    with open(WORDLIST) as f:
        raw_words = f.read()

    found_resume = False
    for word in raw_words.split():
        if resume is not None:
            if found_resume:
                extend_words(word)
            elif word == resume:
                found_resume = True
                print(f'Resumiendo wordlist desde: {resume}')
        else:
            extend_words(word)
    return words


def dir_bruter(words):
    """
    Consume la Queue y realiza peticiones GET a cada ruta.
    Imprime las URL que devuelvan 200 OK.

    Args:
        words (queue.Queue): Cola de rutas a probar.
    """
    headers = {'User-Agent': AGENT}
    while not words.empty():
        url = f'{TARGET}{words.get()}'
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            sys.stderr.write('x'); sys.stderr.flush()
            continue

        if r.status_code == 200:
            print(f'\nÉxito ({r.status_code}): {url}')
        elif r.status_code == 404:
            sys.stderr.write('.'); sys.stderr.flush()
        else:
            print(f'{r.status_code} => {url}')


if __name__ == '__main__':
    words = get_words()
    print('Presiona Enter para comenzar el ataque de fuerza bruta.')
    sys.stdin.readline()
    for _ in range(THREADS):
        t = threading.Thread(target=dir_bruter, args=(words,))
        t.start()
