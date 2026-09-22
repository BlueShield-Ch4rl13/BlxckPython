"""
rforward.py - Túnel SSH inverso (Remote Port Forwarding)
=========================================================
Abre un túnel SSH inverso: el puerto remoto del servidor SSH se redirige
al host:puerto local especificado. Útil para exponer servicios internos
a través de un servidor SSH accesible desde fuera.

Flujo:
  [Cliente externo] → [SSH server:remote_port] → [este script] → [local_host:local_port]

ERRORES CORREGIDOS:
    1. `from tabnanny import verbose` → importación errónea; `tabnanny.verbose`
       es un int, no una función. Se define una función verbose() local.
    2. `from socket import socket` → importaba la CLASE directamente.
       Luego `sock = socket.socket()` falla (no existe atributo .socket en la clase).
       Corregido: `import socket` y usar `socket.socket()`.
    3. Faltaba la función `parse_arguments()` completamente. Se implementa.
    4. `thr.setDaemon(True)` → deprecado en Python 3.10+. Usar `thr.daemon = True`.

REQUISITOS:
    pip install paramiko

EJEMPLOS DE EJECUCIÓN:
    # Exponer el puerto local 8080 como puerto 8080 en el servidor SSH:
    python rforward.py -p 8080 -r localhost:8080 usuario@servidor-ssh.com

    # Con clave privada:
    python rforward.py -p 8080 -r localhost:8080 -K ~/.ssh/id_rsa usuario@servidor.com

    # Con contraseña:
    python rforward.py -p 8080 -r localhost:8080 --readpass usuario@servidor.com
"""

import getpass
import paramiko
import select
import socket   # FIX: importar el módulo completo, no la clase
import sys
import threading

from optparse import OptionParser


def verbose(message: str) -> None:
    """
    Imprime mensajes de depuración en stderr.
    FIX: antes se importaba tabnanny.verbose (un int) en lugar de definir
    una función propia.
    """
    print(message, file=sys.stderr)


def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.

    Returns:
        tuple: (options, (ssh_host, ssh_port), (remote_host, remote_port, local_port))
    FIX: función ausente en el original — causaba NameError al llamar a main().
    """
    usage = "usage: %prog [options] <usuario@servidor-ssh> <host_remoto:puerto_local>"
    parser = OptionParser(usage=usage)
    parser.add_option('-p', '--remote-port', dest='port', type='int',
                      help='Puerto a abrir en el servidor remoto SSH')
    parser.add_option('-u', '--username', dest='username',
                      help='Usuario SSH (si no va incluido en la dirección del servidor)')
    parser.add_option('-K', '--key', dest='keyfile', default=None,
                      help='Ruta a la clave privada SSH')
    parser.add_option('', '--no-key', dest='look_for_keys', default=True,
                      action='store_false', help='No buscar claves SSH')
    parser.add_option('-P', '--readpass', dest='readpass', default=False,
                      action='store_true', help='Solicitar contraseña SSH')

    options, args = parser.parse_args()

    if len(args) < 1:
        parser.error("Debes indicar al menos el servidor SSH (usuario@host[:puerto]).")

    # Parsear servidor SSH
    ssh_address = args[0]
    if '@' in ssh_address:
        options.username, ssh_host = ssh_address.split('@', 1)
    else:
        ssh_host = ssh_address

    ssh_port = 22
    if ':' in ssh_host:
        ssh_host, ssh_port = ssh_host.rsplit(':', 1)
        ssh_port = int(ssh_port)

    # Parsear host remoto y puerto local
    if len(args) < 2:
        parser.error("Debes indicar host_remoto:puerto_local.")
    remote_spec = args[1]
    remote_host, local_port = remote_spec.rsplit(':', 1)
    local_port = int(local_port)

    if options.port is None:
        parser.error("Debes especificar el puerto remoto con -p.")

    return options, (ssh_host, ssh_port), (options.port, remote_host, local_port)


def reverse_forward_tunnel(server_port: int, remote_host: str,
                           remote_port: int, transport: paramiko.Transport):
    """
    Solicita el reenvío de puerto en el servidor SSH y gestiona los canales.
    """
    transport.request_port_forward('', server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(target=handler, args=(chan, remote_host, remote_port))
        thr.daemon = True   # FIX: setDaemon(True) está deprecado
        thr.start()


def handler(chan: paramiko.Channel, host: str, port: int):
    """
    Relay bidireccional entre el canal SSH y el socket local.
    """
    # FIX: `socket.socket()` — antes se importaba la clase directamente
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        verbose(f'Forwarding to {host}:{port} failed: {e}')
        return

    verbose(f'Tunnel open: {chan.origin_addr!r} → {chan.getpeername()!r} → ({host}:{port})')

    while True:
        r, _, _ = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if not data:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if not data:
                break
            sock.send(data)

    chan.close()
    sock.close()
    verbose(f'Tunnel closed from {chan.origin_addr!r}')


def main():
    options, server, remote = parse_arguments()

    password = None
    if options.readpass:
        password = getpass.getpass("Enter SSH password: ")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    verbose(f'[*] Connecting to {server[0]}:{server[1]}…')
    try:
        client.connect(
            server[0], server[1],
            username=options.username,
            key_filename=options.keyfile,
            look_for_keys=options.look_for_keys,
            password=password
        )
    except Exception as e:
        print(f'[-] Failed to connect to {server[0]}:{server[1]}: {e}')
        sys.exit(1)

    verbose(f'Forwarding remote port {remote[0]} → {remote[1]}:{remote[2]}')

    try:
        reverse_forward_tunnel(remote[0], remote[1], remote[2], client.get_transport())
    except KeyboardInterrupt:
        print('C-c: Port forwarding stopped.')
        sys.exit(0)


if __name__ == '__main__':
    main()
