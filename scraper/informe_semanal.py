# -*- coding: utf-8 -*-
"""
Informe semanal de la categoría "Mercenarismo".

Lee el historial acumulado por scraper.py (web/data/historial_mercenarismo.json)
y genera un informe con las noticias de los últimos 7 días: medio, fecha,
título, resumen y link. El informe se guarda como JSON dentro de
web/data/informes/ (para que la app lo muestre en la sección "INFORMES") y,
si hay credenciales configuradas, se envía por correo.

Uso:
    python informe_semanal.py

Variables de entorno opcionales/requeridas para el envío de correo:
    GMAIL_USER           cuenta de Gmail remitente (ej. monitor.colombia@gmail.com)
    GMAIL_APP_PASSWORD    contraseña de aplicación de esa cuenta (NO la contraseña normal)
    INFORME_DESTINATARIO  correo destino (default: andres.zuluagar@esdeg.edu.co)

Si GMAIL_USER / GMAIL_APP_PASSWORD no están configuradas, el informe se
genera igual (queda disponible en la app) pero el envío de correo se omite
con una advertencia — así se puede correr y probar este script localmente
sin credenciales.
"""
import json
import os
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(__file__))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORIAL_PATH = os.path.join(BASE_DIR, "web", "data", "historial_mercenarismo.json")
INFORMES_DIR = os.path.join(BASE_DIR, "web", "data", "informes")
INDEX_PATH = os.path.join(INFORMES_DIR, "index.json")

DESTINATARIO = os.environ.get("INFORME_DESTINATARIO", "andres.zuluagar@esdeg.edu.co")
DIAS_VENTANA = 7


def cargar_historial() -> list:
    if not os.path.exists(HISTORIAL_PATH):
        return []
    with open(HISTORIAL_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("noticias", [])


def filtrar_ventana(noticias: list, hasta: datetime, desde: datetime) -> list:
    resultado = []
    for n in noticias:
        try:
            fecha = datetime.fromisoformat(n["fecha"])
            if fecha.tzinfo is None:
                fecha = fecha.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if desde <= fecha <= hasta:
            resultado.append(n)
    resultado.sort(key=lambda x: x["fecha"], reverse=True)
    return resultado


def construir_informe(noticias: list, desde: datetime, hasta: datetime, titulo: str, informe_id: str) -> dict:
    return {
        "id": informe_id,
        "titulo": titulo,
        "categoria": "Mercenarismo",
        "desde": desde.date().isoformat(),
        "hasta": hasta.date().isoformat(),
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "total": len(noticias),
        "noticias": [
            {
                "medio": n["fuente"],
                "fecha": n["fecha"],
                "titulo": n["titulo"],
                "resumen": n.get("resumen", ""),
                "url": n["url"],
            }
            for n in noticias
        ],
    }


def guardar_informe(informe: dict) -> str:
    os.makedirs(INFORMES_DIR, exist_ok=True)
    nombre_archivo = f"informe-{informe['id']}.json"
    ruta = os.path.join(INFORMES_DIR, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)
    return nombre_archivo


def actualizar_index(informe: dict, nombre_archivo: str, tipo: str = "semanal") -> None:
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {"informes": []}

    # Si ya existe un informe con el mismo id (ej. se corre dos veces el
    # mismo día), se reemplaza en vez de duplicarse.
    index["informes"] = [i for i in index["informes"] if i["id"] != informe["id"]]
    index["informes"].append(
        {
            "id": informe["id"],
            "titulo": informe["titulo"],
            "tipo": tipo,
            "desde": informe["desde"],
            "hasta": informe["hasta"],
            "generado_en": informe["generado_en"],
            "total": informe["total"],
            "archivo": nombre_archivo,
        }
    )
    # Más reciente primero.
    index["informes"].sort(key=lambda i: i["hasta"], reverse=True)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def construir_cuerpo_html(informe: dict) -> str:
    filas = ""
    for n in informe["noticias"]:
        fecha_corta = n["fecha"][:10]
        resumen = n["resumen"] or "(sin resumen)"
        filas += f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #ddd;white-space:nowrap;">{fecha_corta}</td>
          <td style="padding:8px;border-bottom:1px solid #ddd;white-space:nowrap;">{n['medio']}</td>
          <td style="padding:8px;border-bottom:1px solid #ddd;">
            <a href="{n['url']}">{n['titulo']}</a><br/>
            <span style="color:#666;font-size:13px;">{resumen}</span>
          </td>
        </tr>"""

    if not informe["noticias"]:
        cuerpo_tabla = "<p>No se encontraron noticias de la categoría Mercenarismo en este periodo.</p>"
    else:
        cuerpo_tabla = f"""
        <table style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif;font-size:14px;">
          <thead>
            <tr style="background:#f2f2f2;text-align:left;">
              <th style="padding:8px;">Fecha</th>
              <th style="padding:8px;">Medio</th>
              <th style="padding:8px;">Noticia</th>
            </tr>
          </thead>
          <tbody>{filas}
          </tbody>
        </table>"""

    return f"""
    <html>
      <body style="font-family:Arial,sans-serif;color:#222;">
        <h2>{informe['titulo']}</h2>
        <p>Periodo: {informe['desde']} a {informe['hasta']} · {informe['total']} noticia(s) encontradas.</p>
        {cuerpo_tabla}
        <p style="color:#999;font-size:12px;margin-top:24px;">
          Generado automáticamente por Monitor Colombia — Proyecto de investigación
          sobre redes de reclutamiento transnacional.
        </p>
      </body>
    </html>
    """


def enviar_correo(informe: dict) -> bool:
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_pass:
        print(
            "[AVISO] GMAIL_USER / GMAIL_APP_PASSWORD no están configuradas — "
            "se omite el envío de correo (el informe sí quedó guardado para la app)."
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Monitor Colombia] {informe['titulo']}"
    msg["From"] = gmail_user
    msg["To"] = DESTINATARIO
    msg.attach(MIMEText(construir_cuerpo_html(informe), "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, [DESTINATARIO], msg.as_string())
        print(f"Informe enviado por correo a {DESTINATARIO}.")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo enviar el correo: {e}")
        return False


def main():
    ahora = datetime.now(timezone.utc)
    hasta = ahora
    desde = ahora - timedelta(days=DIAS_VENTANA)

    historial = cargar_historial()
    noticias_semana = filtrar_ventana(historial, hasta, desde)

    informe_id = ahora.date().isoformat()
    titulo = f"Informe semanal — Mercenarismo ({desde.date().isoformat()} a {hasta.date().isoformat()})"
    informe = construir_informe(noticias_semana, desde, hasta, titulo, informe_id)

    nombre_archivo = guardar_informe(informe)
    actualizar_index(informe, nombre_archivo, tipo="semanal")
    enviar_correo(informe)

    print(f"\nInforme semanal listo: {informe['total']} noticias ({informe['desde']} a {informe['hasta']}).")
    print(f"Guardado en: {os.path.join(INFORMES_DIR, nombre_archivo)}")


if __name__ == "__main__":
    main()
