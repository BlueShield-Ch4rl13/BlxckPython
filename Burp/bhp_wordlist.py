"""
bhp_wordlist.py - Extensión Burp Suite: generador de wordlist desde respuestas HTTP
====================================================================================
Extensión para Burp Suite (Jython) que extrae palabras de las respuestas HTTP
seleccionadas y genera una wordlist de contraseñas con variaciones de capitalización
y sufijos numéricos/especiales. Útil para ataques de diccionario personalizados.

Flujo:
  1. El usuario selecciona peticiones en la historia HTTP de Burp.
  2. "Create Wordlist" parsea las respuestas, elimina etiquetas HTML
     y extrae palabras únicas de hasta 12 caracteres.
  3. Para cada palabra se generan variantes (minúsculas, capitalizada)
     con sufijos comunes ("", "1", "!", año actual).
  4. La wordlist se imprime por la consola de Burp.

REQUISITOS:
    - Burp Suite con soporte Jython

EJEMPLOS DE EJECUCIÓN:
    Cargar en Burp: Extender → Extensions → Add → Extension Type: Python → bhp_wordlist.py
"""

import re
from datetime import datetime
from html.parser import HTMLParser  # FIX: Python 2 `HTMLParser` → Python 3 `html.parser`

from burp import IBurpExtender
from burp import IContextMenuFactory  # FIX: 'IcontextMenuFactory' → 'IContextMenuFactory'

from java.util    import ArrayList
from javax.swing  import JMenuItem    # FIX: 'JmenuItem' → 'JMenuItem'


class TagStripper(HTMLParser):
    """
    Parser HTML que extrae solo el texto visible de un documento,
    descartando etiquetas y retornando el contenido como cadena.
    """

    def __init__(self):  # FIX: `__int__` → `__init__`
        HTMLParser.__init__(self)
        self.page_text = []

    def handle_data(self, data):
        """Acumula el texto de los nodos de texto."""
        self.page_text.append(data)

    def handle_comment(self, data):
        """Acumula el texto de los comentarios HTML."""
        self.page_text.append(data)

    def strip(self, html):
        """
        Parsea `html` y devuelve el texto visible concatenado.

        Args:
            html (str): Documento HTML a procesar.

        Returns:
            str: Texto limpio sin etiquetas.
        """
        self.feed(html)
        return " ".join(self.page_text)


class BurpExtender(IBurpExtender, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self.context    = None
        self.hosts      = set()
        self.wordlist   = set(["Password"])  # Semilla inicial

        callbacks.setExtensionName("BHP Wordlist")
        callbacks.registerContextMenuFactory(self)
        return

    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list    = ArrayList()
        # FIX: JmenuItem → JMenuItem
        menu_list.add(JMenuItem("Create Wordlist", actionPerformed=self.wordlist_menu))
        return menu_list

    def wordlist_menu(self, event):
        """Callback del menú: procesa las respuestas seleccionadas."""
        http_traffic = self.context.getSelectedMessages()
        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            self.hosts.add(http_service.getHost())
            http_response = traffic.getResponse()
            if http_response:
                self.get_words(http_response)
        self.display_wordlist()
        return

    def get_words(self, http_response):
        """
        Extrae palabras de la respuesta HTTP (solo respuestas text/*).

        Args:
            http_response: Objeto de respuesta de Burp.
        """
        headers, body = http_response.tostring().split('\r\n\r\n', 1)

        # Ignorar respuestas que no sean texto
        if headers.lower().find("content-type: text") == -1:
            return

        tag_stripper = TagStripper()
        page_text    = tag_stripper.strip(body)
        words        = re.findall(r"[a-zA-Z]\w{2,}", page_text)

        for word in words:
            if len(word) <= 12:
                self.wordlist.add(word.lower())
        return

    def mangle(self, word):
        """
        Genera variantes de una palabra con capitalización y sufijos comunes.

        Args:
            word (str): Palabra base.

        Returns:
            list[str]: Lista de variantes generadas.
        """
        year     = datetime.now().year
        suffixes = ["", "1", "!", year]
        mangled  = []

        # FIX: `word.capitaliza()` → `word.capitalize()`
        for password in (word, word.capitalize()):
            for suffix in suffixes:
                # FIX: `"%S%S"` → `"%s%s"` (%S no existe en Python)
                mangled.append("%s%s" % (password, suffix))
        return mangled

    def display_wordlist(self):
        """Imprime la wordlist generada por la consola de salida de Burp."""
        print("#!comment: BHP Wordlist for site(s) %s" % ", ".join(self.hosts))
        for word in sorted(self.wordlist):
            for password in self.mangle(word):
                print(password)
        return
