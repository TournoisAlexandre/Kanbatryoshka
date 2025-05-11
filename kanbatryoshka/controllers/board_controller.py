from PySide6.QtWidgets import QMessageBox
from ..views.list_widget import ListWidget
from ..controllers.list_controller import ListController

class BoardController:
    def __init__(self, nest, main_window):
        self.nest = nest
        self.main_window = main_window
        self.list_controllers = []
        self.setup_connections()
        self.initialize_board()

    def setup_connections(self):
        self.main_window.add_list_requested.connect(self.handle_add_list)
        self.main_window.back_button.clicked.connect(self.navigate_back)
        self.main_window.board_widget.list_moved.connect(self.handle_list_moved)

        self.main_window.new_board_requested.connect(self.create_new_board)
        self.main_window.save_requested.connect(self.save_board)
        self.main_window.load_requested.connect(self.load_board)

        self.update_navigation_path()

    def initialize_board(self):
        if not self.nest.get_current_board():
            default_board = self.nest.create_board("Main Board", "Default Board")
            self.nest.select_board(default_board.id)

        self.update_view()

    def update_view(self):
        board = self.nest.get_current_board()
        self.main_window.set_board_title(board.title)
        self.main_window.update_navigation_path(self.nest.get_board_path())

        self.list_controllers.clear()
        self.clear_board_layout()

        for lst in board.lists:
            lw = ListWidget(lst.title, lst.id)
            self.main_window.board_widget.board_layout.insertWidget(
                self.main_window.board_widget.board_layout.count() - 1, lw
            )
            lc = ListController(self.nest, lw, self)
            self.list_controllers.append(lc)
        
    def clear_board_layout(self):
        board_layout = self.main_window.board_widget.board_layout
        add_button = None
        if board_layout.count() > 0:
            add_button = board_layout.itemAt(board_layout.count() - 1).widget()
            board_layout.removeWidget(add_button)

        while board_layout.count():
            item = board_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        board_layout.addWidget(add_button)

    def handle_add_list(self):
        title = "New List"
        list = self.add_list(title)

        if list:
            for list_controller in self.list_controllers:
                if list_controller.list_widget.list_id == list.id:
                    list_controller.list_widget.handle_edit_title()
                    break

    def add_list(self, title):
        new_list = self.nest.add_list_to_current_board(title)
        if new_list:
            self.update_view()
        return new_list
    
    def remove_list(self, list_id):
        success = self.nest.remove_list_from_current_board(list_id)
        if success:
            self.update_view()
        return success
    
    def navigate_to_task_board(self, list_id, task_id):
        success = self.nest.navigate_to_task_board(list_id, task_id)
        if success:
            self.update_view()
        return success

    def navigate_back(self):
        success = self.nest.back_to_parent()
        if success:
            self.update_view()
        return success
    
    def update_navigation_path(self):
        path = self.nest.get_board_path()
        self.main_window.update_navigation_path(path)

    def handle_list_moved(self, list_id, new_position):
        success = self.nest.move_list_in_current_board(list_id, new_position)
        if success:
            self.update_view()

    def create_new_board(self):
        self.nest = type(self.nest)()
        default_board = self.nest.create_board("Main Board", "Default Board")
        self.nest.select_board(default_board.id)
        
        self.update_view()

    def save_board(self, file_path):
        try:
            success = self.nest.save_to_file(file_path)
            if not success:
                QMessageBox.warning(self.main_window, "Save Failed", 
                                   "Failed to save the kanban board.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", 
                               f"An error occurred while saving: {str(e)}")

    def load_board(self, file_path):
        try:
            success = self.nest.load_from_file(file_path)
            if success:
                self.update_view()
            else:
                QMessageBox.warning(self.main_window, "Load Failed", 
                                   "Failed to load the kanban board.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", 
                               f"An error occurred while loading: {str(e)}")
            