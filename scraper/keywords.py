# -*- coding: utf-8 -*-
"""
Palabras clave usadas para filtrar y clasificar noticias sobre conflicto
armado, Derechos Humanos (DDHH) y Derecho Internacional Humanitario (DIH).

Puedes editar libremente estas listas para ajustar qué se considera
"relevante". El scraper compara título + resumen de cada noticia (sin
tildes y en minúsculas) contra estas palabras.
"""

CONFLICTO_ARMADO = [
    "conflicto armado", "combates", "enfrentamiento armado", "enfrentamientos",
    "clan del golfo", "disidencias", "disidencias de las farc", "farc",
    "eln", "ejercito de liberacion nacional", "grupo armado", "grupos armados",
    "guerrilla", "guerrillero", "paramilitar", "paramilitares",
    "estructura armada", "gaor", "gao", "ataque armado", "atentado",
    "artefacto explosivo", "explosivos", "mina antipersona",
  "minas antipersonal", "reclutamiento forzado", "reclutamiento de menores",
    "reclutamiento", "redes de reclutamiento",
    "redes de reclutamiento transnacional",
    "desplazamiento forzado", "confinamiento", "secuestro", "masacre",
    "cese al fuego", "acuerdo de paz", "proceso de paz", "mesa de dialogo",
    "mesa de paz", "zona veredal", "jep", "jurisdiccion especial para la paz",
    "comision de la verdad", "sometimiento a la justicia", "toma guerrillera",
    "hostigamiento", "ataque a la fuerza publica", "orden publico",
    "gestor de paz", "militar muerto", "militares muertos", "soldado muerto",
    "ataque con drones", "ataque con dron",
]

DDHH = [
    "derechos humanos", "ddhh", "defensor de derechos humanos",
    "defensora de derechos humanos", "lider social", "lideres sociales",
    "lideresa social", "asesinato de lider social", "violencia de genero",
    "desaparicion forzada", "persona desaparecida", "tortura",
    "ejecucion extrajudicial", "ejecuciones extrajudiciales",
    "falsos positivos", "onu derechos humanos", "cidh",
    "corte interamericana de derechos humanos", "defensoria del pueblo",
    "amenazas a defensores", "victimas del conflicto", "unidad de victimas",
    "reparacion a victimas", "restitucion de tierras",
]

DIH = [
    "derecho internacional humanitario", "dih", "crimen de guerra",
    "crimenes de guerra", "poblacion civil", "bloqueo humanitario",
    "mision medica", "escudos humanos", "nino soldado", "ninos soldado",
    "reclutamiento de menores", "principio de distincion",
    "protocolo de ginebra", "convenios de ginebra", "cruz roja",
    "comite internacional de la cruz roja", "corredor humanitario",
    "ayuda humanitaria", "emergencia humanitaria",
]

# --- Categoría "Internacional" -------------------------------------------
# Se usa SOLO para las fuentes internacionales de sources.py (region:
# "internacional"). Ajustado el 29-ago-2026 a pedido explícito: ahora el
# criterio son estos 5 temas (más amplio que antes a propósito, ya que
# el criterio anterior —solo mercenarismo y terminología técnica de
# DICA— resultó demasiado angosto y algunos días no arrojaba ninguna
# noticia internacional):
#   1) Conflictos armados (en cualquier país, no solo Colombia)
#   2) Derechos Humanos
#   3) DIH (Derecho Internacional Humanitario)
#   4) Mercenarios (con énfasis en ciudadanos colombianos)
#   5) Guerra en Ucrania
# Todas se etiquetan bajo el mismo tema "Internacional" (no hay chips de
# filtro separados por sub-tema en la app); "palabras_clave" en cada
# noticia deja ver cuál de los 5 temas fue el que hizo match.

CONFLICTOS_ARMADOS_INTL = [
    "conflicto armado", "conflictos armados", "enfrentamiento armado",
    "enfrentamientos armados", "grupo armado", "grupos armados",
    "combates", "ofensiva militar", "ataque armado", "ataque militar",
    "zona de conflicto", "zona de guerra", "conflicto belico",
    "cese al fuego", "alto el fuego", "tregua humanitaria",
    "estallido de violencia", "toque de queda",
    "reclutamiento", "redes de reclutamiento",
    "redes de reclutamiento transnacional",
]

DERECHOS_HUMANOS_INTL = [
    "derechos humanos", "ddhh", "violaciones a los derechos humanos",
    "violacion de derechos humanos", "crisis humanitaria",
    "defensor de derechos humanos", "defensora de derechos humanos",
    "onu derechos humanos", "consejo de derechos humanos",
    "consejo de derechos humanos de la onu",
    "alto comisionado de la onu para los derechos humanos",
    "acnudh", "relator especial de la onu", "relatora especial de la onu",
    "examen periodico universal",
    "declaracion universal de derechos humanos",
    "corte interamericana de derechos humanos", "cidh",
    "desaparicion forzada", "tortura", "ejecucion extrajudicial",
    "ejecuciones extrajudiciales", "genocidio", "limpieza etnica",
]

DIH_INTL = [
    "derecho internacional humanitario", "dih",
    "derecho internacional de los conflictos armados", "dica",
    "crimen de guerra", "crimenes de guerra", "poblacion civil",
    "ayuda humanitaria", "corredor humanitario", "bloqueo humanitario",
    "emergencia humanitaria", "escudos humanos", "nino soldado",
    "ninos soldado", "convenios de ginebra", "protocolos adicionales",
    "cruz roja", "comite internacional de la cruz roja",
    "corte penal internacional", "tribunal penal internacional",
    "estatuto de roma", "corte internacional de justicia",
    "jus in bello", "principio de distincion", "principio de proporcionalidad",
    "conduccion de hostilidades", "combatientes ilegales",
    "estatuto de combatiente", "derecho de la guerra", "ley de la guerra",
]

MERCENARIOS = [
    # Términos genéricos (mercenarismo en cualquier país, no solo Colombia)
    "mercenario", "mercenarios", "mercenarismo",
    "trafico de mercenarios", "utilizacion de mercenarios",
    "grupo de trabajo sobre mercenarios", "empresas militares privadas",
    "compañias militares privadas", "companias militares privadas",
    "compañia militar privada", "compania militar privada",
    "grupo wagner", "mercenarios de wagner",
    # Énfasis específico en ciudadanos colombianos
    "mercenario colombiano", "mercenarios colombianos",
    "excombatientes colombianos", "exmilitares colombianos",
    "exmilitar colombiano", "veteranos colombianos",
    "soldados colombianos en", "colombianos reclutados",
    "reclutamiento de colombianos", "colombianos como mercenarios",
    "colombianos mercenarios", "contratistas colombianos",
    "colombianos en la guerra de ucrania", "colombianos en ucrania",
    "colombianos en rusia", "colombianos en sudan", "colombianos en yemen",
    "colombianos en medio oriente", "colombianos en emiratos",
    "wagner colombianos", "colombianos wagner", "mercenarismo colombiano",
]

GUERRA_UCRANIA = [
    "guerra en ucrania", "guerra de ucrania", "conflicto en ucrania",
    "invasion a ucrania", "invasion rusa a ucrania",
    "guerra ruso-ucraniana", "guerra rusia-ucrania",
    "frente ucraniano", "tropas ucranianas", "tropas rusas en ucrania",
    "ejercito ucraniano", "ejercito ruso en ucrania",
    "bombardeos rusos en ucrania", "ataques rusos en ucrania",
    "contraofensiva ucraniana", "avance ruso en ucrania",
    "negociaciones de paz en ucrania", "alto el fuego en ucrania",
    "drones rusos en ucrania", "ataques con drones en ucrania",
]

INTERNACIONAL = (
    CONFLICTOS_ARMADOS_INTL + DERECHOS_HUMANOS_INTL + DIH_INTL
    + MERCENARIOS + GUERRA_UCRANIA
)

# Diccionario usado por el scraper para clasificar cada noticia por tema.
# "Internacional" solo se evalúa para fuentes con region="internacional"
# (ver scraper.py: clasificar_tema recibe un diccionario de temas distinto
# según el origen de la noticia).
TOPIC_KEYWORDS = {
    "Conflicto armado": CONFLICTO_ARMADO,
    "DDHH": DDHH,
    "DIH": DIH,
}

TOPIC_KEYWORDS_INTERNACIONAL = {
    "Internacional": INTERNACIONAL,
}

# Lista plana de todas las palabras clave, usada para el filtro general.
ALL_KEYWORDS = CONFLICTO_ARMADO + DDHH + DIH
