# -*- coding: utf-8 -*-
"""
Scraper diario de noticias sobre conflicto armado, DDHH y DIH en Colombia.

Recorre las fuentes definidas en sources.py (RSS y páginas HTML de
sección), filtra los titulares por las palabras clave de keywords.py,
clasifica cada noticia por tema y guarda el resultado en
data/noticias.json para que lo consuma la app móvil (PWA).

Uso:
    python scraper.py

Variables de entorno opcionales:
    MAX_POR_FUENTE   número máximo de noticias a revisar por fuente (default 40)
    SOLO_RELEVANTES  si es "0", guarda todo sin filtrar por palabras clave
                      (útil para depurar una fuente nueva)
"""
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone

import feedparser
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(__file__))
from keywords import (
    TOPIC_KEYWORDS,
    TOPIC_KEYWORDS_INTERNACIONAL,
    TOPIC_KEYWORDS_MERCENARISMO,
    ALL_KEYWORDS,
)
from sources import SOURCES

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 20
MAX_POR_FUENTE = int(os.environ.get("MAX_POR_FUENTE", "40"))
SOLO_RELEVANTES = os.environ.get("SOLO_RELEVANTES", "1") != "0"

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "web",
    "data",
    "noticias.json",
)

# Historial acumulado (solo tema "Mercenarismo"), usado por
# informe_semanal.py para armar el informe de la semana aunque las
# fuentes RSS/HTML ya hayan rotado esas noticias fuera de su página
# principal para cuando corre el informe.
HISTORIAL_MERCENARISMO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "web",
    "data",
    "historial_mercenarismo.json",
)

# Cuántos días de historial conservar como máximo (evita que el archivo
# crezca indefinidamente; 90 días da margen de sobra para informes
# semanales y para reconstruir uno atrasado si hiciera falta).
HISTORIAL_DIAS_MAX = 90


def normalizar(texto: str) -> str:
    """minúsculas y sin tildes, para comparar contra las palabras clave."""
    if not texto:
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


def _patron_palabra(palabra: str) -> re.Pattern:
    """Compila un patrón de coincidencia de PALABRA COMPLETA (con \\b) para
    una keyword ya normalizada.

    Antes se usaba una simple comprobación de substring ("palabra in
    texto"), pero eso produce falsos positivos con keywords cortas: por
    ejemplo "dica" hace match dentro de palabras españolas normales como
    "adjuDICAr", "inDICAn" o "deDICAn", sin ninguna relación con el DICA
    (Derecho Internacional de los Conflictos Armados). Con \\b solo hace
    match cuando la keyword aparece como palabra (o frase) completa.
    """
    return re.compile(r"\b" + re.escape(palabra) + r"\b")


def cargar_historial_mercenarismo() -> list:
    if not os.path.exists(HISTORIAL_MERCENARISMO_PATH):
        return []
    try:
        with open(HISTORIAL_MERCENARISMO_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("noticias", [])
    except Exception as e:
        print(f"[WARN] No se pudo leer el historial de mercenarismo: {e}")
        return []


def actualizar_historial_mercenarismo(noticias_mercenarismo: list) -> None:
    """Agrega al historial las noticias nuevas del tema "Mercenarismo" de
    esta corrida (dedup por id), y recorta lo más viejo que
    HISTORIAL_DIAS_MAX. Así informe_semanal.py siempre tiene a mano la
    última semana completa, aunque una fuente ya haya rotado esa noticia
    fuera de su RSS/página principal.
    """
    from datetime import timedelta

    existentes = cargar_historial_mercenarismo()
    por_id = {n["id"]: n for n in existentes}
    for n in noticias_mercenarismo:
        por_id[n["id"]] = n

    limite = datetime.now(timezone.utc) - timedelta(days=HISTORIAL_DIAS_MAX)
    vigentes = []
    for n in por_id.values():
        try:
            fecha = datetime.fromisoformat(n["fecha"])
            if fecha.tzinfo is None:
                fecha = fecha.replace(tzinfo=timezone.utc)
        except Exception:
            fecha = datetime.now(timezone.utc)
        if fecha >= limite:
            vigentes.append(n)

    vigentes.sort(key=lambda x: x["fecha"], reverse=True)

    os.makedirs(os.path.dirname(HISTORIAL_MERCENARISMO_PATH), exist_ok=True)
    with open(HISTORIAL_MERCENARISMO_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "actualizado_en": datetime.now(timezone.utc).isoformat(),
                "noticias": vigentes,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def clasificar_tema(texto_normalizado: str, topic_keywords: dict = None):
    """Devuelve la lista de temas que coinciden con el texto, y la lista
    de palabras clave encontradas.

    Por defecto clasifica contra TOPIC_KEYWORDS (Conflicto armado / DDHH /
    DIH — fuentes colombianas). Para fuentes internacionales se le pasa
    TOPIC_KEYWORDS_INTERNACIONAL en su lugar (ver filtrar_y_clasificar),
    así una fuente de otro país nunca se marca como relevante solo por
    mencionar palabras genéricas de conflicto que no tienen que ver con
    Colombia.
    """
    if topic_keywords is None:
        topic_keywords = TOPIC_KEYWORDS
    temas = []
    encontradas = []
    for tema, palabras in topic_keywords.items():
        for palabra in palabras:
            if _patron_palabra(normalizar(palabra)).search(texto_normalizado):
                temas.append(tema)
                encontradas.append(palabra)
                break
    return temas, encontradas


def es_relevante(titulo: str, resumen: str = "") -> bool:
    texto = normalizar(f"{titulo} {resumen}")
    return any(_patron_palabra(normalizar(p)).search(texto) for p in ALL_KEYWORDS)


def generar_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]


def parsear_fecha_rss(entry) -> str:
    for campo in ("published_parsed", "updated_parsed"):
        valor = entry.get(campo)
        if valor:
            return datetime(*valor[:6], tzinfo=timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def limpiar_resumen(resumen_html: str) -> str:
    """Quita etiquetas HTML, enlaces "Leer" y píxeles de tracking que
    algunos feeds RSS meten dentro de <summary> (p. ej. El Mundo,
    Infobae). Si no se limpia, ese HTML crudo (URLs, atributos) se cuela
    en el texto que usa el clasificador de palabras clave y mete ruido.
    """
    if not resumen_html:
        return ""
    texto = BeautifulSoup(resumen_html, "html.parser").get_text(" ", strip=True)
    return texto


def obtener_rss(fuente: dict) -> list:
    noticias = []
    try:
        feed = feedparser.parse(fuente["url"])
    except Exception as e:
        print(f"[ERROR] RSS {fuente['name']} ({fuente['url']}): {e}")
        return noticias

    for entry in feed.entries[:MAX_POR_FUENTE]:
        titulo = entry.get("title", "").strip()
        resumen = limpiar_resumen(entry.get("summary", "").strip())
        link = entry.get("link", "").strip()
        if not titulo or not link:
            continue
        noticias.append(
            {
                "titulo": titulo,
                "resumen": resumen,
                "url": link,
                "fuente": fuente["name"],
                "seccion": fuente.get("section", ""),
                "region": fuente.get("region", "nacional"),
                "fecha": parsear_fecha_rss(entry),
            }
        )
    return noticias


def obtener_html(fuente: dict) -> list:
    noticias = []
    try:
        resp = requests.get(fuente["url"], headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] HTML {fuente['name']} ({fuente['url']}): {e}")
        return noticias

    # Todos los diarios de sources.py publican en UTF-8. Si el sitio no
    # declara el charset en el header HTTP, "requests" adivina mal
    # (asume Latin-1 por defecto) y las tildes/ñ quedan corruptas
    # ("Ã©" en vez de "é"). Forzamos UTF-8 explícitamente para evitarlo.
    resp.encoding = "utf-8"

    soup = BeautifulSoup(resp.text, "html.parser")
    debe_contener = fuente.get("link_must_contain", "")
    vistos = set()

    # Estrategia genérica: los titulares casi siempre están dentro de
    # h1/h2/h3/h4 que envuelven o contienen un <a>. Se recorre esa
    # combinación en vez de depender de clases CSS específicas de cada
    # sitio (que cambian con frecuencia).
    candidatos = soup.select("h1 a, h2 a, h3 a, h4 a, article a")

    for a in candidatos:
        href = a.get("href", "").strip()
        titulo = a.get_text(strip=True)

        if not href or not titulo or len(titulo) < 20:
            continue
        if href.startswith("/"):
            base = f"https://{debe_contener}" if debe_contener else fuente["url"]
            href = base.rstrip("/") + href
        if debe_contener and debe_contener not in href:
            continue
        if href in vistos:
            continue
        vistos.add(href)

        noticias.append(
            {
                "titulo": titulo,
                "resumen": "",
                "url": href,
                "fuente": fuente["name"],
                "seccion": fuente.get("section", ""),
                "region": fuente.get("region", "nacional"),
                "fecha": datetime.now(timezone.utc).isoformat(),
            }
        )
        if len(noticias) >= MAX_POR_FUENTE:
            break

    return noticias


def recolectar() -> list:
    todas = []
    for fuente in SOURCES:
        print(f"Consultando {fuente['name']} ({fuente.get('section','')})...")
        if fuente["type"] == "rss":
            items = obtener_rss(fuente)
        else:
            items = obtener_html(fuente)
        print(f"  -> {len(items)} enlaces encontrados")
        todas.extend(items)
    return todas


def filtrar_y_clasificar(noticias: list) -> list:
    resultado = []
    ids_vistos = set()

    for n in noticias:
        texto_normalizado = normalizar(f"{n['titulo']} {n['resumen']}")
        region = n.get("region", "nacional")

        # Cada región se clasifica contra un diccionario de temas distinto:
        # - "internacional": fuentes internacionales, SOLO contra la lista
        #   de conflicto armado/DDHH/DIH/mercenarios/guerra en Ucrania a
        #   nivel mundial — no contra las palabras de conflicto colombiano
        #   específico (farc, eln, clan del golfo, etc.), que en un diario
        #   de otro país producirían ruido.
        # - "mercenarismo": fuentes especializadas (INDEPAZ, Verdad
        #   Abierta, CINEP, SAT), SOLO contra la lista angosta de los 6
        #   temas de mercenarismo/reclutamiento transnacional — el resto
        #   de su cobertura de conflicto/DDHH se descarta a propósito.
        # - cualquier otra cosa (o ausente): fuentes nacionales, contra la
        #   lista general de conflicto armado/DDHH/DIH en Colombia.
        if region == "internacional":
            topic_keywords = TOPIC_KEYWORDS_INTERNACIONAL
        elif region == "mercenarismo":
            topic_keywords = TOPIC_KEYWORDS_MERCENARISMO
        else:
            topic_keywords = TOPIC_KEYWORDS
        temas, encontradas = clasificar_tema(texto_normalizado, topic_keywords)
        relevante = bool(temas)

        if SOLO_RELEVANTES and not relevante:
            continue

        noticia_id = generar_id(n["url"])
        if noticia_id in ids_vistos:
            continue
        ids_vistos.add(noticia_id)

        resultado.append(
            {
                "id": noticia_id,
                "titulo": n["titulo"],
                "resumen": n["resumen"],
                "url": n["url"],
                "fuente": n["fuente"],
                "seccion": n["seccion"],
                "region": n.get("region", "nacional"),
                "fecha": n["fecha"],
                "temas": temas if temas else ["General"],
                "palabras_clave": sorted(set(encontradas)),
            }
        )

    # Más recientes primero
    resultado.sort(key=lambda x: x["fecha"], reverse=True)
    return resultado


def main():
    crudas = recolectar()
    filtradas = filtrar_y_clasificar(crudas)

    mercenarismo_hoy = [n for n in filtradas if "Mercenarismo" in n["temas"]]
    actualizar_historial_mercenarismo(mercenarismo_hoy)

    salida = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "total_revisadas": len(crudas),
        "total_relevantes": len(filtradas),
        "noticias": filtradas,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    print(f"\nListo: {len(filtradas)} noticias relevantes de {len(crudas)} revisadas.")
    print(f"Guardado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
