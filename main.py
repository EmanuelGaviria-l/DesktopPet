import sys
from PyQt6.QtWidgets import QApplication
from src.ui.welcome_screen import WelcomeScreen
from src.ui.main_menu import MainMenu
from src.ui.death_screen import DeathScreen
from src.ui.stats_bar import StatsBar
from src.pet import Pet
from src import profile


def main():
    app = QApplication(sys.argv)

    active_objects = []

    def show_pet_menu():
        menu = MainMenu()
        active_objects.append(menu)

        def start_pet(pet_name: str, sprite_path: str):
            menu.close()
            pet = Pet(name=pet_name, sprite_path=sprite_path)
            pet.window.show()
            active_objects.append(pet)

            # --- Barra de stats: oculta por defecto, aparece solo con el menu ---
            stats_bar = StatsBar()
            active_objects.append(stats_bar)

            pet.stats_changed.connect(stats_bar.update_stats)
            pet.window.menu_opened.connect(stats_bar.show_beside)
            pet.window.menu_closed.connect(stats_bar.hide)

            pet.died.connect(lambda name, seconds: on_pet_died(pet, name, seconds, stats_bar))
            pet.window.quit_requested.connect(app.quit)

        menu.pet_selected.connect(start_pet)
        menu.show()

    def on_pet_died(pet: Pet, name: str, seconds_alive: float, stats_bar: StatsBar):
        pet.window.close()
        stats_bar.close()

        death_screen = DeathScreen(name, seconds_alive)
        active_objects.append(death_screen)

        def on_return_to_menu():
            death_screen.close()
            show_pet_menu()

        death_screen.return_to_menu_requested.connect(on_return_to_menu)
        death_screen.show()

    existing_profile = profile.load_profile()

    if existing_profile is None:
        welcome = WelcomeScreen()
        active_objects.append(welcome)

        def on_name_confirmed(user_name: str):
            profile.save_profile(user_name)
            welcome.close()
            show_pet_menu()

        welcome.name_confirmed.connect(on_name_confirmed)
        welcome.show()
    else:
        show_pet_menu()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()