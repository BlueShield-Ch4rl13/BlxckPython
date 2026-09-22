"""
bhservice.py - Servicio Windows vulnerable para práctica de EoP (Elevation of Privilege)
==========================================================================================
Implementa un servicio Windows (via pywin32) que, cada minuto, copia
un script VBScript desde SRCDIR a C:\Windows\TEMP y lo ejecuta con cscript.
Si el directorio SRCDIR tiene permisos de escritura para usuarios sin privilegios,
un atacante puede sustituir el .vbs para elevar privilegios.

REQUISITOS:
    pip install pywin32
    pyinstaller -F --hiddenimport win32timezone bhservice.py

EJEMPLOS DE EJECUCIÓN:
    bhservice.exe install
    bhservice.exe start
    bhservice.exe stop
    bhservice.exe remove
"""

import os
import servicemanager
import shutil
import subprocess
import sys

import win32event
import win32service
import win32serviceutil

# -------------------------------------------------------------------
# Configuración — leer desde variables de entorno
# -------------------------------------------------------------------
# FIX: SRCIR → SRCDIR (typo); ruta personal reemplazada por variable de entorno
SRCDIR = os.environ.get('BH_SRCDIR', 'C:\\bhservice_src')
TGTDIR = 'C:\\Windows\\TEMP'


class BHServerSvc(win32serviceutil.ServiceFramework):
    """
    Servicio Windows de demostración para prácticas de EoP.
    Ejecuta un VBScript copiado desde SRCDIR cada minuto.
    """
    _svc_name         = "BlackHatService"
    _svc_display_name = "Black Hat Service"
    _svc_description  = (
        "Ejecuta VBScripts a intervalos regulares. "
        "¿Qué podría salir mal?"
    )

    def __init__(self, args):
        self.vbs     = os.path.join(TGTDIR, 'bhservice_task.vbs')
        self.timeout = 1000 * 60  # 1 minuto en milisegundos

        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        """Señaliza al servicio que debe detenerse."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Punto de entrada del hilo del servicio."""
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main()

    def main(self):
        """
        Bucle principal: espera el evento de parada o el timeout (1 min),
        copia el VBScript desde SRCDIR y lo ejecuta con cscript.exe.
        """
        while True:
            ret_code = win32event.WaitForSingleObject(
                self.hWaitStop, self.timeout
            )
            if ret_code == win32event.WAIT_OBJECT_0:
                servicemanager.LogInfoMsg("Service is stopping")
                break
            src = os.path.join(SRCDIR, 'bhservice_task.vbs')  # FIX: SRCIR → SRCDIR
            shutil.copy(src, self.vbs)
            subprocess.call("cscript.exe %s" % self.vbs, shell=False)
            os.unlink(self.vbs)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BHServerSvc)  # FIX: PrepareToHost.Single → PrepareToHostSingle
        servicemanager.StartServiceCtrlDispatcher()
    else:                                                 # FIX: `else.` → `else:`
        win32serviceutil.HandleCommandLine(BHServerSvc)
