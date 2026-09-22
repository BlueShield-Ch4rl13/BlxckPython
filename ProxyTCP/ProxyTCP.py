"""
ProxyTCP.py - Proxy TCP con hexdump
=====================================
Actúa como intermediario entre un cliente y un servidor remoto,
volcando en consola el tráfico (en hexadecimal y ASCII) en ambas
direcciones. Permite modificar los buffers antes del reenvío
editando las funciones request_handler / response_handler.

REQUISITOS:
    pip install (ninguno adicional; solo biblioteca estándar)

EJEMPLOS DE EJECUCIÓN:
    # Redirigir localhost:9000 → 10.0.0.1:9000 recibiendo primero la respuesta:
    python ProxyTCP.py 127.0.0.1 9000 10.0.0.1 9000 True

    # Redirigir localhost:2121 → ftp.ejemplo.com:21:
    python ProxyTCP.py 127.0.0.1 2121 ftp.ejemplo.com 21 True
"""

import sys
import socket
import threading

# -------------------------------------------------------------------
# Tabla de caracteres imprimibles para el hexdump
# -------------------------------------------------------------------
HEX_FILTER = ''.join([chr(i) if len(repr(chr(i))) == 3 else '.' for i in range(256)])


def hexdump(src, length=16, show=True):
    """
    Imprime (o devuelve) un volcado hexadecimal + ASCII de src.

    Args:
        src    (bytes | str): Datos a volcar.
        length (int)        : Bytes por línea.
        show   (bool)       : Si True imprime; si False devuelve la lista.
    """
    if isinstance(src, bytes):
        src = src.decode(errors='replace')
    results = []

    for i in range(0, len(src), length):
        word = str(src[i:i + length])
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f"{ord(c):02X}" for c in word])
        hexwidth = length * 3
        results.append(f"{i:04x}   {hexa:<{hexwidth}}   {printable}")

    if show:
        for line in results:
            print(line)
    else:
        return results


def receive_from(connection):
    """
    Lee datos de un socket hasta timeout o cierre de conexión.

    Args:
        connection (socket): Socket del que leer.
    Returns:
        bytes: Datos acumulados.
    """
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception:
        pass
    return buffer


def request_handler(buffer):
    """
    Punto de extensión para modificar peticiones del cliente antes
    de reenviarlas al servidor remoto. Edita aquí para inyectar
    o filtrar bytes.
    """
    return buffer


def response_handler(buffer):
    """
    Punto de extensión para modificar respuestas del servidor antes
    de enviarlas al cliente local. Edita aquí para analizar o alterar.
    """
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    """
    Hilo que gestiona el relay bidireccional entre cliente y servidor.

    Args:
        client_socket (socket): Socket del cliente conectado al proxy.
        remote_host   (str)   : Host remoto al que conectar.
        remote_port   (int)   : Puerto del host remoto.
        receive_first (bool)  : Si True, lee del remoto antes de enviar.
    """
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        if remote_buffer:
            print(f"[<==] Sending {len(remote_buffer)} bytes to localhost.")
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if local_buffer:
            print(f"[==>] Received {len(local_buffer)} bytes from localhost.")
            print("-" * 50)   # FIX: era `print(line)` → variable no definida
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if remote_buffer:
            print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not local_buffer and not remote_buffer:
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    """
    Bucle principal del proxy: enlaza, escucha y lanza hilos por conexión.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"[!!] Failed to bind on {local_host}:{local_port} → {e}")
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print(f"[==>] Incoming connection from {addr[0]}:{addr[1]}")
        print("-" * 50)   # FIX: era `print(line)` → variable no definida
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first)
        )
        proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print("Uso: python ProxyTCP.py [localhost] [localport] "
              "[remotehost] [remoteport] [receive_first]")
        print("Ejemplo: python ProxyTCP.py 127.0.0.1 9000 10.0.0.1 9000 True")
        sys.exit(0)

    local_host  = sys.argv[1]
    local_port  = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5].strip().lower() == "true"

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


# FIX: el bloque estaba indentado dentro de main() → nunca se ejecutaba
if __name__ == "__main__":
    main()
