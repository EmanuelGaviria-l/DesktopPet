import sys
import random
from typing import Optional
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMenu
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QMouseEvent, QTransform


class PetWindow(QWidget):
    dragged = pyqtSignal(QPoint)
    feed_requested = pyqtSignal()
    play_requested = pyqtSignal()
    assign_task_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    # Avisan cuando se abre/cierra el menu, con la posicion y tamano
    # de la ventana del gato, para que main.py pueda mostrar/ocultar
    # y posicionar la ventana de stats justo arriba de el.
    menu_opened = pyqtSignal(int, int, int, int)  # x, y, ancho, alto
    menu_closed = pyqtSignal()

    WALK_SPEED = 3
    MIN_IDLE_MS = 1500
    MAX_IDLE_MS = 4000
    SCREEN_MARGIN = 40
    ANIMATION_MS = 200
    SPRITE_SCALE = 4
    CLICK_DRAG_THRESHOLD = 6

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

        self._animations: dict[str, list[QPixmap]] = {}
        self._current_state: Optional[str] = None
        self._frame_index = 0
        self._facing_right = True

        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._advance_frame)
        self._anim_timer.start(self.ANIMATION_MS)

        self.resize(128, 128)

        self._drag_offset = QPoint()
        self._press_global_pos = QPoint()
        self._dragging = False
        self._moved_past_threshold = False

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 200, screen.height() - 200)

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
        self.raise_()

    # ============================================================
    # ANIMACION
    # ============================================================

    def load_state_frames(self, state: str, frame_paths: list[str]):
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
        self.setMask(frame.mask())

    # ============================================================
    # MOVIMIENTO AUTONOMO
    # ============================================================

    def _pick_new_target(self):
        screen = QApplication.primaryScreen().geometry()
        max_x = screen.width() - self.width() - self.SCREEN_MARGIN
        max_y = screen.height() - self.height() - self.SCREEN_MARGIN
        self._target_x = float(random.randint(self.SCREEN_MARGIN, max(max_x, self.SCREEN_MARGIN)))
        self._target_y = float(random.randint(self.SCREEN_MARGIN, max(max_y, self.SCREEN_MARGIN)))
        self._facing_right = self._target_x >= self._pos_x
        self._render_current_frame()
        self._walking = True

    def _step_movement(self):
        if self._dragging or not self._walking:
            return

        dx = self._target_x - self._pos_x
        dy = self._target_y - self._pos_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance <= self.WALK_SPEED:
            self._pos_x, self._pos_y = self._target_x, self._target_y
            self.move(int(self._pos_x), int(self._pos_y))
            self._walking = False
            idle_duration = random.randint(self.MIN_IDLE_MS, self.MAX_IDLE_MS)
            self._idle_timer.start(idle_duration)
            return

        self._pos_x += (dx / distance) * self.WALK_SPEED
        self._pos_y += (dy / distance) * self.WALK_SPEED
        self.move(int(self._pos_x), int(self._pos_y))

    # ============================================================
    # MOUSE
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
            self._pick_new_target()
        else:
            self.menu_opened.emit(self.x(), self.y(), self.width(), self.height())
            self._show_options_menu(event.globalPosition().toPoint())
            self.menu_closed.emit()

    def _show_options_menu(self, global_pos: QPoint):
        menu = QMenu(self)
        feed_action = menu.addAction("🍖 Alimentar")
        play_action = menu.addAction("🎾 Jugar")
        task_action = menu.addAction("📋 Asignar tarea")
        menu.addSeparator()
        quit_action = menu.addAction("❌ Cerrar DesktopPet")

        chosen = menu.exec(global_pos)

        if chosen == feed_action:
            self.feed_requested.emit()
        elif chosen == play_action:
            self.play_requested.emit()
        elif chosen == task_action:
            self.assign_task_requested.emit()
        elif chosen == quit_action:
            self.quit_requested.emit()
            return

        self._pick_new_target()


def run_standalone():
    app = QApplication(sys.argv)
    pet = PetWindow()
    pet.load_state_frames("idle", ["assets/cat_test.png"])
    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_standalone()