from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt


class StatsBar(QWidget):
    """
    Ventana flotante que muestra hambre, energia y felicidad como
    3 barras VERTICALES lado a lado, con su icono debajo de cada una.
    Empieza oculta — main.py la muestra/oculta junto con el menu del gato.
    """

    BAR_HEIGHT = 70  # alto de cada barra vertical

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget#statsContainer {
                background-color: rgba(30, 30, 30, 180);
                border-radius: 6px;
            }
            QLabel { color: white; }
        """)
        self.setObjectName("statsContainer")

        # --- Layout principal: 3 columnas una al lado de la otra ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        self.hunger_bar = self._build_bar_column("🍖", main_layout)
        self.energy_bar = self._build_bar_column("⚡", main_layout)
        self.happiness_bar = self._build_bar_column("💛", main_layout)

        self.resize(100, self.BAR_HEIGHT + 40)

    def _build_bar_column(self, emoji: str, parent_layout: QHBoxLayout) -> QProgressBar:
        """Crea una columna con una barra vertical arriba y su icono debajo."""
        column = QVBoxLayout()
        column.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        bar = QProgressBar()
        bar.setOrientation(Qt.Orientation.Vertical)
        bar.setFixedHeight(self.BAR_HEIGHT)
        bar.setFixedWidth(18)
        bar.setRange(0, 100)
        bar.setValue(100)
        bar.setTextVisible(False)
        column.addWidget(bar, alignment=Qt.AlignmentFlag.AlignHCenter)

        icon_label = QLabel(emoji)
        column.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        parent_layout.addLayout(column)
        return bar

    def update_stats(self, stats: dict):
        """Se llama cada vez que Pet avisa que hunger/energy/happiness cambiaron."""
        self.hunger_bar.setValue(int(stats["hunger"]))
        self.energy_bar.setValue(int(stats["energy"]))
        self.happiness_bar.setValue(int(stats["happiness"]))

    def show_beside(self, pet_x: int, pet_y: int, pet_width: int, pet_height: int):
        """Se posiciona al lado izquierdo del gato, centrada verticalmente con el, y se muestra."""
        new_x = pet_x - self.width() - 8
        center_y = pet_y + (pet_height // 2)
        new_y = center_y - (self.height() // 2)
        self.move(new_x, new_y)
        self.show()