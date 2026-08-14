import json
import os

# Guardamos el cementerio como un archivo JSON simple en la carpeta data/.
# No es informacion sensible, pero es "datos del usuario en su maquina",
# no codigo — por eso data/ va en el .gitignore (cada quien tiene el suyo).
CEMETERY_PATH = "data/cemetery.json"


def _ensure_data_folder():
    os.makedirs(os.path.dirname(CEMETERY_PATH), exist_ok=True)


def save_death_record(name: str, seconds_alive: float):
    """Agrega una mascota fallecida al cementerio."""
    _ensure_data_folder()

    records = load_all()
    records.append({
        "name": name,
        "seconds_alive": round(seconds_alive),
    })

    with open(CEMETERY_PATH, "w") as f:
        json.dump(records, f, indent=2)


def load_all() -> list[dict]:
    """Devuelve la lista completa de mascotas fallecidas (vacia si no hay ninguna aun)."""
    if not os.path.exists(CEMETERY_PATH):
        return []

    with open(CEMETERY_PATH, "r") as f:
        return json.load(f)