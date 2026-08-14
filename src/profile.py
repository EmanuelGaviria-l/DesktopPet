import json
import os

# El perfil del usuario (su nombre) se guarda una sola vez, la primera
# vez que abre la app. En sesiones futuras, si el archivo ya existe,
# nos saltamos la pantalla de bienvenida por completo.
PROFILE_PATH = "data/profile.json"


def _ensure_data_folder():
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)


def load_profile() -> dict | None:
    """Devuelve el perfil guardado, o None si es la primera vez que se abre la app."""
    if not os.path.exists(PROFILE_PATH):
        return None

    with open(PROFILE_PATH, "r") as f:
        return json.load(f)


def save_profile(user_name: str):
    """Guarda el nombre del usuario para que la app lo recuerde en el futuro."""
    _ensure_data_folder()
    with open(PROFILE_PATH, "w") as f:
        json.dump({"user_name": user_name}, f, indent=2)