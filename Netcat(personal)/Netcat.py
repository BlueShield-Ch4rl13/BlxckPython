"""
Netcat.py - Netcat personalizado en Python 3
=============================================
Herramienta de red multiuso que replica funcionalidades básicas de netcat:
  - Escucha en modo servidor (-l)
  - Ejecuta un comando único al recibir conexión (-e)
  - Ofrece una shell interactiva (-c)
  - Recibe y guarda un archivo (-u NOMBRE_ARCHIVO)
  - Envía datos al servidor (modo cliente, sin flags)

REQUISITOS:
    - Python 3.x
    - Módulos estándar: argparse, socket, shlex, subprocess, threading

EJEMPLOS DE EJECUCIÓN:
    # Modo shell inversa en servidor (escuchar en 0.0.0.0:9999):
    python Netcat.py -t 0.0.0.0 -p 9999 -l -c

    # Ejecutar un comando al conectar:
    python Netcat.py -t 0.0.0.0 -p 9999 -l -e "cat /etc/hostname"

    # Subir un archivo al servidor:
    python Netcat.py -t 0.0.0.0 -p 9999 -l -u output.txt

    # Conectar como cliente y enviar texto:
    echo 'Hola Servidor' | python Netcat.py -t 127.0.0.1 -p 9999

    # Conectar como cliente de forma interactiva:
    python Netcat.py -t 127.0.0.1 -p 9999
"""

import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    """Ejecuta un comando de shell y devuelve su salida como string."""
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()


class Netcat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        """Decide si escuchar (servidor) o conectar (cliente)."""
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        """Modo cliente: conecta y permite intercambio interactivo."""
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            while True:
                recv_len = 1
                response = ''

                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break

                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())

        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listen(self):
        """Modo servidor: acepta conexiones y las delega a hilos."""
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def handle(self, client_socket):
        """Gestiona una conexión según el modo seleccionado."""
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break

            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)

            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while b'\n' not in cmd_buffer:
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'Server killed {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Ejemplo:
            netcat.py -t 192.168.1.100 -p 9999 -l -c          # shell inversa
            netcat.py -t 192.168.1.100 -p 9999 -l -u=test.txt # subir archivo
            netcat.py -t 192.168.1.100 -p 9999 -l -e="id"     # ejecutar comando
            echo "ABC" | python netcat.py -t 192.168.1.100 -p 9999  # enviar texto
            netcat.py -t 192.168.1.100 -p 9999                # conectar al servidor
        '''))
    parser.add_argument('-c', '--command', action='store_true', help='shell interactiva')
    parser.add_argument('-e', '--execute', help='comando a ejecutar')
    parser.add_argument('-l', '--listen', action='store_true', help='modo escucha')
    parser.add_argument('-p', '--port', type=int, default=9999, help='puerto')
    parser.add_argument('-t', '--target', default='0.0.0.0', help='host destino')
    parser.add_argument('-u', '--upload', help='nombre de archivo a guardar')
    args = parser.parse_args()

    # En modo cliente leemos stdin; en modo servidor empezamos vacíos
    if args.listen:
        buffer = b''
    else:
        buffer = sys.stdin.buffer.read()

    nc = Netcat(args, buffer)
    nc.run()
