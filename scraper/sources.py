# -*- coding: utf-8 -*-
"""
Configuración de fuentes (diarios) que el scraper consulta cada día.

Cada fuente es de tipo:
  - "rss": se descarga y parsea un feed RSS/XML (más estable).
  - "html": se descarga una página de sección/etiqueta y se extraen los
    enlaces de titulares con un selector CSS genérico.

Todas las fuentes fueron verificadas manualmente en agosto de 2026.
Si un diario cambia su sitio web, es posible que haya que actualizar la
URL o el selector aquí — es el único lugar del proyecto donde eso se
configura.
"""

SOURCES = [
    # --- El Tiempo (RSS oficial) ---
    {
        "name": "El Tiempo",
        "type": "rss",
        "url": "https://www.eltiempo.com/rss/justicia_conflicto-y-narcotrafico.xml",
        "section": "Justicia / Conflicto y narcotráfico",
    },
    {
        "name": "El Tiempo",
        "type": "rss",
        "url": "https://www.eltiempo.com/rss/politica_proceso-de-paz.xml",
        "section": "Política / Proceso de paz",
    },
    {
        "name": "El Tiempo",
        "type": "rss",
        "url": "https://www.eltiempo.com/rss/justicia.xml",
        "section": "Justicia",
    },

    # --- El Espectador (sección Colombia+20, dedicada a conflicto y paz) ---
    {
        "name": "El Espectador",
        "type": "html",
        "url": "https://www.elespectador.com/colombia-20/",
        "section": "Colombia+20",
        "link_must_contain": "elespectador.com",
    },

    # --- Semana (sección Nación) ---
    {
        "name": "Semana",
        "type": "html",
        "url": "https://www.semana.com/nacion/",
        "section": "Nación",
        "link_must_contain": "semana.com",
    },

    # --- El Colombiano (cronología de conflicto armado) ---
    {
        "name": "El Colombiano",
        "type": "html",
        "url": "https://www.elcolombiano.com/cronologia/noticias/meta/conflicto-armado",
        "section": "Conflicto armado",
        "link_must_contain": "elcolombiano.com",
    },

    # --- El País (Cali) ---
    {
        "name": "El País",
        "type": "html",
        "url": "https://www.elpais.com.co/judicial/",
        "section": "Judicial",
        "link_must_contain": "elpais.com.co",
    },

    # --- La Opinión (Cúcuta) ---
    {
        "name": "La Opinión",
        "type": "html",
        "url": "https://laopinion.co/judicial",
        "section": "Judicial",
        "link_must_contain": "laopinion.co",
    },

    # --- Vanguardia (Bucaramanga) ---
    {
        "name": "Vanguardia",
        "type": "html",
        "url": "https://www.vanguardia.com/colombia/",
        "section": "Colombia",
        "link_must_contain": "vanguardia.com",
    },

    # =======================================================================
    # FUENTES INTERNACIONALES (region: "internacional")
    #
    # Los 5 diarios en español de mayor alcance fuera de Colombia que se
    # pudieron verificar como accesibles (El País, Clarín y ABC bloquean el
    # acceso automatizado). Estas fuentes NO se filtran con las listas
    # colombianas de arriba — se filtran con la lista INTERNACIONAL de
    # keywords.py, que cubre 5 temas: conflictos armados (en cualquier
    # país), derechos humanos, DIH, mercenarios (con énfasis en
    # ciudadanos colombianos) y la guerra en Ucrania. Ver scraper.py.
    # =======================================================================

    {
        "name": "Infobae",
        "type": "rss",
        "url": "https://www.infobae.com/arc/outboundfeeds/rss/",
        "section": "Mundo (Argentina)",
        "region": "internacional",
    },
    {
        "name": "El Mundo",
        "type": "rss",
        "url": "https://e00-elmundo.uecdn.es/elmundo/rss/internacional.xml",
        "section": "Internacional (España)",
        "region": "internacional",
    },
    {
        "name": "El Universal",
        "type": "html",
        "url": "https://www.eluniversal.com.mx/mundo",
        "section": "Mundo (México)",
        "link_must_contain": "eluniversal.com.mx",
        "region": "internacional",
    },
    {
        "name": "La Nación",
        "type": "html",
        "url": "https://www.lanacion.com.ar/el-mundo/",
        "section": "El Mundo (Argentina)",
        "link_must_contain": "lanacion.com.ar",
        "region": "internacional",
    },
    {
        "name": "El Comercio",
        "type": "html",
        "url": "https://elcomercio.pe/mundo/",
        "section": "Mundo (Perú)",
        "link_must_contain": "elcomercio.pe",
        "region": "internacional",
    },

    # =======================================================================
    # FUENTES ESPECIALIZADAS (region: "reclutamiento_transnacional")
    #
    # INDEPAZ, Verdad Abierta, CINEP y el Sistema de Alertas Tempranas de
    # la Defensoría del Pueblo. A diferencia de las demás fuentes, estas
    # NO se filtran con ninguna lista de conflicto/DDHH/DIH general — se
    # filtran ÚNICAMENTE con la lista RECLUTAMIENTO_TRANSNACIONAL de
    # keywords.py, para quedarnos solo con lo que tenga que ver
    # exclusivamente con reclutamiento transnacional de ciudadanos
    # colombianos para conflictos internacionales (el resto de su
    # cobertura diaria de conflicto/DDHH en Colombia, aunque relevante en
    # general, queda fuera de la app a propósito — ya está cubierta por
    # las fuentes nacionales). Ver scraper.py.
    # =======================================================================

    {
        "name": "INDEPAZ",
        "type": "rss",
        "url": "https://indepaz.org.co/feed/",
        "section": "Instituto de Estudios para el Desarrollo y la Paz",
        "region": "reclutamiento_transnacional",
    },
    {
        "name": "Verdad Abierta",
        "type": "rss",
        "url": "https://verdadabierta.com/feed/",
        "section": "Verdad Abierta",
        "region": "reclutamiento_transnacional",
    },
    {
        "name": "CINEP",
        "type": "rss",
        "url": "https://cinep.org.co/feed/",
        "section": "Centro de Investigación y Educación Popular",
        "region": "reclutamiento_transnacional",
    },
    {
        # La Defensoría no es WordPress (corre en Liferay), así que no
        # tiene un feed RSS estándar. Se scrapea la página de comunicados,
        # donde se anuncian las Alertas Tempranas (ej. "Alerta Temprana
        # 023 de 2026"), junto con comunicados de prensa generales — por
        # eso es clave que el filtro de palabras clave sea estricto aquí.
        # El selector genérico (h1-h4 a, article a) de scraper.py no se
        # pudo verificar contra el markup real de este sitio (es un
        # portal Liferay, con paginación por portlets); si tras la
        # primera corrida real no trae resultados, puede que el selector
        # necesite un ajuste específico para este sitio.
        "name": "Defensoría del Pueblo (SAT)",
        "type": "html",
        "url": "https://www.defensoria.gov.co/comunicados",
        "section": "Sistema de Alertas Tempranas",
        "link_must_contain": "defensoria.gov.co",
        "region": "reclutamiento_transnacional",
    },
]
