import sys
from PyQt6.QtWidgets import QApplication
from src.pet import Pet


def main():
    app = QApplication(sys.argv)
    pet = Pet()
    pet.window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()