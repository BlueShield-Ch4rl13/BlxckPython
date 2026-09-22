#!/usr/bin/env bash
# DfirOff.sh - Configuración de entorno Volatility 3 para análisis forense
# =========================================================================
# Instrucciones de instalación y comandos de uso de Volatility 3.
# Los nombres de fichero .vmem son ejemplos genéricos; sustituir por
# los de tu laboratorio.

# --- Instalación ---
python3 -m venv vol3
# En Linux:  source vol3/bin/activate
# En Windows: vol3/Scripts/Activate.ps1
cd vol3
git clone https://github.com/volatilityfoundation/volatility3.git
cd volatility3/
python setup.py install
pip install pycryptodome

# Verificar instalación
python vol.py --help
cd volatility/framework/plugins/windows/
ls

# --- Reconocimiento general ---
# vol -f imagen.vmem windows.info
# vol -f imagen.vmem windows.registry.printkey --key 'ControlSet001\Services'

# --- Reconocimiento de usuario ---
# vol -f imagen.vmem windows.cmdline
# vol -f imagen.vmem windows.pslist
# vol -f imagen.vmem windows.pstree
# vol -f imagen.vmem windows.hashdump

# --- Detección de anomalías ---
# vol -f imagen.vmem windows.malfind
# vol -f imagen.vmem windows.netscan

# --- Interfaz interactiva volshell ---
# volshell -w -f imagen.vmem
# from volatility.plugins.windows import pslist
# dpo(pslist.Pslist, primary=self.current_layer, nt_symbols=self.config['nt_symbols'])

# --- Plugin personalizado: ver DfirOff/aslrcheck.py ---
