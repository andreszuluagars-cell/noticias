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
  };

  const TAG_CLASS = {
    "Conflicto armado": "tag-conflicto",
    "DDHH": "tag-ddhh",
    "DIH": "tag-dih",
    "General": "tag-general",
  };

  function tiempoRelativo(fechaISO) {
    const fecha = new Date(fechaISO);
    const ahora = new Date();
    const diffMs = ahora - fecha;
    const diffMin = Math.round(diffMs / 60000);
    if (diffMin < 1) return "justo ahora";
    if (diffMin < 60) return `hace ${diffMin} min`;
    const diffH = Math.round(diffMin / 60);
    if (diffH < 24) return `hace ${diffH} h`;
    const diffD = Math.round(diffH / 24);
    if (diffD === 1) return "hace 1 día";
    return `hace ${diffD} días`;
  }

  function poblarSelectFuentes(noticias) {
    const fuentes = Array.from(new Set(noticias.map((n) => n.fuente))).sort();
    els.sourceSelect.innerHTML = '<option value="Todos">Todos los diarios</option>';
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

      const meta = document.createElement("div");
      meta.className = "card-meta";
      meta.innerHTML = `<span class="source-name">${escapeHtml(n.fuente)}</span><span class="dot">•</span><span class="time-ago">${tiempoRelativo(n.fecha)}</span>`;

      const titulo = document.createElement("p");
      titulo.className = "card-title";
      titulo.textContent = n.titulo;

      const tags = document.createElement("div");
      tags.className = "topic-tags";
      (n.temas || ["General"]).forEach((t) => {
        const span = document.createElement("span");
        span.className = "tag " + (TAG_CLASS[t] || "tag-general");
        span.textContent = t;
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
      ? `${resultado.length} noticias · actualizado ${tiempoRelativo(state.generadoEn)}`
      : `${resultado.length} noticias`;
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
      els.status.textContent = "No se pudo cargar. Mostrando datos guardados si existen.";
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

  cargarDatos();
})();
