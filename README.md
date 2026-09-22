# bl4ckpython — Toolkit de Python para Hacking Ético y Ciberseguridad

> **Versión documentada.**  
> Se ha añadido documentación exhaustiva y se han eliminado todos los datos personales (URLs, credenciales, rutas, nombres de usuario).

---

## Índice de carpetas

| Carpeta | Descripción |
|---|---|
| [Redes](#redes) | Clientes y servidores TCP/UDP con sockets |
| [Netcat(personal)](#netcatpersonal) | Netcat minimalista en Python puro |
| [ProxyTCP](#proxytcp) | Proxy TCP con volcado hexadecimal |
| [CleanCode](#cleancode) | Escáner de puertos con nmap y Python limpio |
| [SnifferRed](#snifferred) | Sniffers de red con sockets raw e ICMP |
| [ScanMail](#scanmail) | Sniffer de correo con filtros BPF y ARP poisoning |
| [SSHParamiko](#sshparamiko) | Cliente/servidor SSH con Paramiko |
| [SSH](#ssh) | Túnel SSH inverso (remote port forwarding) |
| [HxckWeb](#hxckweb) | Peticiones HTTP, scraping, brute-force web |
| [Exfiltracion](#exfiltracion) | Cifrado híbrido y exfiltración de datos |
| [Modulos](#modulos) | Módulos auxiliares del troyano (dirlister, environment, IP) |
| [PCAP](#pcap) | Análisis de capturas de red y detección facial |
| [Burp](#burp) | Extensiones Jython para Burp Suite |
| [C2](#c2) | Troyano con canal de C2 en GitHub |
| [EoPWIN](#eopwin) | Escalada de privilegios en Windows |
| [TroyanWIN](#troyanwin) | Troyano Windows: keylogger, sandbox detect, shellcode |
| [DfirOff](#dfiroff) | Plugin Volatility 3 para detección de ASLR |
| [EntornoPython](#entornopython) | Scripts de instalación del entorno |

---

## Redes

**Archivos:** `ClientTCP.py`, `ClientUDP.py`, `SrvTCP.py`

Implementaciones básicas de comunicación en red usando el módulo `socket` de Python.

- **ClientTCP.py** — cliente TCP que conecta a un host:puerto y recibe datos hasta que la conexión se cierra. 
- **ClientUDP.py** — cliente UDP que envía un datagrama y espera respuesta. Sin errores en el original.
- **SrvTCP.py** — servidor TCP con soporte multihilo para conexiones concurrentes. Sin errores en el original.

```bash
python Redes/ClientTCP.py
python Redes/SrvTCP.py
```

---

## Netcat(personal)

**Archivo:** `Netcat.py`

Reimplementación de Netcat en Python 3: modo cliente (conectar), modo escucha (`-l`), ejecución de comandos (`-e`), subida de ficheros (`-u`) y shell interactiva.

```bash
python "Netcat(personal)/Netcat.py" -t 0.0.0.0 -p 4444 -l -c    # escucha con shell
python "Netcat(personal)/Netcat.py" -t 192.168.1.1 -p 4444       # conectar
```

---

## ProxyTCP

**Archivo:** `ProxyTCP.py`

Proxy TCP que retransmite tráfico entre un cliente y un servidor destino, mostrando los datos en hexadecimal y ASCII.

```bash
python ProxyTCP/ProxyTCP.py 127.0.0.1 9000 192.168.1.10 80 True
```

---

## CleanCode

**Archivo:** `scan.py`

Escáner de puertos con interfaz orientada a objetos y nmap. Muestra el estado de los puertos de un host dado.

```bash
python CleanCode/scan.py
```

---

## SnifferRed

**Archivos:** `sniffer.py`, `sniffer_ip_header_decode.py`, `sniffer_with_icmp.py`, `scanner.py`

Sniffers de red usando sockets raw (`AF_INET`, `SOCK_RAW`). Parsean cabeceras IPv4 e ICMP para mostrar el tráfico en tiempo real.

- **sniffer.py** — sniffer básico con parámetro de host.
- **sniffer_ip_header_decode.py** — decodifica campos del cabecero IP.
- **sniffer_with_icmp.py** — añade decodificación del cabecero ICMP. *Reconstruido completamente* (fichero original truncado).
- **scanner.py** — envía paquetes UDP y detecta respuestas ICMP para mapear hosts activos.

```bash
sudo python SnifferRed/sniffer.py
sudo python SnifferRed/scanner.py 192.168.1.0/24
```

---

## ScanMail

**Archivos:** `BPF_sniffer.py`, `mail_sniffer.py`, `arper.py`

Herramientas de intercepción de correo en red local.

- **BPF_sniffer.py** / **mail_sniffer.py** — sniffers con filtros BPF para capturar tráfico SMTP/POP3/IMAP.  
- **arper.py** — envenenamiento ARP para realizar ataques MitM.  

```bash
sudo python ScanMail/arper.py <victim_ip> <gateway_ip> <interface>
```

---

## SSHParamiko

**Archivos:** `ssh_cmd.py`, `ssh_rcmd.py`, `ssh_server.py`

Clientes y servidor SSH usando la biblioteca Paramiko.

- **ssh_cmd.py** — ejecuta un comando remoto por SSH.  
- **ssh_rcmd.py** — reverse SSH: el servidor ejecuta comandos enviados por el cliente.  
- **ssh_server.py** — servidor SSH minimal con autenticación por contraseña (para lab).  

```bash
python SSHParamiko/ssh_cmd.py
SSH_USER=admin SSH_PWD=secreto python SSHParamiko/ssh_server.py
```

---

## SSH

**Archivo:** `rforward.py`

Túnel SSH inverso (remote port forwarding): expone un puerto local a través de un servidor SSH accesible desde el exterior.

```bash
python SSH/rforward.py -p 8080 -r localhost:8080 usuario@servidor-ssh.com
```

---

## HxckWeb

**Archivos:** `urllib2GET.py`, `urllib2POST.py`, `urllib3GET.py`, `urllib3CredencialPOST.py`, `BeautifulSoup.py`, `lxml.py`, `bruter.py`, `mapperWP.py`, `WP_killer.py`, `VictimaHTTP.html`

Scripts de interacción con aplicaciones web: peticiones HTTP, scraping y ataques de fuerza bruta.

| Archivo | Función | Correcciones |
|---|---|---|
| `urllib2GET.py` | GET con urllib | `import urllib2` → `import urllib.request` (Python 3) |
| `urllib2POST.py` | GET con User-Agent | Mismo fix Python 2→3 |
| `urllib3GET.py` | GET estándar | URL personal eliminada |
| `urllib3CredencialPOST.py` | POST con credenciales | Credenciales personales eliminadas |
| `BeautifulSoup.py` | Scraping de enlaces | `fin_all` → `find_all`; `'//a'` → `'a'` |
| `lxml.py` | Scraping con XPath | `etree.parser` → `etree.parse`; `finall` → `findall` |
| `bruter.py` | Fuerza bruta de directorios | `word.put()` → `words.put()` (Queue, no str) |
| `mapperWP.py` | Mapper de rutas WordPress | Ruta personal → variable de entorno |
| `WP_killer.py` | Brute-force login WP | `etree.parser`→`etree.parse`; `brute`→`passwd`; `url`→`TARGET` |
| `VictimaHTTP.html` | Formulario de ejemplo | URL personal eliminada |

```bash
pip install requests beautifulsoup4 lxml
TARGET=https://mi-lab.local python HxckWeb/bruter.py
```

---

## Exfiltracion

**Archivos:** `cryptor.py`, `email_exfil.py`, `exfil.py`, `paste_exfil.py`, `transmit_exfil.py`

Módulos de cifrado y exfiltración de datos desde el sistema objetivo.

- **cryptor.py** — cifrado híbrido AES-EAX + RSA-OAEP con compresión zlib.  
- **email_exfil.py** — exfiltración por SMTP / Outlook.  
- **paste_exfil.py** — exfiltración a Pastebin (API + IE).  
- **transmit_exfil.py** — FTP anónimo y socket con `win32file.TransmitFile`.  
- **exfil.py** — orquestador que busca documentos y los exfiltra por el canal elegido.

```bash
pip install pycryptodomex
python Exfiltracion/cryptor.py
```

---

## Modulos

**Archivos:** `ctypes.py`, `dirlister.py`, `environment.py`, `struct.py`

Módulos auxiliares diseñados para ser cargados dinámicamente por `C2/git_trojan.py`.

> ⚠️ Los ficheros `ctypes.py` y `struct.py` tienen el mismo nombre que módulos estándar de Python. No los importes como módulos desde otros scripts en el mismo directorio.

- **ctypes.py** — clase `IP` como `ctypes.Structure` mapeada sobre bytes raw del socket.
- **struct.py** — clase `IP` usando `struct.unpack` (Python puro, multiplataforma).
- **dirlister.py** — lista el directorio actual (`os.listdir`).
- **environment.py** — devuelve las variables de entorno (`os.environ`).

---

## PCAP

**Archivos:** `recapper.py`, `detector.py`

Análisis post-explotación de capturas de red.

- **recapper.py** — lee un PCAP con Scapy, reconstruye flujos HTTP y extrae imágenes.  
- **detector.py** — detecta caras en imágenes JPEG con el clasificador Haar de OpenCV.  

```bash
pip install scapy opencv-python
PCAPS=/ruta/pcaps OUTDIR=/tmp/imgs python PCAP/recapper.py
```

---

## Burp

**Archivos:** `bhp_bing.py`, `bhp_fuzzer.py`, `bhp_wordlist.py`

Extensiones para Burp Suite escritas en Python (Jython). Se cargan desde `Extender → Extensions → Add → Python`.

| Archivo | Función | Correcciones |
|---|---|---|
| `bhp_bing.py` | Búsqueda en Bing por IP/dominio | `IContexMenuFactory`→correcto; `JmenuItem`→`JMenuItem`; `thread`→`threading`; `0cp-Apim`→`Ocp-Apim`; `urllib.quote`→`urllib.parse.quote` |
| `bhp_fuzzer.py` | Generador de payloads mutados para Intruder | `IintruderPayloadGeneratorFactory/Generator` → capitalización correcta |
| `bhp_wordlist.py` | Extractor de wordlist desde respuestas HTTP | `IcontextMenuFactory`→correcto; `JmenuItem`→`JMenuItem`; `HTMLParser` Python 3; `__int__`→`__init__`; `capitaliza()`→`capitalize()`; `%S%S`→`%s%s` |

---

## C2

**Archivo:** `git_trojan.py`

Troyano que usa un repositorio privado de GitHub como canal de Comando y Control (C2): descarga módulos Python dinámicamente, los ejecuta y sube los resultados al repo.

```bash
pip install github3.py
echo "ghp_tutoken" > mytoken.txt
GITHUB_USER=tu_usuario python C2/git_trojan.py
```

---

## EoPWIN

**Archivos:** `bhservice.py`, `file_monitor.py`, `process_monitor.py`

Herramientas de escalada de privilegios (Elevation of Privilege) en Windows.

- **bhservice.py** — servicio Windows que ejecuta VBScripts periódicamente (vector de EoP si SRCDIR es escribible).  
- **file_monitor.py** — vigila directorios con `ReadDirectoryChangesW` y vuelca ficheros modificados.  
- **process_monitor.py** — registra nuevos procesos en CSV con sus privilegios.  

```bash
pip install pywin32 wmi
python EoPWIN/process_monitor.py
```

---

## TroyanWIN

**Archivos:** `keylogger.py`, `sandbox_detect.py`, `screenshotter.py`, `shell_exec.py`

Módulos de troyano para Windows.

- **keylogger.py** — registra pulsaciones de teclado y portapapeles con pyWinhook.  
- **sandbox_detect.py** — detecta entornos sandbox midiendo la interacción humana.  
- **screenshotter.py** — captura todos los monitores como BMP.  
- **shell_exec.py** — descarga y ejecuta shellcode en memoria (VirtualAlloc + ctypes).  

```bash
pip install pyWinhook pywin32 pythoncom
python TroyanWIN/sandbox_detect.py
```

---

## DfirOff

**Archivo:** `aslrcheck.py`

Plugin de Volatility 3 que detecta procesos en Windows con ASLR deshabilitado inspeccionando la cabecera PE de cada imagen ejecutable.

```bash
vol -f imagen.vmem -p DfirOff/ windows.aslrcheck.AslrCheck
```

---

## EntornoPython

**Archivos:** `Cifrar.sh`, `DfirOff.sh`, `EoP.sh`, `Git.sh`, `IDE.sh`, `Web.sh`

Scripts de instalación y configuración del entorno de desarrollo/laboratorio.

| Script | Propósito |
|---|---|
| `IDE.sh` | Actualiza el sistema e instala Python 3, venv, lxml y VS Code |
| `Web.sh` | Instala requests, lxml y beautifulsoup4 |
| `Cifrar.sh` | Instala pycryptodomex (corrección de typo `instañll`) |
| `DfirOff.sh` | Configura el entorno de Volatility 3 y lista comandos de uso |
| `EoP.sh` | Instala pywin32/wmi/pyinstaller y compila bhservice.py |
| `Git.sh` | Inicializa el repositorio C2 para git_trojan.py |

---

## Requisitos generales

```bash
# Red / sniffers
pip install scapy paramiko

# Web
pip install requests beautifulsoup4 lxml

# Cifrado / exfiltración
pip install pycryptodomex

# Windows (solo en Windows)
pip install pywin32 wmi pyinstaller pyWinhook

# C2
pip install github3.py

# PCAP / imagen
pip install scapy opencv-python

# Burp (Jython — instalar en Burp Suite)
# Descargar Jython standalone desde https://www.jython.org/
```

> **Nota legal:** Este toolkit está diseñado exclusivamente para entornos de laboratorio, CTFs y formación en ciberseguridad ofensiva. El uso de estas herramientas contra sistemas sin autorización explícita es ilegal.
