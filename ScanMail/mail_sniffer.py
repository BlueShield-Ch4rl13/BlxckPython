"""
mail_sniffer.py - Sniffer básico de un paquete con scapy
=========================================================
Captura el primer paquete de red y muestra su estructura completa
usando scapy. Útil como punto de partida para inspección de protocolos.

ERRORES CORREGIDOS:
    1. `if __name__ == '__name__':` → `if __name__ == '__main__':`
    2. Indentación inconsistente en la función main().

REQUISITOS:
    pip install scapy
    Ejecutar con privilegios de root / administrador.

EJEMPLOS DE EJECUCIÓN:
    sudo python mail_sniffer.py
    # Captura UN paquete, lo muestra y termina.
"""

from scapy.all import sniff


def packet_callback(packet):
    """Muestra la disección completa de un paquete scapy."""
    print(packet.show())


def main():
    """Captura un único paquete de cualquier protocolo."""
    print("[*] Capturing one packet...")
    sniff(prn=packet_callback, count=1)


# FIX: era `if __name__ == '__name__':` → nunca ejecutaba main()
if __name__ == '__main__':
    main()
