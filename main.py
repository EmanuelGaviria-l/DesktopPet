import sys
from PyQt6.QtWidgets import QApplication
from src.ui.welcome_screen import WelcomeScreen
from src.ui.main_menu import MainMenu
from src.ui.death_screen import DeathScreen
from src.pet import Pet
from src import profile


def main():
    app = QApplication(sys.argv)

    # Mantenemos referencias vivas aqui para que Qt no las borre de
    # memoria mientras el usuario todavia las esta usando.
    active_objects = []

    # ============================================================
    # FLUJO PRINCIPAL DE PANTALLAS
    # ============================================================

    def show_pet_menu():
        """Muestra la pantalla para crear/nombrar la mascota de esta sesion."""
        menu = MainMenu()
        active_objects.append(menu)

        def start_pet(pet_name: str, sprite_path: str):
            menu.close()
            pet = Pet(name=pet_name, sprite_path=sprite_path)
            pet.window.show()
            active_objects.append(pet)

            # --- Las barras de stats viven dentro de la ventana del gato,
            # se muestran solo al hacer click en el ---
            pet.stats_changed.connect(pet.window.update_stats)

            pet.died.connect(lambda name, seconds: on_pet_died(pet, name, seconds))
            pet.window.quit_requested.connect(app.quit)

        menu.pet_selected.connect(start_pet)
        menu.show()

    def on_pet_died(pet: Pet, name: str, seconds_alive: float):
        """Se llama cuando una mascota muere: cierra su ventana y muestra el aviso."""
        pet.window.close()

        death_screen = DeathScreen(name, seconds_alive)
        active_objects.append(death_screen)

        def on_return_to_menu():
            death_screen.close()
            show_pet_menu()

        death_screen.return_to_menu_requested.connect(on_return_to_menu)
        death_screen.show()

    # --- Decidir si mostrar la bienvenida o saltarla directo al menu ---
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

    '''
    Hay un error en el menu de necesidades, no se muestran
    a la par del gato, sino que se muestran DENTRO del gato
    y no se pueden ver adecuadamente. Esto se debe a que el 
    menu de necesidades es un widget hijo de la ventana del 
    gato, y por lo tanto se dibuja dentro de ella. 
    Para solucionarlo, se puede hacer que el menu de 
    necesidades sea un widget independiente (no hijo) y 
    posicionarlo al lado del gato, o usar un layout adecuado 
    para que se muestre correctamente.
    '''