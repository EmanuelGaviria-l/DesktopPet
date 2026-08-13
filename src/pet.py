from PyQt6.QtCore import QTimer
from src.ui.pet_window import PetWindow


class Pet:
    """
    The Tamagotchi "mind": tracks hunger, energy, and happiness.
    Derives a single current_state from those stats and tells the
    window which animation to play. ai_brain.py and future skills
    will call feed()/play()/rest() the same way user clicks do.
    """

    DECAY_PER_TICK = {"hunger": 2, "energy": 1, "happiness": 1}
    TICK_MS = 500  # stats decay every 30 seconds (tune for demo speed)

    def __init__(self):
        print("PET INIT ARRANCANDO - VERSION NUEVA")
        self.window = PetWindow()

        # Register whatever animations exist right now.
        # Later, swap these lists for multiple frames per state
        # once your friend delivers the real spritesheets.
        self.window.load_state_frames("idle", ["assets/cat_test.png"])
        self.window.load_state_frames("hungry", ["assets/cat_test.png"])
        self.window.load_state_frames("bored", ["assets/cat_test.png"])
        self.window.load_state_frames("happy", ["assets/cat_test.png"])
        self.window.play_state("idle")

        self.stats = {"hunger": 100, "energy": 100, "happiness": 100}
        self.state = "idle"

        self.window.clicked.connect(self._on_clicked)
        self.window.double_clicked.connect(self._on_double_clicked)

        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.TICK_MS)

    # --- public API — this is what ai_brain.py / skills will call later ---

    def feed(self, amount: int = 20):
        self._adjust("hunger", amount)

    def play(self, amount: int = 15):
        self._adjust("happiness", amount)
        self._adjust("energy", -5)

    def rest(self, amount: int = 30):
        self._adjust("energy", amount)

    def get_state(self) -> str:
        return self.state

    # --- internals ---

    def _tick(self):
        self._adjust("hunger", -self.DECAY_PER_TICK["hunger"])
        self._adjust("energy", -self.DECAY_PER_TICK["energy"])
        self._adjust("happiness", -self.DECAY_PER_TICK["happiness"])
        print(f"[tick] hunger={self.stats['hunger']} happiness={self.stats['happiness']}")

    def _adjust(self, stat: str, amount: float):
        self.stats[stat] = max(0, min(100, self.stats[stat] + amount))
        self._update_state()

    def _update_state(self):
        prev_state = self.state

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
            print(f"[pet] nuevo estado: {self.state}")

    def _on_clicked(self):
        self.play(amount=5)

    def _on_double_clicked(self):
        self.feed(amount=10)