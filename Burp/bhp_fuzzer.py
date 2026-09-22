"""
bhp_fuzzer.py - Extensión Burp Suite: generador de payloads fuzzer
===================================================================
Extensión para Burp Suite (Jython) que registra un generador de payloads
personalizado para el módulo Intruder. En cada iteración muta el payload
original insertando comillas simples (SQLi), scripts XSS o repeticiones
aleatorias de fragmentos del payload.

Implementa las interfaces:
  - IIntruderPayloadGeneratorFactory → registra el generador en Intruder.
  - IIntruderPayloadGenerator        → produce los payloads mutados.

ERRORES CORREGIDOS:
    1. `from burp import IintruderPayloadGeneratorFactory` → nombre incorrecto
       (la 'I' inicial debe ir seguida de mayúsculas). Corregido a
       `IIntruderPayloadGeneratorFactory`.
    2. `from burp import IintruderPayloadGenerator` → mismo problema.
       Corregido a `IIntruderPayloadGenerator`.
    3. `class BurpExtender(IBurpExtender, IintruderPayloadGeneratorFactory)` →
       usa el nombre mal escrito. Corregido.
    4. `class BHPFuzzer(IintruderPayloadGenerator)` → ídem. Corregido.

REQUISITOS:
    - Burp Suite con soporte Jython

EJEMPLOS DE EJECUCIÓN:
    Cargar en Burp: Extender → Extensions → Add → Extension Type: Python → bhp_fuzzer.py
    Luego en Intruder → Payloads → Payload Type: Extension-generated → BHP Payload Generator
"""

import random

from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory   # FIX: 'Iintruder...' → 'IIntruder...'
from burp import IIntruderPayloadGenerator          # FIX: ídem

from java.util import List, ArrayList


class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):  # FIX: nombre corregido

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        callbacks.registerIntruderPayloadGeneratorFactory(self)
        return

    def getGeneratorName(self):
        """Nombre que aparece en la lista de Payload Types de Intruder."""
        return "BHP Payload Generator"

    def createNewInstance(self, attack):
        """Crea una nueva instancia del generador para cada ataque."""
        return BHPFuzzer(self, attack)


class BHPFuzzer(IIntruderPayloadGenerator):  # FIX: nombre corregido

    def __init__(self, extender, attack):
        self._extender       = extender
        self._helpers        = extender._helpers
        self._attack         = attack
        self.max_payloads    = 10   # Número máximo de payloads a generar
        self.num_iterations  = 0
        return

    def hasMorePayloads(self):
        """Indica a Intruder si quedan payloads por generar."""
        return self.num_iterations < self.max_payloads

    def getNextPayload(self, current_payloads):
        """
        Genera el siguiente payload mutado a partir del payload actual.

        Args:
            current_payloads: Bytes del payload actual de Intruder.

        Returns:
            str: Payload mutado.
        """
        # Convertir bytes a string (cada byte al carácter correspondiente)
        payload = "".join(chr(x) for x in current_payloads)
        payload = self.mutate_payload(payload)
        self.num_iterations += 1
        return payload

    def reset(self):
        """Reinicia el contador para un nuevo ataque."""
        self.num_iterations = 0
        return

    def mutate_payload(self, original_payload):
        """
        Aplica una mutación aleatoria al payload:
          1 → inyección SQL básica (comilla simple)
          2 → inyección XSS básica (script alert)
          3 → repetición de fragmento aleatorio del payload

        Args:
            original_payload (str): Payload original de Intruder.

        Returns:
            str: Payload mutado.
        """
        picker = random.randint(1, 3)
        offset = random.randint(0, len(original_payload) - 1)
        front, back = original_payload[:offset], original_payload[offset:]

        if picker == 1:
            # SQLi: insertar comilla simple en posición aleatoria
            front += "'"
        elif picker == 2:
            # XSS: insertar script de alerta
            front += "<script>alert('H4CKED');</script>"
        elif picker == 3:
            # Repetición: insertar un fragmento del payload varias veces
            chunk_length = random.randint(0, len(back) - 1)
            repeater     = random.randint(1, 10)
            for _ in range(repeater):
                front += original_payload[:offset + chunk_length]

        return front + back
