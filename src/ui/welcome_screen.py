from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt


class WelcomeScreen(QWidget):
    """
    Pantalla que aparece SOLO la primera vez que se abre la app
    (como el setup inicial de una Mac nueva). Pregunta el nombre
    del usuario y lo guarda de forma permanente en profile.py.
    """

    # Se emite cuando el usuario confirma su nombre
    name_confirmed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenido a DesktopPet")
        self.resize(340, 200)

        # --- Construccion de la interfaz ---
        layout = QVBoxLayout(self)

        title = QLabel("¡Bienvenido! 👋")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Antes de empezar, ¿cómo te llamas?")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Tu nombre")
        layout.addWidget(self.name_input)

        self.continue_button = QPushButton("Continuar")
        self.continue_button.clicked.connect(self._on_continue_clicked)
        layout.addWidget(self.continue_button)

        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: red;")
        layout.addWidget(self.warning_label)

    def _on_continue_clicked(self):
        name = self.name_input.text().strip()

        if not name:
            self.warning_label.setText("Por favor escribe tu nombre.")
            return

        self.name_confirmed.emit(name)