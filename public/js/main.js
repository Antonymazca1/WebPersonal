// Modo oscuro (guardado)
const themeBtnId = "themeToggle";
const savedTheme = localStorage.getItem("theme");
if (savedTheme) document.documentElement.setAttribute("data-theme", savedTheme);

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
}

// Validación simple formulario
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("contactForm");
  if (form) {
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
});
