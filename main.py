
from gui.layout import build_gui
from database.db_handler import create_table

if __name__ == "__main__":
    create_table()
    build_gui()
