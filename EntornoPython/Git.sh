#!/usr/bin/env bash
# Git.sh - Inicialización del repositorio C2 en GitHub para git_trojan.py
# ========================================================================
# Crea la estructura de directorios que git_trojan.py espera encontrar
# en el repositorio remoto:
#   config/   → ficheros JSON de configuración de tareas (<id>.json)
#   modules/  → módulos Python descargados dinámicamente
#   data/     → resultados subidos por cada instancia del troyano
#

mkdir bhptrojan
cd bhptrojan
git init
mkdir modules
mkdir config
mkdir data
touch .gitignore
git add .
git commit -m "Adds repo structure for trojan."

# Sustituir <tu_usuario> y <tu_repo> por los valores reales de tu laboratorio
# git remote add origin https://github.com/<tu_usuario>/<tu_repo>.git
# git push origin master
