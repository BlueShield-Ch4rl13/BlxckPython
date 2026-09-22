"""
cryptor.py - Cifrado/descifrado híbrido AES + RSA
==================================================
Implementa cifrado híbrido: AES-EAX cifra el contenido (rápido para
datos grandes), RSA-OAEP cifra la clave de sesión AES (seguro para
el intercambio de claves). El resultado final se codifica en Base64.

Flujo de cifrado:
  plaintext → zlib.compress → AES-EAX → [RSA(session_key) | nonce | tag | ciphertext] → base64

Flujo de descifrado:
  base64 → split bytes → RSA.decrypt(session_key) → AES-EAX.decrypt → zlib.decompress

ERRORES CORREGIDOS:
    1. `from cryptodome.Cipher import AES` → módulo incorrecto (minúsculas).
       Corregido a `from Cryptodome.Cipher import AES` (mayúscula inicial).
    2. `ciphertext, tag = cipher_aes.encrypt_and_digest(compressed_text)` →
       variable `compressed_text` no definida. Corregido a `compressed`
       (nombre devuelto por zlib.compress).
    3. `RSA.importkey(key)` → método incorrecto.
       Corregido a `RSA.import_key(key)`.
    4. `open(f'key.{keytype}')` → modo texto. Las claves son bytes (PEM).
       Corregido a `open(f'key.{keytype}', 'rb')`.
    5. Bloque `if __name__ == '__main__':` duplicado → solo uno puede ejecutarse.
       Fusionados en un único bloque que genera claves y luego las usa.

REQUISITOS:
    pip install pycryptodomex   # o pycryptodome

EJEMPLOS DE EJECUCIÓN:
    python cryptor.py
    # Genera key.pri / key.pub y cifra/descifra el mensaje de prueba.
"""

from Cryptodome.Cipher import AES, PKCS1_OAEP   # FIX: mayúscula en 'Cryptodome'
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from io import BytesIO

import base64
import zlib


def generate():
    """
    Genera un par de claves RSA de 2048 bits y las guarda en
    key.pri (privada) y key.pub (pública) en el directorio actual.
    """
    new_key    = RSA.generate(2048)
    private_key = new_key.export_key()
    public_key  = new_key.publickey().export_key()

    with open('key.pri', 'wb') as f:
        f.write(private_key)
    with open('key.pub', 'wb') as f:
        f.write(public_key)


def get_rsa_cipher(keytype):
    """
    Carga la clave RSA del fichero key.<keytype> y devuelve
    el cifrador PKCS1-OAEP y el tamaño de la clave en bytes.

    Args:
        keytype (str): 'pub' para cifrar, 'pri' para descifrar.

    Returns:
        tuple: (PKCS1_OAEP cipher, int key_size_bytes)
    """
    # FIX: modo 'rb' — las claves PEM son bytes
    with open(f'key.{keytype}', 'rb') as f:
        key = f.read()
    # FIX: RSA.importkey → RSA.import_key (nombre correcto del método)
    rsakey = RSA.import_key(key)
    return (PKCS1_OAEP.new(rsakey), rsakey.size_in_bytes())


def encrypt(plaintext):
    """
    Cifra `plaintext` con AES-EAX (clave efímera) y cifra la clave
    AES con RSA-OAEP (clave pública). Devuelve el resultado en Base64.

    Args:
        plaintext (bytes): Datos a cifrar.

    Returns:
        bytes: Mensaje cifrado codificado en Base64.
    """
    compressed = zlib.compress(plaintext)  # comprimir antes de cifrar

    session_key = get_random_bytes(16)
    cipher_aes  = AES.new(session_key, AES.MODE_EAX)
    # FIX: `compressed_text` → `compressed` (nombre correcto de la variable)
    ciphertext, tag = cipher_aes.encrypt_and_digest(compressed)

    cipher_rsa, _         = get_rsa_cipher('pub')
    encrypted_session_key = cipher_rsa.encrypt(session_key)

    # Empaquetar: clave_RSA | nonce | tag | ciphertext
    msg_payload = encrypted_session_key + cipher_aes.nonce + tag + ciphertext
    return base64.b64encode(msg_payload)


def decrypt(encrypted):
    """
    Invierte el proceso: decodifica Base64, extrae los campos del
    mensaje, descifra la clave AES con la clave privada RSA y
    descifra el contenido con AES-EAX.

    Args:
        encrypted (bytes): Mensaje cifrado en Base64.

    Returns:
        bytes: Datos originales descifrados.
    """
    encrypted_bytes    = BytesIO(base64.decodebytes(encrypted))
    cipher_rsa, keysize = get_rsa_cipher('pri')

    encrypted_session_key = encrypted_bytes.read(keysize)
    nonce      = encrypted_bytes.read(16)
    tag        = encrypted_bytes.read(16)
    ciphertext = encrypted_bytes.read()

    session_key = cipher_rsa.decrypt(encrypted_session_key)
    cipher_aes  = AES.new(session_key, AES.MODE_EAX, nonce)
    decrypted   = cipher_aes.decrypt_and_verify(ciphertext, tag)

    return zlib.decompress(decrypted)


if __name__ == '__main__':
    # FIX: bloque duplicado fusionado en uno solo
    generate()                             # genera key.pri y key.pub

    plaintext = b'Hello, World!'
    encrypted = encrypt(plaintext)
    print('Cifrado:   ', encrypted)
    print('Descifrado:', decrypt(encrypted))
