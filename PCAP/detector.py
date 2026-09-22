"""
detector.py - Detección de caras en imágenes extraídas de PCAP
===============================================================
Recorre un directorio de imágenes JPEG, aplica el clasificador Haar
de OpenCV para detección de caras y guarda las imágenes con los
rectángulos marcados en el directorio de salida.

Combinado con recapper.py: primero se extraen las imágenes del PCAP
y luego detector.py las analiza en busca de rostros.

REQUISITOS:
    pip install opencv-python

EJEMPLOS DE EJECUCIÓN:
    # Con valores por defecto:
    python detector.py

    # Especificando rutas:
    PICTURES=/tmp/imgs FACES=/tmp/out TRAIN=/usr/share/opencv4/haarcascades python detector.py
"""

import os

import cv2

# -------------------------------------------------------------------
# Rutas de trabajo — configurables por variables de entorno
# -------------------------------------------------------------------
ROOT  = os.environ.get('PICTURES', '/root/Desktop/pictures')   # Directorio de imágenes de entrada
FACES = os.environ.get('FACES',    '/root/Desktop/faces')      # Directorio de salida (imágenes con caras)
TRAIN = os.environ.get('TRAIN',    '/root/Desktop/training')   # Directorio del modelo Haar XML


def detect(srcdir=ROOT, tgtdir=FACES, train_dir=TRAIN):
    """
    Detecta caras en imágenes JPEG del directorio `srcdir` usando el
    clasificador Haar de OpenCV y guarda los resultados en `tgtdir`.

    El clasificador `haarcascade_frontalface_alt.xml` debe encontrarse
    en `train_dir`. Se puede descargar del repositorio oficial de OpenCV.

    Args:
        srcdir    (str): Directorio con imágenes JPEG de entrada.
        tgtdir    (str): Directorio donde se guardan las imágenes procesadas.
        train_dir (str): Directorio que contiene el fichero XML del clasificador.
    """
    for fname in os.listdir(srcdir):
        if not fname.upper().endswith('.JPG'):
            continue

        fullname = os.path.join(srcdir, fname)
        newname  = os.path.join(tgtdir, fname)

        img = cv2.imread(fullname)
        if img is None:
            continue

        # Convertir a escala de grises (el clasificador Haar trabaja en gris)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        training = os.path.join(train_dir, 'haarcascade_frontalface_alt.xml')
        cascade  = cv2.CascadeClassifier(training)
        rects    = cascade.detectMultiScale(gray, 1.3, 5)

        try:
            if rects.any():
                print(f'Cara detectada en {fname}')
                # Convertir (x, y, w, h) → (x1, y1, x2, y2) para dibujar rectángulos
                rects[:, 2:] += rects[:, :2]
        # FIX: ArithmeticError → AttributeError
        # `rects` puede ser una tupla vacía () si no se detecta nada;
        # llamar a .any() sobre ella lanza AttributeError, no ArithmeticError.
        except AttributeError:
            print(f'Sin caras en {fname}.')
            continue

        # Dibujar rectángulos alrededor de cada cara detectada
        for x1, y1, x2, y2 in rects:
            cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)

        cv2.imwrite(newname, img)


if __name__ == '__main__':
    detect()
