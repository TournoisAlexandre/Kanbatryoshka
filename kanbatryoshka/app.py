from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import os
from .controllers.board_controller import BoardController
from .models.nest import Nest
from .views.main_window import MainWindow


class KanbatryoshkaApp:
    def __init__(self):
        self.app = QApplication([])
        self.app.setStyle("Fusion")
        
        self.nest = Nest()
        
        if not self.nest.boards:
            default_board = self.nest.create_board("Main Board")
            self.nest.select_board(default_board.id)
        else:
            self.nest.select_board(self.nest.boards[0].id)
        
        self.main_window = MainWindow()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "assets/mini_icon.png")
        self.main_window.setWindowIcon(QIcon(icon_path))
        
        self.board_controller = BoardController(self.nest, self.main_window)
        
    def run(self):
        self.main_window.show()
        return self.app.exec()
