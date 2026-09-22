"""
SrvTCP.py - Servidor TCP multihilo
=====================================
Escucha conexiones TCP entrantes en 0.0.0.0:9999 y las atiende
en hilos independientes. Responde con un ACK a cada mensaje recibido.

REQUISITOS:
    - Python 3.x
    - Módulo estándar: socket, threading

EJEMPLOS DE EJECUCIÓN:
    # Terminal 1 - levantar el servidor:
    python SrvTCP.py

    # Terminal 2 - conectar con netcat:
    nc 127.0.0.1 9999
    # o con el cliente incluido:
    python ClientTCP.py
"""

import socket
import threading

IP = '0.0.0.0'    # Escucha en todas las interfaces
PORT = 9999


def main():
    """Crea el socket servidor, enlaza y entra en bucle de aceptación."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(5)  # Cola máxima de 5 conexiones pendientes
    print(f"[*] Listening on {IP}:{PORT}")

    while True:
        client, addr = server.accept()
        print(f'[*] Accepted connection from {addr[0]}:{addr[1]}')
        # Cada cliente en su propio hilo para no bloquear el bucle principal
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


def handle_client(client_socket):
    """Recibe un mensaje del cliente, lo imprime y responde con ACK."""
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')


if __name__ == '__main__':
    main()
