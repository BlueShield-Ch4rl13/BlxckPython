"""
sandbox_detect.py - Detección de entorno sandbox (Windows)
===========================================================
Comprueba si el proceso se está ejecutando en un sandbox (análisis automático)
midiendo la interacción real del usuario:
  - Si el sistema lleva mucho tiempo inactivo, se asume sandbox y termina.
  - Se esperan N pulsaciones de teclado, M clics de ratón y P doble-clics
    antes de considerar que el entorno es humano y continuar.

REQUISITOS:
    pip install pywin32

EJEMPLOS DE EJECUCIÓN:
    python sandbox_detect.py
    # Si se ejecuta en sandbox (sin interacción humana), termina al instante.
    # Si detecta interacción suficiente, imprime 'okay.' y continúa.
"""

from ctypes import byref, c_uint, c_ulong, sizeof, Structure, windll

import random
import sys
import time

import win32api


# -----------------------------------------------------------------------
# Estructura para obtener el tiempo desde el último input del usuario
# -----------------------------------------------------------------------

class LASTINPUTINFO(Structure):
    """Estructura de Windows para GetLastInputInfo."""
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_ulong),
    ]


def get_last_input():
    """
    Devuelve el número de milisegundos transcurridos desde el último
    evento de entrada del usuario (ratón o teclado).

    Returns:
        int: Milisegundos de inactividad.
    """
    # FIX: `get_last_input` era un método dentro de la estructura
    #      LASTINPUTINFO._fields_ (ilegible y no funcional).
    #      Movida aquí como función de módulo.
    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = sizeof(LASTINPUTINFO)
    windll.user32.GetLastInputInfo(byref(struct_lastinputinfo))
    run_time = windll.kernel32.GetTickCount()
    elapsed  = run_time - struct_lastinputinfo.dwTime
    print(f"[*] Han pasado {elapsed} ms desde el último evento de entrada.")
    return elapsed


# -----------------------------------------------------------------------
# Clase detectora de entorno sandbox
# -----------------------------------------------------------------------

class Detector:
    """
    Monitoriza la interacción del usuario para determinar si el proceso
    se ejecuta en un entorno humano real o en un sandbox automatizado.
    """

    def __init__(self):
        self.double_clicks = 0
        self.keystrokes    = 0
        self.mouse_clicks  = 0

    def get_key_press(self):
        """
        Comprueba el estado de todas las teclas virtuales.
        Devuelve el timestamp del evento si se detecta un clic de ratón
        o una tecla imprimible; None en caso contrario.

        Returns:
            float | None: Tiempo del evento o None.
        """
        for i in range(0, 0xFF):
            state = win32api.GetAsyncKeyState(i)
            if state & 0x0001:
                if i == 0x01:          # Botón izquierdo del ratón
                    self.mouse_clicks += 1
                    return time.time()
                elif 32 < i < 127:     # Carácter imprimible
                    self.keystrokes += 1
        return None

    def detect(self):
        """
        Bucle de detección: comprueba inactividad inicial y espera hasta
        alcanzar umbrales de interacción humana.
        Llama a sys.exit(0) si detecta sandbox (inactividad excesiva o
        doble-clics demasiado rápidos para ser humanos).
        """
        previous_timestamp    = None
        first_double_click    = None        # FIX: inicializada antes de su uso
        double_click_threshold = 0.35       # segundos

        max_double_clicks  = 10
        max_keystrokes     = random.randint(10, 25)
        max_mouse_clicks   = random.randint(5, 25)
        max_input_threshold = 30000         # ms de inactividad = sandbox

        # Si el sistema lleva > 30s inactivo al arrancar → sandbox
        last_input = get_last_input()
        if last_input >= max_input_threshold:
            sys.exit(0)

        detection_complete = False
        while not detection_complete:
            keypress_time = self.get_key_press()

            if keypress_time is not None and previous_timestamp is not None:
                elapsed = keypress_time - previous_timestamp

                if elapsed <= double_click_threshold:
                    # Doble clic detectado
                    self.mouse_clicks -= 2
                    self.double_clicks += 1

                    if first_double_click is None:
                        first_double_click = time.time()
                    else:
                        # FIX: el `else` mal indentado en el original colgaba
                        #      del `if first_double_click` en lugar del interno
                        if self.double_clicks >= max_double_clicks:
                            interval = keypress_time - first_double_click
                            if interval <= (max_double_clicks * double_click_threshold):
                                sys.exit(0)

            if (self.keystrokes    >= max_keystrokes and
                    self.double_clicks >= max_double_clicks and
                    self.mouse_clicks  >= max_mouse_clicks):
                detection_complete = True

            if keypress_time is not None:
                previous_timestamp = keypress_time


if __name__ == '__main__':
    d = Detector()
    d.detect()
    print('okay.')
