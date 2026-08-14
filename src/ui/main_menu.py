from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
)
from PyQt6.QtCore import pyqtSignal, Qt


class MainMenu(QWidget):
    """
    Pantalla de inicio de la app: el usuario escoge un preset de mascota
    y le pone nombre antes de empezar a jugar. Cuando presiona "Comenzar",
    emite pet_selected con (nombre, ruta_del_sprite) para que main.py
    cree la mascota real.
    """

    # (nombre_elegido, ruta_del_sprite_preset)
    pet_selected = pyqtSignal(str, str)

    # --- Presets disponibles ---
    # Por ahora solo tenemos el sprite de prueba. Cuando lleguen mas
    # assets de Jose, solo hay que agregar entradas aqui — el resto
    # del menu ya sabe manejar cualquier cantidad de opciones.
    PRESETS = {
        "Gato": "assets/cat_test.png",
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DesktopPet — Nueva mascota")
        self.resize(320, 220)

        # --- Construccion de la interfaz ---
        layout = QVBoxLayout(self)

        title = QLabel("Crea tu mascota")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Nombre:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Michi")
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Elige tu mascota:"))
        self.preset_selector = QComboBox()
        self.preset_selector.addItems(self.PRESETS.keys())
        layout.addWidget(self.preset_selector)

        self.start_button = QPushButton("Comenzar")
        self.start_button.clicked.connect(self._on_start_clicked)
        layout.addWidget(self.start_button)

        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: red;")
        layout.addWidget(self.warning_label)

    def _on_start_clicked(self):
        """Valida el nombre y, si esta todo bien, avisa a main.py para crear la mascota."""
        name = self.name_input.text().strip()

        if not name:
            self.warning_label.setText("Por favor ponle un nombre a tu mascota.")
            return

        preset_name = self.preset_selector.currentText()
        sprite_path = self.PRESETS[preset_name]

        self.pet_selected.emit(name, sprite_path)