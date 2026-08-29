const CACHE_NAME = "monitor-co-v3-osint";
const APP_SHELL = [
  "./",
  "./index.html",
  "./styles.css",
  "./app.js",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // data/noticias.json: red primero, y si falla usar caché (para tener
  // siempre la versión más reciente posible, con respaldo offline).
  //
  // Ojo con dos detalles que antes rompían el offline en silencio:
  // 1) app.js le agrega "?_=<timestamp>" a la URL en cada carga para
  //    evitar caché HTTP, así que cada carga pide una URL distinta. Si
  //    guardamos/buscamos en caché usando esa URL con query, la
  //    siguiente carga (con otro timestamp) nunca encuentra lo
  //    cacheado. Por eso usamos una clave de caché estable, sin query
  //    (origin + pathname), tanto al guardar como al leer.
  // 2) La escritura en caché (cache.put) es un side-effect asíncrono
  //    que hay que envolver en event.waitUntil(): si no, el navegador
  //    puede dar por terminado el service worker en cuanto respondWith
  //    resuelve, cancelando el cache.put antes de que termine.
  if (url.pathname.endsWith("noticias.json")) {
    const cacheKey = url.origin + url.pathname;
    event.respondWith(
      fetch(event.request)
        .then((resp) => {
          const clone = resp.clone();
          event.waitUntil(
            caches.open(CACHE_NAME).then((cache) => cache.put(cacheKey, clone))
          );
          return resp;
        })
        .catch(() => caches.match(cacheKey))
    );
    return;
  }

  // App shell: caché primero, con actualización en segundo plano.
  event.respondWith(
    caches.match(event.request).then((cached) => {
      const fetchPromise = fetch(event.request)
        .then((resp) => {
          if (resp && resp.status === 200) {
            const clone = resp.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return resp;
        })
        .catch(() => cached);
      return cached || fetchPromise;
    })
  );
});
