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
    "estructura armada", "gaoR", "gao", "ataque armado", "atentado",
    "artefacto explosivo", "explosivos", "mina antipersona",
  "minas antipersonal", "reclutamiento forzado", "reclutamiento de menores",
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
# "internacional"). A diferencia de los diarios colombianos, esas fuentes
# cubren todo tipo de noticias del mundo, así que en vez de filtrarlas con
# las listas de arriba (darían muchísimo ruido: "combates", "guerra",
# etc. de conflictos que no tienen nada que ver con Colombia), se filtran
# ÚNICAMENTE con estas dos listas especializadas.

MERCENARISMO = [
    "mercenario colombiano", "mercenarios colombianos",
    "excombatientes colombianos", "exmilitares colombianos",
    "exmilitar colombiano", "veteranos colombianos",
    "soldados colombianos en", "colombianos reclutados",
    "reclutamiento de colombianos", "colombianos como mercenarios",
    "colombianos mercenarios", "contratistas colombianos",
    "colombianos en la guerra de ucrania", "colombianos en ucrania",
    "colombianos en rusia", "colombianos en sudan", "colombianos en yemen",
    "colombianos en medio oriente", "colombianos en emiratos",
    "trafico de mercenarios", "utilizacion de mercenarios",
    "grupo de trabajo sobre mercenarios", "empresas militares privadas",
    "compañias militares privadas", "companias militares privadas",
    "wagner colombianos", "colombianos wagner",
    "mercenarismo colombiano", "mercenarismo",
]

DICA = [
    "derecho internacional de los conflictos armados", "dica",
    "jus in bello", "conduccion de hostilidades",
    "corte penal internacional", "tribunal penal internacional",
    "estatuto de roma", "conflicto armado no internacional",
    "conflicto armado internacional", "principio de proporcionalidad",
    "combatientes ilegales", "estatuto de combatiente",
    "derecho de la guerra", "ley de la guerra", "crimenes de guerra",
    "convenios de ginebra", "protocolos adicionales",
]

INTERNACIONAL = MERCENARISMO + DICA

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
