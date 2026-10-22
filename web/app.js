(function () {
  "use strict";

  const DATA_URL = "data/noticias.json?_=" + Date.now();

  const state = {
    noticias: [],
    topic: "Todos",
    source: "Todos",
    query: "",
    generadoEn: null,
  };

  const els = {
    list: document.getElementById("news-list"),
    empty: document.getElementById("empty-state"),
    status: document.getElementById("status-line"),
    refreshBtn: document.getElementById("refresh-btn"),
    search: document.getElementById("search"),
    sourceSelect: document.getElementById("source-select"),
    chips: Array.from(document.querySelectorAll(".chip")),
    offlineBanner: document.getElementById("offline-banner"),
    informesBtn: document.getElementById("informes-btn"),
    informesOverlay: document.getElementById("informes-overlay"),
    informesClose: document.getElementById("informes-close"),
    informesListaView: document.getElementById("informes-lista-view"),
    informesLista: document.getElementById("informes-lista"),
    informesVacio: document.getElementById("informes-vacio"),
    informesDetalleView: document.getElementById("informes-detalle-view"),
    informesVolver: document.getElementById("informes-volver"),
    informesDetalleTitulo: document.getElementById("informes-detalle-titulo"),
    informesDetalleMeta: document.getElementById("informes-detalle-meta"),
    informesDetalleLista: document.getElementById("informes-detalle-lista"),
  };

  const TAG_CLASS = {
    "Conflicto armado": "tag-conflicto",
    "DDHH": "tag-ddhh",
    "DIH": "tag-dih",
    "Internacional": "tag-internacional",
    "Mercenarismo": "tag-mercenarismo",
    "General": "tag-general",
  };

  const TOPIC_VAR = {
    "Conflicto armado": "var(--topic-conflicto)",
    "DDHH": "var(--topic-ddhh)",
    "DIH": "var(--topic-dih)",
    "Internacional": "var(--topic-internacional)",
    "Mercenarismo": "var(--topic-mercenarismo)",
    "General": "var(--topic-general)",
  };

  function tiempoRelativo(fechaISO) {
    const fecha = new Date(fechaISO);
    const ahora = new Date();
    const diffMs = ahora - fecha;
    const diffMin = Math.round(diffMs / 60000);
    if (diffMin < 1) return "AHORA";
    if (diffMin < 60) return `HACE ${diffMin} MIN`;
    const diffH = Math.round(diffMin / 60);
    if (diffH < 24) return `HACE ${diffH} H`;
    const diffD = Math.round(diffH / 24);
    if (diffD === 1) return "HACE 1 D";
    return `HACE ${diffD} D`;
  }

  function iniciarReloj() {
    const clockEl = document.getElementById("clock");
    if (!clockEl) return;
    const tick = () => {
      const ahora = new Date();
      const hh = String(ahora.getHours()).padStart(2, "0");
      const mm = String(ahora.getMinutes()).padStart(2, "0");
      const ss = String(ahora.getSeconds()).padStart(2, "0");
      clockEl.textContent = `${hh}:${mm}:${ss}`;
    };
    tick();
    setInterval(tick, 1000);
  }

  function poblarSelectFuentes(noticias) {
    const fuentes = Array.from(new Set(noticias.map((n) => n.fuente))).sort();
    els.sourceSelect.innerHTML = '<option value="Todos">TODAS LAS FUENTES</option>';
    fuentes.forEach((f) => {
      const opt = document.createElement("option");
      opt.value = f;
      opt.textContent = f;
      els.sourceSelect.appendChild(opt);
    });
  }

  function normalizar(texto) {
    return (texto || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  }

  function filtrar() {
    const q = normalizar(state.query);
    return state.noticias.filter((n) => {
      if (state.topic !== "Todos" && !n.temas.includes(state.topic)) return false;
      if (state.source !== "Todos" && n.fuente !== state.source) return false;
      if (q) {
        const texto = normalizar(`${n.titulo} ${n.fuente} ${n.seccion} ${(n.palabras_clave || []).join(" ")}`);
        if (!texto.includes(q)) return false;
      }
      return true;
    });
  }

  function render() {
    const resultado = filtrar();
    els.list.innerHTML = "";
    els.empty.classList.toggle("hidden", resultado.length > 0);

    const frag = document.createDocumentFragment();
    resultado.forEach((n) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.className = "news-card";
      a.href = n.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      const temaPrincipal = (n.temas || ["General"])[0];
      a.style.setProperty("--card-accent", TOPIC_VAR[temaPrincipal] || "var(--topic-general)");

      const meta = document.createElement("div");
      meta.className = "card-meta";
      const reportId = "REG-" + (n.id || "000000").toUpperCase();
      meta.innerHTML = `<span class="report-id">${escapeHtml(reportId)}</span><span class="dot">·</span><span class="source-name">${escapeHtml(n.fuente)}</span><span class="time-ago">${tiempoRelativo(n.fecha)}</span>`;

      const titulo = document.createElement("p");
      titulo.className = "card-title";
      titulo.textContent = n.titulo;

      const tags = document.createElement("div");
      tags.className = "topic-tags";
      (n.temas || ["General"]).forEach((t) => {
        const span = document.createElement("span");
        span.className = "tag " + (TAG_CLASS[t] || "tag-general");
        span.textContent = "[ " + t.toUpperCase() + " ]";
        tags.appendChild(span);
      });

      a.appendChild(meta);
      a.appendChild(titulo);
      a.appendChild(tags);
      li.appendChild(a);
      frag.appendChild(li);
    });
    els.list.appendChild(frag);

    els.status.textContent = state.generadoEn
      ? `${resultado.length} REGISTROS · SYNC ${tiempoRelativo(state.generadoEn)}`
      : `${resultado.length} REGISTROS`;
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function mostrarSkeleton() {
    els.list.innerHTML = "";
    for (let i = 0; i < 5; i++) {
      const li = document.createElement("li");
      li.className = "skeleton";
      li.innerHTML = `<div class="skeleton-line" style="width:40%"></div><div class="skeleton-line" style="width:90%"></div><div class="skeleton-line" style="width:60%"></div>`;
      els.list.appendChild(li);
    }
  }

  async function cargarDatos() {
    mostrarSkeleton();
    els.refreshBtn.classList.add("spinning");
    let datos = null;
    try {
      const resp = await fetch(DATA_URL, { cache: "no-store" });
      if (resp.ok) datos = await resp.json();
    } catch (e) {
      datos = null;
    }
    els.refreshBtn.classList.remove("spinning");

    if (!datos) {
      els.status.textContent = "ERROR DE ENLACE — SIN DATOS NUEVOS";
      els.offlineBanner.classList.remove("hidden");
      render();
      return;
    }

    els.offlineBanner.classList.add("hidden");
    state.noticias = datos.noticias || [];
    state.generadoEn = datos.generado_en || null;
    poblarSelectFuentes(state.noticias);
    render();
  }

  function formatFechaLarga(fechaISO) {
    try {
      return new Date(fechaISO).toLocaleDateString("es-CO", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    } catch (e) {
      return fechaISO;
    }
  }

  let informesIndexCache = null;

  async function cargarInformesIndex() {
    if (informesIndexCache) return informesIndexCache;
    try {
      const resp = await fetch("data/informes/index.json?_=" + Date.now(), { cache: "no-store" });
      if (!resp.ok) return null;
      informesIndexCache = await resp.json();
      return informesIndexCache;
    } catch (e) {
      return null;
    }
  }

  function renderInformesLista(data) {
    els.informesLista.innerHTML = "";
    const informes = (data && data.informes) || [];
    els.informesVacio.classList.toggle("hidden", informes.length > 0);
    informes.forEach((inf) => {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.className = "informe-item";
      btn.innerHTML = `
        <span class="informe-item-titulo">${escapeHtml(inf.titulo)}</span>
        <span class="informe-item-meta">${escapeHtml(inf.desde)} → ${escapeHtml(inf.hasta)} · ${inf.total} noticia(s)</span>
      `;
      btn.addEventListener("click", () => abrirInforme(inf));
      li.appendChild(btn);
      els.informesLista.appendChild(li);
    });
  }

  async function abrirInforme(infMeta) {
    let informe = null;
    try {
      const resp = await fetch("data/informes/" + infMeta.archivo + "?_=" + Date.now(), { cache: "no-store" });
      if (resp.ok) informe = await resp.json();
    } catch (e) {
      informe = null;
    }
    if (!informe) return;

    els.informesDetalleTitulo.textContent = informe.titulo;
    els.informesDetalleMeta.textContent = `${informe.desde} → ${informe.hasta} · ${informe.total} noticia(s) · generado ${formatFechaLarga(informe.generado_en)}`;
    els.informesDetalleLista.innerHTML = "";

    const frag = document.createDocumentFragment();
    (informe.noticias || []).forEach((n) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.className = "news-card";
      a.href = n.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.style.setProperty("--card-accent", "var(--topic-mercenarismo)");

      const meta = document.createElement("div");
      meta.className = "card-meta";
      meta.innerHTML = `<span class="source-name">${escapeHtml(n.medio)}</span><span class="dot">·</span><span class="time-ago">${escapeHtml((n.fecha || "").slice(0, 10))}</span>`;

      const titulo = document.createElement("p");
      titulo.className = "card-title";
      titulo.textContent = n.titulo;

      const resumen = document.createElement("p");
      resumen.className = "informe-item-resumen";
      resumen.textContent = n.resumen || "";

      a.appendChild(meta);
      a.appendChild(titulo);
      if (n.resumen) a.appendChild(resumen);
      li.appendChild(a);
      frag.appendChild(li);
    });
    els.informesDetalleLista.appendChild(frag);

    els.informesListaView.classList.add("hidden");
    els.informesDetalleView.classList.remove("hidden");
  }

  async function abrirInformes() {
    els.informesOverlay.classList.remove("hidden");
    els.informesListaView.classList.remove("hidden");
    els.informesDetalleView.classList.add("hidden");
    const data = await cargarInformesIndex();
    renderInformesLista(data);
  }

  function cerrarInformes() {
    els.informesOverlay.classList.add("hidden");
  }

  if (els.informesBtn) {
    els.informesBtn.addEventListener("click", abrirInformes);
    els.informesClose.addEventListener("click", cerrarInformes);
    els.informesOverlay.addEventListener("click", (e) => {
      if (e.target === els.informesOverlay) cerrarInformes();
    });
    els.informesVolver.addEventListener("click", () => {
      els.informesDetalleView.classList.add("hidden");
      els.informesListaView.classList.remove("hidden");
    });
  }

  els.chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      els.chips.forEach((c) => {
        c.classList.remove("active");
        c.setAttribute("aria-selected", "false");
      });
      chip.classList.add("active");
      chip.setAttribute("aria-selected", "true");
      state.topic = chip.dataset.topic;
      render();
    });
  });

  els.sourceSelect.addEventListener("change", (e) => {
    state.source = e.target.value;
    render();
  });

  let debounceTimer;
  els.search.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      state.query = e.target.value;
      render();
    }, 150);
  });

  els.refreshBtn.addEventListener("click", cargarDatos);

  window.addEventListener("online", () => els.offlineBanner.classList.add("hidden"));
  window.addEventListener("offline", () => els.offlineBanner.classList.remove("hidden"));

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("service-worker.js").catch(() => {});
    });
  }

  iniciarReloj();
  cargarDatos();
})();
