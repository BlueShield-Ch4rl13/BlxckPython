"""
ssh_cmd.py - Ejecución remota de comandos SSH con Paramiko
===========================================================
Conecta a un servidor SSH usando usuario/contraseña y ejecuta
un comando, mostrando su salida estándar y de error.

ERRORES CORREGIDOS:
    1. Firma de función inconsistente con la llamada:
       - Definición : execute_ssh_command(hostname, username, password, cmd)  → 4 parámetros
       - Llamada    : execute_ssh_command(ip, port, username, password, cmd)  → 5 parámetros
       Se añade `port` a la firma de la función para que coincida con la llamada.

REQUISITOS:
    pip install paramiko

EJEMPLOS DE EJECUCIÓN:
    python ssh_cmd.py
    # → solicita usuario, contraseña, IP, puerto y comando.

    # Directo desde código (importando el módulo):
    from ssh_cmd import execute_ssh_command
    execute_ssh_command('192.168.1.10', 22, 'admin', 'contraseña', 'id')
"""

import getpass
import paramiko


def execute_ssh_command(hostname: str, port: int, username: str,
                        password: str, cmd: str) -> None:
    """
    Conecta por SSH y ejecuta un comando, imprimiendo la salida.

    Args:
        hostname (str): IP o nombre del host SSH.
        port     (int): Puerto SSH (habitualmente 22).
        username (str): Nombre de usuario.
        password (str): Contraseña del usuario.
        cmd      (str): Comando a ejecutar remotamente.
    """
    client = paramiko.SSHClient()
    # Acepta automáticamente la clave del host (útil en lab; en producción
    # usar client.load_system_host_keys() o RejectPolicy)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=username, password=password)

    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()

    if output:
        print('--- OUTPUT ---')
        for line in output:
            print(line.strip())

    client.close()


if __name__ == "__main__":
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    ip       = input("Enter IP address: ")
    port     = int(input("Enter port [22]: ") or 22)
    cmd      = input("Enter command to execute [id]: ") or "id"

    # FIX: se añadió `port` como segundo argumento (firma corregida)
    execute_ssh_command(ip, port, username, password, cmd)
