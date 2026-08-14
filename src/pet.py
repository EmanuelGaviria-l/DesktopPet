import time
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from src.ui.pet_window import PetWindow
from src import cemetery


class Pet(QObject):
    """
    El "cerebro" del Tamagotchi: controla hambre, energia y felicidad.
    Si el hambre llega a 0, entra en un periodo de gracia ("starving")
    de STARVATION_GRACE_MS. Si se alimenta a tiempo, se salva. Si no,
    muere de forma permanente cuando se acaba ese plazo.
    """

    died = pyqtSignal(str, float)
    stats_changed = pyqtSignal(dict)  # avisa cada vez que hunger/energy/happiness cambian

    # --- Calculado para que, sin cuidar la mascota, el hambre llegue
    # a 0 en aproximadamente 7 horas (420 minutos, tick cada 1 min).
    # Energia y felicidad bajan mas lento, ya que no son letales.
    DECAY_PER_TICK = {"hunger": 0.24, "energy": 0.12, "happiness": 0.12}
    TICK_MS = 60_000  # un tick cada minuto

    STARVATION_GRACE_MS = 20 * 60 * 1000  # 20 minutos de gracia en 0 antes de morir
    DEATH_ANIMATION_DELAY_MS = 2500  # cuanto se ve la animacion "dead" antes del aviso final

    def __init__(self, name: str, sprite_path: str):
        super().__init__()
        self.name = name
        self._birth_time = time.time()

        # --- Ventana y animaciones ---
        self.window = PetWindow()
        self.window.load_state_frames("idle", [sprite_path])
        self.window.load_state_frames("hungry", [sprite_path])
        self.window.load_state_frames("bored", [sprite_path])
        self.window.load_state_frames("happy", [sprite_path])
        self.window.load_state_frames("starving", [sprite_path])  # TODO: sprite distinto, mas urgente
        self.window.load_state_frames("dead", [sprite_path])       # TODO: sprite de "muerto" real
        self.window.play_state("idle")

        # --- Stats del Tamagotchi ---
        self.stats = {"hunger": 100, "energy": 100, "happiness": 100}
        self.state = "idle"
        self._alive = True

        # --- Periodo de gracia por inanicion ---
        self._starving = False
        self._starvation_timer = QTimer()
        self._starvation_timer.setSingleShot(True)
        self._starvation_timer.timeout.connect(self._on_starvation_timeout)

        # --- El menu de la ventana avisa aqui que opcion eligio el usuario ---
        self.window.feed_requested.connect(lambda: self.feed())
        self.window.play_requested.connect(lambda: self.play())
        self.window.assign_task_requested.connect(self._on_assign_task_requested)

        # --- Timer que hace bajar las stats solas con el tiempo ---
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.TICK_MS)

    # ============================================================
    # API PUBLICA
    # ============================================================

    def feed(self, amount: int = 20):
        if not self._alive:
            return
        self._adjust("hunger", amount)

    def play(self, amount: int = 15):
        if not self._alive:
            return
        self._adjust("happiness", amount)
        self._adjust("energy", -5)

    def rest(self, amount: int = 30):
        if not self._alive:
            return
        self._adjust("energy", amount)

    def get_state(self) -> str:
        return self.state

    def is_alive(self) -> bool:
        return self._alive

    # ============================================================
    # INTERNOS
    # ============================================================

    def _tick(self):
        self._adjust("hunger", -self.DECAY_PER_TICK["hunger"])
        self._adjust("energy", -self.DECAY_PER_TICK["energy"])
        self._adjust("happiness", -self.DECAY_PER_TICK["happiness"])

    def _adjust(self, stat: str, amount: float):
        self.stats[stat] = max(0, min(100, self.stats[stat] + amount))
        self.stats_changed.emit(self.stats)
        self._update_state()

    def _update_state(self):
        if not self._alive:
            return

        prev_state = self.state

        # --- Hambre en 0: entra (o se mantiene) en periodo de gracia ---
        if self.stats["hunger"] <= 0:
            if not self._starving:
                # Primera vez que llega a 0: arrancamos el reloj de gracia
                self._starving = True
                self._starvation_timer.start(self.STARVATION_GRACE_MS)
            self.state = "starving"
            if self.state != prev_state:
                self.window.play_state("starving")
            return

        # --- Si se alimento a tiempo durante el periodo de gracia, se salva ---
        if self._starving:
            self._starving = False
            self._starvation_timer.stop()

        # --- Estados normales ---
        if self.stats["hunger"] <= 30:
            self.state = "hungry"
        elif self.stats["happiness"] <= 30:
            self.state = "bored"
        elif self.stats["happiness"] >= 80 and self.stats["hunger"] >= 60:
            self.state = "happy"
        else:
            self.state = "idle"

        if self.state != prev_state:
            self.window.play_state(self.state)

    def _on_starvation_timeout(self):
        """Se acabo el periodo de gracia sin comer: la mascota muere, de forma permanente."""
        if not self._alive or self.stats["hunger"] > 0:
            return  # se salvo justo a tiempo, no hacer nada

        self.state = "dead"
        self._alive = False
        self._timer.stop()
        self.window.play_state("dead")

        QTimer.singleShot(self.DEATH_ANIMATION_DELAY_MS, self._finalize_death)

    def _finalize_death(self):
        """Se ejecuta despues de ver la animacion 'dead': guarda el registro y avisa a main.py."""
        seconds_alive = time.time() - self._birth_time
        cemetery.save_death_record(self.name, seconds_alive)
        self.died.emit(self.name, seconds_alive)

    def _on_assign_task_requested(self):
        print("[pet] Asignar tarea seleccionado — funcionalidad pendiente")