from PyQt6.QtCore import QTimer
from src.ui.pet_window import PetWindow


class Pet:
    """
    El "cerebro" del Tamagotchi: controla hambre, energia y felicidad,
    decide el estado actual, y reacciona a las opciones que el usuario
    elige en el menu de la mascota (Alimentar/Jugar/Asignar tarea).
    """

    DECAY_PER_TICK = {"hunger": 2, "energy": 1, "happiness": 1}
    TICK_MS = 30_000  # cada cuanto bajan las stats

    def __init__(self):
        # --- Ventana y animaciones ---
        self.window = PetWindow()
        self.window.load_state_frames("idle", ["assets/cat_test.png"])
        self.window.load_state_frames("hungry", ["assets/cat_test.png"])
        self.window.load_state_frames("bored", ["assets/cat_test.png"])
        self.window.load_state_frames("happy", ["assets/cat_test.png"])
        self.window.load_state_frames("dead", ["assets/cat_test.png"])  # TODO: sprite de "muerto" real
        self.window.play_state("idle")

        # --- Stats del Tamagotchi ---
        self.stats = {"hunger": 100, "energy": 100, "happiness": 100}
        self.state = "idle"
        self._alive = True

        # --- El menu de la ventana avisa aqui que opcion eligio el usuario ---
        self.window.feed_requested.connect(lambda: self.feed())
        self.window.play_requested.connect(lambda: self.play())
        self.window.assign_task_requested.connect(self._on_assign_task_requested)

        # --- Timer que hace bajar las stats solas con el tiempo ---
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.TICK_MS)

    # ============================================================
    # API PUBLICA — usada por el menu, y luego por ai_brain.py / skills
    # ============================================================

    def feed(self, amount: int = 20):
        """Le da de comer. No hace nada si ya murio."""
        if not self._alive:
            return
        self._adjust("hunger", amount)

    def play(self, amount: int = 15):
        """Juega con la mascota (sube felicidad, gasta energia)."""
        if not self._alive:
            return
        self._adjust("happiness", amount)
        self._adjust("energy", -5)

    def rest(self, amount: int = 30):
        """La deja descansar (sube energia)."""
        if not self._alive:
            return
        self._adjust("energy", amount)

    def get_state(self) -> str:
        return self.state

    def is_alive(self) -> bool:
        """
        Punto de coordinacion con el resto del proyecto (ej: Jose deberia
        chequear esto antes de mostrar una burbuja de recordatorio).
        """
        return self._alive

    def revive(self):
        """Reinicia la mascota desde cero (para un futuro boton de 'jugar de nuevo')."""
        self.stats = {"hunger": 100, "energy": 100, "happiness": 100}
        self._alive = True
        self.state = "idle"
        self.window.play_state("idle")
        self._timer.start(self.TICK_MS)

    # ============================================================
    # INTERNOS
    # ============================================================

    def _tick(self):
        self._adjust("hunger", -self.DECAY_PER_TICK["hunger"])
        self._adjust("energy", -self.DECAY_PER_TICK["energy"])
        self._adjust("happiness", -self.DECAY_PER_TICK["happiness"])

    def _adjust(self, stat: str, amount: float):
        self.stats[stat] = max(0, min(100, self.stats[stat] + amount))
        self._update_state()

    def _update_state(self):
        """
        Decide el estado segun las stats. Solo el HAMBRE en 0 causa la
        muerte (felicidad/energia bajas solo cambian el animo, no matan).
        """
        if not self._alive:
            return

        prev_state = self.state

        # --- Muerte: unicamente por hambre ---
        if self.stats["hunger"] <= 0:
            self.state = "dead"
            self._alive = False
            self._timer.stop()
            self.window.play_state("dead")
            return

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

    def _on_assign_task_requested(self):
        """
        Placeholder por ahora: aqui es donde en el futuro se abrira
        la interfaz para escribirle una tarea/recordatorio a la mascota,
        una vez que construyamos esa parte del asistente.
        """
        print("[pet] Asignar tarea seleccionado — funcionalidad pendiente")