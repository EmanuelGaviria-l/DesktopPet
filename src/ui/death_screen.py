from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt


class DeathScreen(QWidget):
    """
    Pantalla que aparece cuando la mascota muere. Anuncia la muerte,
    muestra cuanto tiempo vivio, y da la opcion de volver al menu
    principal para crear una mascota nueva (no hay revivir).
    """

    # Se emite cuando el usuario presiona "Crear nueva mascota"
    return_to_menu_requested = pyqtSignal()

    def __init__(self, pet_name: str, seconds_alive: float):
        super().__init__()
        self.setWindowTitle("DesktopPet — En memoria")
        self.resize(340, 220)

        # --- Convertimos segundos a un formato legible (ej: "2 min 15 seg") ---
        minutes = int(seconds_alive // 60)
        seconds = int(seconds_alive % 60)
        time_text = f"{minutes} min {seconds} seg" if minutes > 0 else f"{seconds} seg"

        # --- Construccion de la interfaz ---
        layout = QVBoxLayout(self)

        title = QLabel("🕯️ En memoria")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        message = QLabel(f'"{pet_name}" ha fallecido.')
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("font-size: 14px;")
        layout.addWidget(message)

        stats = QLabel(f"Tiempo con vida: {time_text}")
        stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(stats)

        note = QLabel("Ninguna mascota vuelve a la vida.\nCrea una nueva para continuar.")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(note)

        new_pet_button = QPushButton("Crear nueva mascota")
        new_pet_button.clicked.connect(self.return_to_menu_requested.emit)
        layout.addWidget(new_pet_button)