import json
import os
from datetime import datetime

def _ensure_file(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def add_message(file_path: str, nombre: str, correo: str, mensaje: str):
    _ensure_file(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    next_id = (max([m["id"] for m in data]) + 1) if data else 1

    data.append({
        "id": next_id,
        "nombre": nombre,
        "correo": correo,
        "mensaje": mensaje,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def list_messages(file_path: str):
    _ensure_file(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # más recientes primero
    return list(reversed(data))
