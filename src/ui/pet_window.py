import sys
import random
from typing import Optional
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMenu
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QMouseEvent, QTransform


class PetWindow(QWidget):
    # --- Señales que pet.py escucha para reaccionar a lo que pasa en la ventana ---
    dragged = pyqtSignal(QPoint)
    feed_requested = pyqtSignal()          # usuario eligio "Alimentar" en el menu
    play_requested = pyqtSignal()          # usuario eligio "Jugar" en el menu
    assign_task_requested = pyqtSignal()   # usuario eligio "Asignar tarea" en el menu

    # --- Configuracion de movimiento y animacion (ajustable) ---
    WALK_SPEED = 3
    MIN_IDLE_MS = 1500
    MAX_IDLE_MS = 4000
    SCREEN_MARGIN = 40
    ANIMATION_MS = 200
    SPRITE_SCALE = 4
    CLICK_DRAG_THRESHOLD = 6  # pixeles: si te mueves menos que esto, cuenta como "click", no arrastre

    def __init__(self):
        super().__init__()

        # --- Configuracion de la ventana: sin bordes, fondo transparente ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

        # --- Sistema de animacion: cada "estado" tiene su lista de frames ---
        self._animations: dict[str, list[QPixmap]] = {}
        self._current_state: Optional[str] = None
        self._frame_index = 0
        self._facing_right = True

        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._advance_frame)
        self._anim_timer.start(self.ANIMATION_MS)

        self.resize(128, 128)  # tamano por defecto hasta que cargue el primer sprite

        # --- Estado del mouse: distinguir "click rapido" de "arrastrar" ---
        self._drag_offset = QPoint()
        self._press_global_pos = QPoint()  # donde se presiono el mouse, para medir si hubo arrastre real
        self._dragging = False
        self._moved_past_threshold = False

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 200, screen.height() - 200)

        # --- Movimiento autonomo: la mascota camina sola por la pantalla ---
        self._walking = False
        self._target_x = float(self.x())
        self._target_y = float(self.y())
        self._pos_x = float(self.x())
        self._pos_y = float(self.y())

        self._idle_timer = QTimer(self)
        self._idle_timer.setSingleShot(True)
        self._idle_timer.timeout.connect(self._pick_new_target)

        self._move_timer = QTimer(self)
        self._move_timer.timeout.connect(self._step_movement)
        self._move_timer.start(1000 // 30)

        self._pick_new_target()

    def bring_to_front(self):
        """Se llama solo cuando la mascota necesita interrumpir (ej: burbuja de recordatorio)."""
        self.raise_()

    # ============================================================
    # ANIMACION
    # ============================================================

    def load_state_frames(self, state: str, frame_paths: list[str]):
        """
        Carga una o mas imagenes como la animacion de un estado.
        Una sola imagen = animacion "estatica" (funciona igual, solo no cicla).
        Varias imagenes = van a ciclar en orden, en loop, cada ANIMATION_MS.
        """
        frames = []
        for path in frame_paths:
            pixmap = QPixmap(path)
            if pixmap.isNull():
                continue
            scaled = pixmap.scaled(
                pixmap.width() * self.SPRITE_SCALE,
                pixmap.height() * self.SPRITE_SCALE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
            frames.append(scaled)

        if frames:
            self._animations[state] = frames
            if self._current_state is None:
                self.play_state(state)

    def play_state(self, state: str):
        """Cambia a otra animacion (ej: 'idle', 'hungry', 'dead')."""
        if state not in self._animations or state == self._current_state:
            return
        self._current_state = state
        self._frame_index = 0
        self._render_current_frame()

    def _advance_frame(self):
        if self._current_state is None:
            return
        frames = self._animations[self._current_state]
        if len(frames) <= 1:
            return
        self._frame_index = (self._frame_index + 1) % len(frames)
        self._render_current_frame()

    def _render_current_frame(self):
        if self._current_state is None:
            return
        frames = self._animations[self._current_state]
        frame = frames[self._frame_index]

        if self._facing_right:
            frame = frame.transformed(QTransform().scale(-1, 1))

        self.label.setPixmap(frame)
        self.resize(frame.size())
        self.setMask(frame.mask())  # solo el area visible del sprite recibe clicks

    # ============================================================
    # MOVIMIENTO AUTONOMO
    # ============================================================

    def _pick_new_target(self):
        """Elige un punto aleatorio de la pantalla y empieza a caminar hacia el."""
        screen = QApplication.primaryScreen().geometry()
        max_x = screen.width() - self.width() - self.SCREEN_MARGIN
        max_y = screen.height() - self.height() - self.SCREEN_MARGIN
        self._target_x = float(random.randint(self.SCREEN_MARGIN, max(max_x, self.SCREEN_MARGIN)))
        self._target_y = float(random.randint(self.SCREEN_MARGIN, max(max_y, self.SCREEN_MARGIN)))
        self._facing_right = self._target_x >= self._pos_x
        self._render_current_frame()
        self._walking = True

    def _step_movement(self):
        """Se ejecuta ~30 veces por segundo: mueve la mascota un poco hacia su destino."""
        if self._dragging or not self._walking:
            return

        dx = self._target_x - self._pos_x
        dy = self._target_y - self._pos_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance <= self.WALK_SPEED:
            # Llego al destino: para y descansa un rato antes de elegir el siguiente
            self._pos_x, self._pos_y = self._target_x, self._target_y
            self.move(int(self._pos_x), int(self._pos_y))
            self._walking = False
            idle_duration = random.randint(self.MIN_IDLE_MS, self.MAX_IDLE_MS)
            self._idle_timer.start(idle_duration)
            return

        # Avanza un paso en linea recta hacia el destino
        self._pos_x += (dx / distance) * self.WALK_SPEED
        self._pos_y += (dy / distance) * self.WALK_SPEED
        self.move(int(self._pos_x), int(self._pos_y))

    # ============================================================
    # MOUSE: distinguir click rapido (abre menu) de arrastre (mueve la mascota)
    # ============================================================

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._moved_past_threshold = False
            self._walking = False
            self._idle_timer.stop()
            self._press_global_pos = event.globalPosition().toPoint()
            self._drag_offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._dragging:
            return

        current_global = event.globalPosition().toPoint()

        # Medimos que tan lejos nos hemos movido desde que presionamos el mouse.
        # Si supera el umbral, esto ya es un "arrastre" real, no un click rapido.
        distance_from_press = (current_global - self._press_global_pos).manhattanLength()
        if distance_from_press > self.CLICK_DRAG_THRESHOLD:
            self._moved_past_threshold = True

        new_pos = current_global - self._drag_offset
        self.move(new_pos)
        self._pos_x, self._pos_y = float(new_pos.x()), float(new_pos.y())
        self.dragged.emit(new_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self._dragging = False

        if self._moved_past_threshold:
            # Fue un arrastre real: al soltar, retoma el paseo normal
            self._pick_new_target()
        else:
            # Fue un click rapido (sin mover el mouse): abrir el menu de opciones
            self._show_options_menu(event.globalPosition().toPoint())

    def _show_options_menu(self, global_pos: QPoint):
        """Construye y muestra el menu con las acciones disponibles sobre la mascota."""
        menu = QMenu(self)
        feed_action = menu.addAction("🍖 Alimentar")
        play_action = menu.addAction("🎾 Jugar")
        task_action = menu.addAction("📋 Asignar tarea")

        chosen = menu.exec(global_pos)

        if chosen == feed_action:
            self.feed_requested.emit()
        elif chosen == play_action:
            self.play_requested.emit()
        elif chosen == task_action:
            self.assign_task_requested.emit()

        # Despues de cerrar el menu, retoma el paseo normal
        self._pick_new_target()


def run_standalone():
    app = QApplication(sys.argv)
    pet = PetWindow()
    pet.load_state_frames("idle", ["assets/cat_test.png"])
    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_standalone()