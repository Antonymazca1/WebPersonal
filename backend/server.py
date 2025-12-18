from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import os, secrets, html

from config import ADMIN_PASSWORD, SESSION_COOKIE, DATA_FILE
from storage import add_message, list_messages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "public")
DATA_PATH = os.path.join(BASE_DIR, "data", DATA_FILE)

SESSIONS = set()

def read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def guess_content_type(path: str) -> str:
    if path.endswith(".html"): return "text/html; charset=utf-8"
    if path.endswith(".css"):  return "text/css; charset=utf-8"
    if path.endswith(".js"):   return "application/javascript; charset=utf-8"
    if path.endswith(".png"):  return "image/png"
    if path.endswith(".jpg") or path.endswith(".jpeg"): return "image/jpeg"
    if path.endswith(".svg"):  return "image/svg+xml"
    return "application/octet-stream"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Rutas principales
        if path == "/": return self.serve_static("index.html")
        if path == "/mensajes": return self.serve_static("mensajes.html")
        if path == "/frases": return self.serve_static("frases.html")
        if path == "/favoritos": return self.serve_static("favoritos.html")
        if path == "/contacto": return self.serve_static("contacto.html")
        if path == "/login": return self.serve_static("login.html")
        if path == "/gracias": return self.serve_static("gracias.html")

        if path == "/logout":
            self.send_response(302)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; Max-Age=0; Path=/")
            self.end_headers()
            return

        if path == "/admin":
            if not self.is_logged_in():
                self.send_response(302)
                self.send_header("Location", "/login")
                self.end_headers()
                return
            return self.render_admin()

        # Estáticos (css/js/img)
        safe = os.path.normpath(path).lstrip("/").replace("..", "")
        file_path = os.path.join(PUBLIC_DIR, safe)

        if os.path.isfile(file_path):
            return self.serve_file(file_path)

        self.send_error(404, "No encontrado")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="ignore")
        data = parse_qs(body)

        if path == "/enviar_contacto":
            nombre = (data.get("nombre", [""])[0]).strip()
            correo = (data.get("correo", [""])[0]).strip()
            mensaje = (data.get("mensaje", [""])[0]).strip()

            # Validación mínima servidor
            if not nombre or not correo or not mensaje or "@" not in correo:
                return self.simple_html(400, "Datos inválidos. Regresa e inténtalo de nuevo.")

            add_message(DATA_PATH, nombre, correo, mensaje)

            self.send_response(302)
            self.send_header("Location", "/gracias")
            self.end_headers()
            return

        if path == "/login":
            password = (data.get("password", [""])[0]).strip()
            if password == ADMIN_PASSWORD:
                sid = secrets.token_hex(16)
                SESSIONS.add(sid)
                self.send_response(302)
                self.send_header("Location", "/admin")
                self.send_header("Set-Cookie", f"{SESSION_COOKIE}={sid}; HttpOnly; Path=/")
                self.end_headers()
                return
            return self.simple_html(401, "Contraseña incorrecta. Regresa e inténtalo.")

        self.send_error(404, "Ruta POST no encontrada")

    def serve_static(self, filename: str):
        return self.serve_file(os.path.join(PUBLIC_DIR, filename))

    def serve_file(self, file_path: str):
        try:
            content = read_file(file_path)
            self.send_response(200)
            self.send_header("Content-Type", guess_content_type(file_path))
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "Archivo no encontrado")

    def get_cookie(self, name: str):
        cookie = self.headers.get("Cookie", "")
        parts = [c.strip() for c in cookie.split(";") if "=" in c]
        for p in parts:
            k, v = p.split("=", 1)
            if k == name:
                return v
        return None

    def is_logged_in(self) -> bool:
        sid = self.get_cookie(SESSION_COOKIE)
        return sid in SESSIONS if sid else False

    def render_admin(self):
        rows = list_messages(DATA_PATH)

        trs = []
        for r in rows:
            trs.append(
                "<tr>"
                f"<td>{r['id']}</td>"
                f"<td>{html.escape(r['nombre'])}</td>"
                f"<td>{html.escape(r['correo'])}</td>"
                f"<td>{html.escape(r['mensaje'])}</td>"
                f"<td>{r['fecha']}</td>"
                "</tr>"
            )

        page = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Admin - Mensajes</title>
  <link rel="stylesheet" href="/css/styles.css">
</head>
<body>
  <header class="topbar">
    <div class="brand">Panel Admin</div>
    <nav class="nav">
      <a href="/">Inicio</a>
      <a href="/logout">Salir</a>
    </nav>
  </header>

  <main class="container">
    <h1>Mensajes recibidos</h1>
    <div class="card">
      <div style="overflow:auto;">
        <table class="table">
          <thead>
            <tr><th>ID</th><th>Nombre</th><th>Correo</th><th>Mensaje</th><th>Fecha</th></tr>
          </thead>
          <tbody>
            {"".join(trs) if trs else "<tr><td colspan='5'>No hay mensajes todavía.</td></tr>"}
          </tbody>
        </table>
      </div>
    </div>
  </main>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))

    def simple_html(self, code: int, msg: str):
        page = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Error</title><link rel="stylesheet" href="/css/styles.css"></head>
<body><main class="container"><div class="card"><h2>Error</h2><p>{html.escape(msg)}</p>
<p><a href="/">Volver</a></p></div></main></body></html>"""
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))

if __name__ == "__main__":
    host, port = "127.0.0.1", 8000
    httpd = HTTPServer((host, port), Handler)
    print(f"Servidor corriendo en http://{host}:{port}")
    httpd.serve_forever()
