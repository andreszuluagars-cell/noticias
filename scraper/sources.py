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
    # acceso automatizado). Estas fuentes NO se filtran con las palabras
    # clave de conflicto/DDHH/DIH colombianas (darían demasiado ruido con
    # noticias de otros países) — se filtran solo con las listas
    # MERCENARISMO y DICA de keywords.py, para rastrear específicamente
    # mercenarismo colombiano y Derecho Internacional de los Conflictos
    # Armados. Ver scraper.py.
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
]
