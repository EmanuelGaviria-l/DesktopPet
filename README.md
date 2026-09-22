# Desktop Pet 🐾

A desktop companion built with Python and PyQt6. The application features an interactive virtual pet that lives on the user's desktop, manages its own needs over time, and responds to user interactions.

## Features

- Interactive desktop pet with autonomous movement
- Hunger, energy, and happiness systems
- Timed stat decay and starvation mechanics
- Feeding, playing, and resting interactions
- Multiple pet states and animations
- Persistent user profiles using JSON
- Pet death and cemetery system
- Custom pet names and profiles
- Transparent, frameless desktop window
- Drag-and-drop pet interaction

## Tech Stack

- Python
- PyQt6
- JSON
- Object-Oriented Programming
- Event-Driven Programming

## Project Structure

```text
DesktopPet/
├── assets/
│   ├── bat_v1.png
│   ├── cat_test.png
│   └── pets.png
├── data/
├── src/
│   └── ui/
│       ├── death_screen.py
│       ├── main_menu.py
│       ├── pet_window.py
│       ├── stats_bar.py
│       └── welcome_screen.py
├── cemetery.py
├── pet.py
├── profile.py
├── main.py
└── .gitignore
