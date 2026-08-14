# Monitor Colombia — Conflicto armado, DDHH y DIH

Prototipo funcional de una app móvil (PWA) que filtra y muestra a diario
noticias sobre **conflicto armado, derechos humanos (DDHH) y Derecho
Internacional Humanitario (DIH)** publicadas en los principales diarios
colombianos: El Tiempo, El Espectador, Semana, El Colombiano, El País
(Cali), La Opinión (Cúcuta) y Vanguardia (Bucaramanga).

## Cómo funciona

```
scraper/   → script en Python que revisa los diarios y filtra noticias
web/       → la app (PWA): HTML/CSS/JS instalable en el celular
.github/   → automatización: corre el scraper todos los días y publica la app
```

1. **`scraper/scraper.py`** consulta cada diario (RSS donde existe, o la
   página de su sección de judicial/conflicto donde no) y se queda solo
   con los titulares que contienen palabras clave de conflicto armado,
   DDHH o DIH (ver `scraper/keywords.py`).
2. Guarda el resultado en `web/data/noticias.json`.
3. La app (`web/index.html` + `app.js`) lee ese archivo y muestra las
   noticias en tarjetas, con filtros por tema y por diario, buscador, y
   modo offline (vía service worker) para que abra incluso sin señal.
4. **GitHub Actions** ejecuta el scraper todos los días a las 5:30 a.m.
   (hora Colombia) y publica automáticamente la app actualizada en
   GitHub Pages — no necesitas tener un servidor propio prendido.

Ahora mismo el archivo `web/data/noticias.json` tiene noticias reales
de ejemplo (verificadas manualmente el 14 de agosto de 2026) para que
puedas ver la app funcionando de inmediato, mientras conectas la
actualización automática.

## Cómo probarla ahora mismo (sin publicar nada)

Necesitas Python 3 instalado.

```bash
cd web
python3 -m http.server 8000
```

Abre `http://localhost:8000` en el navegador de tu celular (conectado a
la misma red) o en Chrome de tu computador, y en el menú del navegador
elige "Agregar a pantalla de inicio" / "Instalar app" para probarla como
una app instalada.

## Cómo ponerla a actualizarse sola todos los días (recomendado)

1. Crea un repositorio nuevo en GitHub (puede ser privado o público).
2. Sube esta carpeta completa a ese repositorio:
   ```bash
   git init
   git add .
   git commit -m "Primera versión de Monitor Colombia"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
   git push -u origin main
   ```
3. En GitHub, ve a **Settings → Pages** y en "Build and deployment" elige
   **Source: GitHub Actions**.
4. Ve a la pestaña **Actions** del repositorio: verás dos workflows,
   *"Actualizar noticias diarias"* y *"Publicar app en GitHub Pages"*.
   Puedes correr cada uno manualmente la primera vez con el botón
   *"Run workflow"* para no esperar al horario programado.
5. Cuando termine, la URL de tu app aparecerá en **Settings → Pages**
   (algo como `https://tu-usuario.github.io/tu-repo/`). Ábrela desde el
   celular e instálala desde el menú del navegador.

A partir de ahí, todos los días a las 5:30 a.m. (hora Colombia) el
scraper revisa los diarios y actualiza la app sola — no tienes que hacer
nada más.

## Cómo ajustar qué se considera "relevante"

Edita `scraper/keywords.py`: son tres listas de palabras
(`CONFLICTO_ARMADO`, `DDHH`, `DIH`). Si una noticia contiene alguna de
esas palabras en el título, se guarda y se etiqueta con ese tema. Puedes
agregar o quitar palabras libremente — el cambio se aplica en la próxima
ejecución del scraper.

## Cómo agregar o quitar diarios

Edita `scraper/sources.py`. Cada fuente tiene:
- `type: "rss"` — para feeds RSS (más estables), o
- `type: "html"` — para páginas de sección/etiqueta (el scraper busca
  automáticamente titulares dentro de encabezados `<h1>`–`<h4>` y
  etiquetas `<article>`).

## Limitaciones de este prototipo (y qué mejorar después)

- **Clasificación por palabras clave, no por IA.** Es rápido y
  transparente, pero puede pasar por alto noticias relevantes que usan
  otras palabras, o marcar como relevante algo que no lo es. Si quieres,
  el siguiente paso natural es agregar un modelo de lenguaje que
  clasifique con más matiz (lo conversamos si te interesa).
- **El scraping HTML es frágil por naturaleza.** Si un diario rediseña su
  sitio, el selector genérico puede dejar de encontrar titulares en esa
  fuente puntual; hay que revisar `sources.py` de vez en cuando. Las
  fuentes RSS (El Tiempo) son más estables.
- **No hay notificaciones push todavía.** La app se actualiza cuando la
  abres; agregar notificaciones cuando hay una noticia nueva es posible
  pero requiere un paso adicional (un servicio de notificaciones).
- **No está en las tiendas de apps.** Es una PWA instalable desde el
  navegador, no un paquete para Play Store / App Store. Si más adelante
  quieres una app nativa "de verdad" en las tiendas, este prototipo sirve
  como base de contenido y diseño para construirla en React Native o
  Flutter.

## Próximos pasos sugeridos

- Probar la app instalada en tu celular unos días y ajustar palabras
  clave según lo que veas que falta o sobra.
- Sumar más diarios o fuentes especializadas (Verdad Abierta, INDEPAZ,
  CINEP) si quieres mayor profundidad.
- Evaluar clasificación por IA en vez de solo palabras clave.
- Evaluar notificaciones push para alertas del día.
