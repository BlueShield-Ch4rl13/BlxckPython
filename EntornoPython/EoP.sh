#!/usr/bin/env bash
# EoP.sh - Compilación e instalación del servicio Windows vulnerable (bhservice)
# ===============================================================================
# Instala las dependencias, empaqueta bhservice.py como ejecutable standalone
# con PyInstaller y gestiona el ciclo de vida del servicio.

# --- Instalar dependencias ---
pip install pywin32 wmi pyinstaller

# --- Compilar como ejecutable Windows (.exe) ---
# --hiddenimport win32timezone: necesario porque pyinstaller no detecta
# automáticamente este módulo usado internamente por pywin32.
pyinstaller -F --hiddenimport win32timezone EoPWIN/bhservice.py

# --- Gestión del servicio (ejecutar como Administrador) ---
# dist/bhservice.exe install   # Registrar el servicio en Windows
# dist/bhservice.exe start     # Iniciar el servicio
# dist/bhservice.exe stop      # Detener el servicio
# dist/bhservice.exe remove    # Desinstalar el servicio
