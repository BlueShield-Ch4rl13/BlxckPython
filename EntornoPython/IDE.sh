#!/usr/bin/env bash
# IDE.sh - Configuración del entorno de desarrollo Python en Linux (Debian/Ubuntu)
# =================================================================================
# Actualiza el sistema, instala Python 3 con entornos virtuales, lxml y
# Visual Studio Code. Crea un directorio de proyecto con su venv.

# --- Actualizar sistema ---
sudo apt update
apt list --upgradable
sudo apt upgrade
sudo apt dist-upgrade
sudo apt autoremove

# --- Instalar Python 3 y herramientas ---
sudo apt-get install python3
sudo apt-get upgrade python3
sudo apt-get install python3-venv

# --- Instalar lxml (requiere dependencias del sistema) ---
pip install lxml

# --- Instalar Visual Studio Code ---
sudo apt-get install code
# Alternativa si se descargó el .deb manualmente:
# sudo apt-get install ./code*.deb

# --- Crear directorio de proyecto y entorno virtual ---
mkdir mi_proyecto
cd mi_proyecto

python3 -m venv venv3
source venv3/bin/activate

# Verificar que lxml está disponible en el venv:
# python -c "from lxml import etree; print('lxml OK')"
