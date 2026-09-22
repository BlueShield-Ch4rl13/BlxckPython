"""
process_monitor.py - Monitor de procesos nuevos con privilegios (Windows)
=========================================================================
Vigila la creación de nuevos procesos en Windows mediante WMI y registra
en un CSV el comando, ejecutable, PIDs, propietario y privilegios activos.
Útil para detectar procesos que heredan tokens elevados o se ejecutan
como SYSTEM.

ERRORES CORREGIDOS:
    1. `exectutable = new_process.ExecutablePath` → typo.
       Corregido a `executable` (también ajustado en el f-string).
    2. `privileges = 'N\A'` → la secuencia `\A` no forma una secuencia
       de escape estándar pero puede causar warnings. Corregido a `'N/A'`.
    3. En `get_process_privileges`, el bloque `except` hacía una llamada
       recursiva infinita: `privileges = get_process_privileges(pid)`.
       Si la primera llamada falla, la recursión no termina nunca.
       Corregido: en el except se asigna `privileges = ''` directamente.

REQUISITOS:
    pip install pywin32 wmi

EJEMPLOS DE EJECUCIÓN:
    python process_monitor.py
    # Registra en process_monitor_log.csv cada nuevo proceso detectado.
"""

import os
import sys

import win32api
import win32con
import win32security
import wmi


def log_to_file(message):
    """
    Añade `message` al fichero CSV de log.

    Args:
        message (str): Línea a registrar.
    """
    with open('process_monitor_log.csv', 'a') as fd:
        fd.write(f'{message}\r\n')


def get_process_privileges(pid):
    """
    Obtiene los privilegios habilitados del proceso con PID `pid`.

    Args:
        pid (int): PID del proceso a inspeccionar.

    Returns:
        str: Cadena con los nombres de privilegios separados por '|',
             o cadena vacía si no se puede obtener.
    """
    try:
        hproc = win32api.OpenProcess(
            win32con.PROCESS_QUERY_INFORMATION, False, pid
        )
        htok  = win32security.OpenProcessToken(hproc, win32con.TOKEN_QUERY)
        privs = win32security.GetTokenInformation(
            htok, win32security.TokenPrivileges
        )
        privileges = ''
        for priv_id, flags in privs:
            if flags == (win32security.SE_PRIVILEGE_ENABLED |
                         win32security.SE_PRIVILEGE_ENABLED_BY_DEFAULT):
                privileges += f'{win32security.LookupPrivilegeName(None, priv_id)}|'
    except Exception:
        # FIX: recursión infinita eliminada
        #      Antes: `privileges = get_process_privileges(pid)` → StackOverflow
        #      Corregido: simplemente devolver cadena vacía cuando falla
        privileges = ''

    return privileges


def monitor():
    """
    Bucle principal: espera eventos de creación de procesos mediante WMI
    y registra en CSV la información de cada nuevo proceso.
    """
    head = 'CommandLine, Time, Executable, Parent PID, PID, User, Privileges'
    log_to_file(head)

    c = wmi.WMI()
    process_watcher = c.Win32_Process.watch_for('creation')

    while True:
        try:
            new_process = process_watcher()
            cmdline     = new_process.CommandLine
            create_date = new_process.CreationDate
            executable  = new_process.ExecutablePath   # FIX: `exectutable` → `executable`
            parent_pid  = new_process.ParentProcessId
            pid         = new_process.ProcessId
            proc_owner  = new_process.GetOwner()

            privileges  = 'N/A'                        # FIX: `'N\A'` → `'N/A'`
            try:
                privileges = get_process_privileges(pid)
            except Exception:
                pass

            process_log_message = (
                f'{cmdline} , {create_date} , {executable} ,'   # FIX: variable corregida
                f'{parent_pid} , {pid} , {proc_owner} , {privileges}'
            )
            print(process_log_message)
            print()
            log_to_file(process_log_message)

        except Exception:
            pass


if __name__ == '__main__':
    monitor()
