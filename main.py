from pathlib import Path
from src.gui import MainGUI


def main():
    if not Path('./database.json').exists():
        with open('database.json', 'w') as f:
            f.write('{}')
    gui = MainGUI()
    gui.mainloop()


if __name__ == '__main__':
    main()
