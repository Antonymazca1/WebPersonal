// ====== Datos ======
const FRASES = [
  "Hoy cuenta.",
  "Un paso a la vez.",
  "Respira. Vuelve. Intenta.",
  "No estás tarde. Estás creciendo.",
  "Tu enfoque es tu poder.",
  "La disciplina te salva.",
  "Hazlo simple, pero hazlo.",
  "Aunque sea lento, sigue.",
  "Lo que haces hoy te construye.",
  "Sé constante, no perfecto."
];

const LS_KEY = "favoritos_inspiracion";

// ====== Favoritos (LocalStorage) ======
function getFavoritos() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function setFavoritos(arr) {
  localStorage.setItem(LS_KEY, JSON.stringify(arr));
}

function isFav(texto) {
  return getFavoritos().includes(texto);
}

function addFav(texto) {
  const favs = getFavoritos();
  if (!favs.includes(texto)) {
    favs.push(texto);
    setFavoritos(favs);
  }
}

function removeFav(texto) {
  const favs = getFavoritos().filter(f => f !== texto);
  setFavoritos(favs);
}

function renderFavoritos() {
  const list = document.getElementById("favoritosList");
  const empty = document.getElementById("favEmpty");
  if (!list || !empty) return;

  const favs = getFavoritos();
  list.innerHTML = "";

  if (favs.length === 0) {
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";

  favs.forEach((txt) => {
    const card = document.createElement("div");
    card.className = "card";

    const p = document.createElement("p");
    p.className = "quote smallq";
    p.textContent = txt;

    const btn = document.createElement("button");
    btn.className = "btn small ghost";
    btn.type = "button";
    btn.textContent = "Eliminar";
    btn.addEventListener("click", () => {
      removeFav(txt);
      renderFavoritos();
    });

    card.appendChild(p);
    card.appendChild(btn);
    list.appendChild(card);
  });
}

// ====== Utilidad ======
function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// ====== Página Inicio: “Motívame ahora” ======
function setupHome() {
  const motivarBtn = document.getElementById("motivarBtn");
  const heroFrase = document.getElementById("heroFrase");
  const favHeroBtn = document.getElementById("favHeroBtn");
  const heroInfo = document.getElementById("heroInfo");

  if (!motivarBtn || !heroFrase || !favHeroBtn) return;

  let actual = "";

  function updateFavButton() {
    if (!actual) {
      favHeroBtn.disabled = true;
      return;
    }
    const exists = isFav(actual);
    favHeroBtn.disabled = false;
    favHeroBtn.textContent = exists ? "Guardado ✅" : "Guardar en favoritos";
    if (heroInfo) heroInfo.textContent = exists ? "Ya está en favoritos." : "";
  }

  motivarBtn.addEventListener("click", () => {
    actual = randomItem(FRASES);
    heroFrase.textContent = actual;
    updateFavButton();
  });

  favHeroBtn.addEventListener("click", () => {
    if (!actual) return;
    addFav(actual);
    updateFavButton();
  });
}

// ====== Página Frases: generador ======
function setupFrases() {
  const generar = document.getElementById("generarFraseBtn");
  const guardar = document.getElementById("guardarFraseBtn");
  const out = document.getElementById("fraseActual");
  const info = document.getElementById("fraseInfo");

  if (!generar || !guardar || !out) return;

  let actual = "";

  function refresh() {
    if (!actual) {
      guardar.disabled = true;
      return;
    }
    guardar.disabled = false;
    const exists = isFav(actual);
    guardar.textContent = exists ? "Guardado ✅" : "Guardar";
    if (info) info.textContent = exists ? "Ya estaba en favoritos." : "";
  }

  generar.addEventListener("click", () => {
    actual = randomItem(FRASES);
    out.textContent = actual;
    refresh();
  });

  guardar.addEventListener("click", () => {
    if (!actual) return;
    addFav(actual);
    refresh();
  });
}

// ====== Botones “Guardar” (data-fav) en cards ======
function setupQuickFavButtons() {
  const buttons = document.querySelectorAll("[data-fav]");
  if (!buttons.length) return;

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const txt = btn.getAttribute("data-fav");
      if (!txt) return;
      addFav(txt);
      btn.textContent = "Guardado ✅";
      btn.disabled = true;
    });
  });
}

// ====== Página Favoritos ======
function setupFavoritosPage() {
  const limpiar = document.getElementById("limpiarFavBtn");
  if (limpiar) {
    limpiar.addEventListener("click", () => {
      setFavoritos([]);
      renderFavoritos();
    });
  }
  renderFavoritos();
}

// ====== Validación formulario contacto ======
function setupContactoForm() {
  const form = document.getElementById("contactForm");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    const nombre = document.getElementById("nombre").value.trim();
    const correo = document.getElementById("correo").value.trim();
    const mensaje = document.getElementById("mensaje").value.trim();
    const err = document.getElementById("formError");

    let msg = "";
    if (nombre.length < 2) msg = "Tu nombre debe tener al menos 2 caracteres.";
    else if (!correo.includes("@")) msg = "Correo inválido (falta @).";
    else if (mensaje.length < 10) msg = "El mensaje debe tener al menos 10 caracteres.";

    if (msg) {
      e.preventDefault();
      err.textContent = msg;
      err.style.display = "block";
    }
  });
}

// ====== Init ======
document.addEventListener("DOMContentLoaded", () => {
  setupHome();
  setupFrases();
  setupQuickFavButtons();
  setupFavoritosPage();
  setupContactoForm();
});
