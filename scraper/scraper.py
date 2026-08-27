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
from keywords import TOPIC_KEYWORDS, ALL_KEYWORDS
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


def normalizar(texto: str) -> str:
    """minúsculas y sin tildes, para comparar contra las palabras clave."""
    if not texto:
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


def clasificar_tema(texto_normalizado: str):
    """Devuelve la lista de temas (Conflicto armado / DDHH / DIH) que
    coinciden con el texto, y la lista de palabras clave encontradas."""
    temas = []
    encontradas = []
    for tema, palabras in TOPIC_KEYWORDS.items():
        for palabra in palabras:
            if normalizar(palabra) in texto_normalizado:
                temas.append(tema)
                encontradas.append(palabra)
                break
    return temas, encontradas


def es_relevante(titulo: str, resumen: str = "") -> bool:
    texto = normalizar(f"{titulo} {resumen}")
    return any(normalizar(p) in texto for p in ALL_KEYWORDS)


def generar_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]


def parsear_fecha_rss(entry) -> str:
    for campo in ("published_parsed", "updated_parsed"):
        valor = entry.get(campo)
        if valor:
            return datetime(*valor[:6], tzinfo=timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def obtener_rss(fuente: dict) -> list:
    noticias = []
    try:
        feed = feedparser.parse(fuente["url"])
    except Exception as e:
        print(f"[ERROR] RSS {fuente['name']} ({fuente['url']}): {e}")
        return noticias

    for entry in feed.entries[:MAX_POR_FUENTE]:
        titulo = entry.get("title", "").strip()
        resumen = entry.get("summary", "").strip()
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
    # declara el charset en el header HTTP, "requests" adivina mal y las
    # tildes/ñ quedan corruptas ("Ã©" en vez de "é"). Forzamos UTF-8.
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
        temas, encontradas = clasificar_tema(texto_normalizado)
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
