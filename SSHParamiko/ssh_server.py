"""
ssh_server.py - Servidor SSH embebido con Paramiko
====================================================
Levanta un servidor SSH mínimo que autentica por usuario/contraseña
y permite enviarle comandos desde la consola del operador.
Diseñado para usarse junto a ssh_rcmd.py (cliente inverso).

REQUISITOS:
    pip install paramiko
    # Generar clave RSA para el servidor (una sola vez):
    ssh-keygen -t rsa -b 2048 -f test_rsa.key -N ""

EJEMPLOS DE EJECUCIÓN:
    # Servidor en 0.0.0.0:2222 (evitar puerto 22 sin root):
    python ssh_server.py 0.0.0.0 2222

    # Conectar con el cliente inverso desde otra máquina:
    python ssh_rcmd.py  # → IP del servidor, puerto 2222, usuario/clave de abajo
"""

import os
import paramiko
import socket
import sys
import threading

CWD     = os.path.dirname(os.path.realpath(__file__))
HostKey = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

# -------------------------------------------------------------------
# Credenciales del servidor SSH de prueba
# Personalizar antes de desplegar en un entorno de lab.
# -------------------------------------------------------------------
SSH_USER = os.environ.get('SSH_USER', 'usuario_lab')
SSH_PASS = os.environ.get('SSH_PASS', 'contraseña_lab')


class Server(paramiko.ServerInterface):
    """Interfaz de servidor SSH: gestiona autenticación y apertura de canales."""

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username: str, password: str) -> int:
        if username == SSH_USER and password == SSH_PASS:
            return paramiko.AUTH_SUCCESSFUL
        # FIX: faltaba el return en caso negativo
        return paramiko.AUTH_FAILED


if __name__ == '__main__':
    server_ip   = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    server_port = int(sys.argv[2]) if len(sys.argv) > 2 else 2222

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server_ip, server_port))
        sock.listen(100)
        print(f'[+] Listening for connections on {server_ip}:{server_port}…')
        client, addr = sock.accept()
    except Exception as e:
        print(f'[-] Listen failed: {e}')
        sys.exit(1)

    print(f'[+] Got a connection from {addr}')

    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HostKey)
    server = Server()
    bhSession.start_server(server=server)

    chan = bhSession.accept(20)
    if chan is None:
        print('[-] No channel established.')
        sys.exit(1)

    print('[+] Authenticated!')
    print(chan.recv(1024).decode())
    chan.send(b'Welcome to bh_ssh')

    try:
        while True:
            command = input("Enter command (or 'exit'): ")
            if command.strip() == 'exit':
                chan.send(b'exit')
                print('[*] Closing session.')
                bhSession.close()
                break
            chan.send(command.encode())
            r = chan.recv(8192)
            print(r.decode())
    except KeyboardInterrupt:
        bhSession.close()
