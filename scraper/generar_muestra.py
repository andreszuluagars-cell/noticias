# -*- coding: utf-8 -*-
"""
Genera data/noticias.json de ejemplo usando titulares reales verificados
manualmente (agosto 2026) en las secciones de conflicto/judicial de cada
diario. Sirve para que la app tenga contenido real desde el primer momento,
mientras el scraper automático corre en GitHub Actions (que sí tiene
salida a internet; este entorno de pruebas no la tiene).

Reutiliza la misma lógica de clasificación que scraper.py para que el
resultado sea consistente con lo que producirá el scraper real.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
from scraper import clasificar_tema, normalizar, generar_id

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "web",
    "data",
    "noticias.json",
)

# Titulares reales tomados de las secciones de conflicto/judicial de cada
# diario (verificados el 14 de agosto de 2026).
MUESTRA = [
    dict(fuente="El Colombiano", seccion="Conflicto armado",
         titulo="Cayó alias 'Chuzo', señalado de desatar una guerra entre grupos armados en el Nordeste de Antioquia",
         url="https://www.elcolombiano.com/antioquia/captura-alias-chuzo-guerra-grupos-armados-nordeste-antioquia-DH39943257"),
    dict(fuente="El Colombiano", seccion="Conflicto armado",
         titulo="Doble golpe contra explosivos de ilegales: se entrega un explosivista y hallan 14 artefactos que podían haber sido sembrados",
         url="https://www.elcolombiano.com/antioquia/explosivista-se-entrega-hallan-14-artefactos-explosivos-ilegales-LA39933769"),
    dict(fuente="El Colombiano", seccion="Conflicto armado",
         titulo="Ejército y Clan del Golfo se enfrentan en zona rural de El Bagre, Antioquia",
         url="https://www.elcolombiano.com/antioquia/ejercito-clan-del-golfo-combates-zona-rural-el-bagre-antioquia-KA39930318"),
    dict(fuente="El Colombiano", seccion="Conflicto armado",
         titulo="Abatido alias 'Max Max', cerebro de los atentados con explosivos de las disidencias de 'Mordisco'",
         url="https://www.elcolombiano.com/colombia/dieron-baja-explosivista-disidencias-ivan-mordisco-ED39902420"),
    dict(fuente="El Espectador", seccion="Colombia+20",
         titulo="Petro retira de mesa de diálogo a voceros de disidencias de 'Calarcá': no ve voluntad",
         url="https://www.elespectador.com/politica/presidente-gustavo-petro-retira-de-mesa-dialogo-a-voceros-de-disidencias-de-alias-calarca-porque-no-ve-voluntad-y-se-presume-que-algunos-fallecieron-noticias-hoy/"),
    dict(fuente="El Espectador", seccion="Colombia+20",
         titulo="Consejo de Estado suspende provisionalmente nombramiento de Mancuso como gestor de paz",
         url="https://www.elespectador.com/judicial/consejo-de-estado-suspende-provisionalmente-nombramiento-de-mancuso-como-gestor-de-paz/"),
    dict(fuente="El Espectador", seccion="Colombia+20",
         titulo="Defensoría reporta 74 casos de reclutamiento de menores durante el primer periodo de 2026",
         url="https://www.elespectador.com/judicial/defensoria-reporta-74-casos-de-reclutamiento-de-menores-durante-el-primer-periodo-de-2026/"),
    dict(fuente="Semana", seccion="Nación",
         titulo="Disidencias de Mordisco estarían usando colegios, viviendas y escudos humanos para sembrar el terror en Cauca: Ejército",
         url="https://www.semana.com/nacion/articulo/disidencias-de-mordisco-estarian-usando-colegios-viviendas-y-escudos-humanos-para-sembrar-el-terror-en-cauca-ejercito/202608/"),
    dict(fuente="El País", seccion="Judicial",
         titulo="Asesinaron al dragoneante del Inpec Wilber Martínez cerca de la cárcel de Itagüí; hay dos capturados",
         url="https://www.elpais.com.co/judicial/asesinaron-al-dragoneante-del-inpec-wilber-martinez-cerca-de-la-carcel-de-itagui-hay-dos-capturados-1343.html"),
    dict(fuente="El País", seccion="Judicial",
         titulo="Golpe a las redes de apoyo a las disidencias en Pasto: capturados presuntos autores de ataque a subestación Jamundino",
         url="https://www.elpais.com.co/judicial/golpe-a-las-redes-de-apoyo-a-las-disidencias-en-pasto-capturados-presuntos-autores-de-ataque-a-subestacion-jamundino-1338.html"),
    dict(fuente="El País", seccion="Judicial",
         titulo="Muere alias Max Max, señalado explosivista de las disidencias de las Farc, tras varios días de combates en Ortega, Cajibío",
         url="https://www.elpais.com.co/judicial/muere-alias-max-max-senalado-explosivista-de-las-disidencias-de-las-farc-tras-varios-dias-de-combates-en-ortega-cajibio-1206.html"),
    dict(fuente="El País", seccion="Judicial",
         titulo="Ataque con explosivos contra el Ejército deja dos militares muertos y 19 heridos en Algeciras, Huila",
         url="https://www.elpais.com.co/judicial/ataque-con-explosivos-contra-el-ejercito-deja-dos-militares-muertos-y-19-heridos-en-algeciras-huila-1202.html"),
    dict(fuente="La Opinión", seccion="Judicial",
         titulo="Capturan en Pamplona a Clavijo, señalado de manejar explosivos, armas y drogas",
         url="https://laopinion.co/judicial/capturan-en-pamplona-clavijo-senalado-de-manejar-explosivos-armas-y-drogas"),
    dict(fuente="La Opinión", seccion="Judicial",
         titulo="Tragedia familiar en Carora: un muerto y un herido tras ataque armado contra jóvenes",
         url="https://laopinion.co/judicial/tragedia-familiar-en-carora-un-muerto-y-un-herido-tras-ataque-armado-contra-jovenes-en"),
    dict(fuente="La Opinión", seccion="Judicial",
         titulo="Ataque con drones en El Carmen, Norte de Santander deja un militar muerto",
         url="https://laopinion.co/judicial/ataque-con-drones-en-el-carmen-norte-de-santander-deja-un-militar-muerto"),
    dict(fuente="La Opinión", seccion="Judicial",
         titulo="Frustran presunto atentado con dron contra estación de Policía en El Zulia",
         url="https://laopinion.co/judicial/frustran-presunto-atentado-con-dron-contra-estacion-de-policia-en-el-zulia"),
    dict(fuente="El Espectador", seccion="Judicial",
         titulo="34 líderes sociales han sido asesinados en 2026: la alerta de la Defensoría del Pueblo",
         url="https://www.elespectador.com/judicial/34-lideres-sociales-han-sido-asesinados-en-2026-la-alerta-de-la-defensoria-del-pueblo/"),
    dict(fuente="El Tiempo", seccion="Justicia / Paz y derechos humanos",
         titulo="Más de 460 líderes sociales y firmantes de paz han sido asesinados en Colombia durante gobierno de Gustavo Petro desde 2024: Indepaz",
         url="https://www.eltiempo.com/justicia/paz-y-derechos-humanos/mas-de-460-lideres-sociales-y-firmantes-de-paz-han-sido-asesinados-en-colombia-durante-gobierno-de-gustavo-petro-desde-2024-indepaz-3576841"),
    dict(fuente="El Tiempo", seccion="Justicia / Paz y derechos humanos",
         titulo="Cada dos días asesinan a un líder social en Colombia en 2026; Antioquia encabeza los casos",
         url="https://www.eltiempo.com/justicia/paz-y-derechos-humanos/cada-dos-dias-asesinan-a-un-lider-social-en-colombia-en-2026-antioquia-encabeza-los-casos-3540507"),
]


def main():
    ahora = datetime.now(timezone.utc)
    noticias = []
    for i, item in enumerate(MUESTRA):
        texto = normalizar(f"{item['titulo']}")
        temas, encontradas = clasificar_tema(texto)
        noticias.append({
            "id": generar_id(item["url"]),
            "titulo": item["titulo"],
            "resumen": "",
            "url": item["url"],
            "fuente": item["fuente"],
            "seccion": item["seccion"],
            "fecha": (ahora - timedelta(hours=i)).isoformat(),
            "temas": temas if temas else ["General"],
            "palabras_clave": sorted(set(encontradas)),
        })

    salida = {
        "generado_en": ahora.isoformat(),
        "total_revisadas": len(MUESTRA),
        "total_relevantes": len(noticias),
        "nota": "Datos de ejemplo con titulares reales verificados manualmente. El scraper automático (scraper.py) reemplaza este archivo cada día vía GitHub Actions.",
        "noticias": noticias,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    print(f"Generadas {len(noticias)} noticias de muestra en {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
