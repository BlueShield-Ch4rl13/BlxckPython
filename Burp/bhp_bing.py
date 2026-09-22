"""
bhp_bing.py - Extensión Burp Suite: búsqueda en Bing por IP/dominio
=====================================================================
Extensión para Burp Suite (Jython) que añade una opción de menú contextual
"Send to Bing". Al seleccionar un host en la historia HTTP, lanza búsquedas
en la API Cognitive de Bing (`ip:<ip>` y `domain:<host>`) y añade
automáticamente al scope de Burp las URLs encontradas.

REQUISITOS:
    - Burp Suite con soporte Jython (Extender → Options → Jython standalone)
    - API Key de Bing Cognitive Search v7 en la variable API_KEY

EJEMPLOS DE EJECUCIÓN:
    Cargar en Burp: Extender → Extensions → Add → Extension Type: Python → bhp_bing.py
"""

import json
import socket
import threading
import urllib.parse

from burp import IBurpExtender
from burp import IContextMenuFactory   # FIX: 'IContexMenuFactory' → 'IContextMenuFactory'

from java.net     import URL
from java.util    import ArrayList
from javax.swing  import JMenuItem     # FIX: 'JmenuItem' → 'JMenuItem'

# -------------------------------------------------------------------
# Configuración — reemplazar con tu clave de API real
# -------------------------------------------------------------------
API_KEY  = os.environ.get('BING_API_KEY', 'YOUR_BING_API_KEY')
API_HOST = 'api.cognitive.microsoft.com'


class BurpExtender(IBurpExtender, IContextMenuFactory):  # FIX: nombre de interfaz corregido

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self.context    = None

        callbacks.setExtensionName("BHP Bing")
        callbacks.registerContextMenuFactory(self)
        return

    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list    = ArrayList()
        # FIX: JmenuItem → JMenuItem
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        return menu_list

    def bing_menu(self, event):
        """Callback del elemento de menú: obtiene los hosts seleccionados."""
        http_traffic = self.context.getSelectedMessages()
        print("%d requests highlighted" % len(http_traffic))

        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()
            print("User selected host: %s" % host)
            self.bing_search(host)
        return

    def bing_search(self, host):
        """
        Determina si `host` es IP o nombre de dominio y lanza la búsqueda
        en Bing en un hilo aparte.

        Args:
            host (str): Nombre de host o dirección IP seleccionada en Burp.
        """
        try:
            is_ip = bool(socket.inet_aton(host))
        except socket.error:
            is_ip = False

        if is_ip:
            ip_address = host
            domain     = False
        else:
            ip_address = socket.gethostbyname(host)
            domain     = True

        # FIX: `start_new_thread` (Python 2) → threading.Thread (Python 3)
        t = threading.Thread(target=self.bing_query, args=('ip:%s' % ip_address,))
        t.daemon = True
        t.start()

        if domain:
            t2 = threading.Thread(target=self.bing_query, args=('domain:%s' % host,))
            t2.daemon = True
            t2.start()

    def bing_query(self, bing_query_string):
        """
        Realiza la petición HTTP a la API de Bing Cognitive Search v7.

        Args:
            bing_query_string (str): Cadena de búsqueda (p. ej. 'ip:1.2.3.4').
        """
        print('Performing Bing search: %s' % bing_query_string)
        http_request  = 'GET https://%s/bing/v7.0/search?' % API_HOST
        # FIX: urllib.quote → urllib.parse.quote (Python 3)
        http_request += 'q=%s HTTP/1.1\r\n' % urllib.parse.quote(bing_query_string)
        http_request += 'Host: %s\r\n' % API_HOST
        http_request += 'Connection: close\r\n'
        # FIX: '0cp-Apim-...' → 'Ocp-Apim-...' (era un cero, no la letra O)
        http_request += 'Ocp-Apim-Subscription-Key: %s\r\n' % API_KEY
        http_request += 'User-Agent: Black Hat Python\r\n\r\n'

        json_body = self._callbacks.makeHttpRequest(
            API_HOST, 443, True, http_request
        ).tostring()
        json_body = json_body.split('\r\n\r\n', 1)[1]

        try:
            response = json.loads(json_body)
        except (TypeError, ValueError) as err:
            print('No results from Bing: %s' % err)
        else:
            sites = []
            if response.get('webPages'):
                sites = response['webPages']['value']
            for site in sites:
                print('*' * 100)
                print('Name: %s'        % site['name'])
                print('URL: %s'         % site['url'])
                print('Description: %r' % site['snippet'])
                print('*' * 100)

                java_url = URL(site['url'])
                if not self._callbacks.isInScope(java_url):
                    print('Adding %s to Burp scope' % site['url'])
                    self._callbacks.includeInScope(java_url)
        return
