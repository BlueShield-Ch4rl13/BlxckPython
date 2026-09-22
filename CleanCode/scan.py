"""
scan.py - Esqueleto de escáner basado en lxml y subprocess
============================================================
Plantilla base para un escáner de red que:
  1. Resuelve el nombre de máquina a IP con nmap (mediante subprocess).
  2. Parsea resultados XML de nmap con lxml.etree.

REQUISITOS:
    pip install lxml
    sudo apt install nmap  (para la funcionalidad completa)

EJEMPLOS DE EJECUCIÓN:
    python scan.py
    # → imprime la IP de 'scanme.nmap.org' y lanza el escáner.
"""

from lxml import etree
from subprocess import Popen, PIPE

import argparse
import os
import socket


def get_ip(machine_name: str) -> str:
    """
    Resuelve un nombre de host a su dirección IP.

    Args:
        machine_name (str): Nombre de dominio o hostname.
    Returns:
        str: Dirección IP o mensaje de error.
    """
    try:
        return socket.gethostbyname(machine_name)
    except socket.gaierror as e:
        return f"Error resolviendo {machine_name}: {e}"


class Scan:
    """
    Escáner de red básico. Lanza nmap y parsea el XML resultante.
    """

    def __init__(self, target: str = "scanme.nmap.org"):
        self.target = target
        self.ip = get_ip(target)
        self.results = []

    def run(self):
        """
        Ejecuta nmap contra el objetivo y parsea la salida XML.
        Requiere nmap instalado en el sistema.
        """
        print(f"[*] Objetivo: {self.target} ({self.ip})")
        cmd = ["nmap", "-oX", "-", self.ip]
        try:
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()
            if stderr:
                print(f"[!] nmap stderr: {stderr.decode()}")
            root = etree.fromstring(stdout)
            for host in root.findall(".//host"):
                addr = host.find("address")
                if addr is not None:
                    self.results.append(addr.get("addr"))
                    print(f"[+] Host encontrado: {addr.get('addr')}")
        except FileNotFoundError:
            print("[!] nmap no está instalado. Instala con: sudo apt install nmap")
        return self.results


if __name__ == '__main__':
    scan = Scan(target="scanme.nmap.org")
    scan.run()
