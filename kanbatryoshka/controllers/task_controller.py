class TaskController:
    def __init__(self, nest, task_widget, list_controller, task_id, list_id):
        self.nest = nest
        self.task_widget = task_widget
        self.list_controller = list_controller
        self.task_id = task_id
        self.list_id = list_id
        self.setup_connections()

    def setup_connections(self):
        self.task_widget.open_task_requested.connect(self.open_nested_board)
        self.task_widget.delete_task_requested.connect(self.handle_delete_task)
        self.task_widget.edit_task_requested.connect(self.handle_edit_task)

    def open_nested_board(self):
        board_controller = self.list_controller.board_controller
        board_controller.navigate_to_task_board(self.list_id, self.task_id)

    def handle_delete_task(self):

        if self.nest.task_has_subtasks(self.task_id):
            from PySide6.QtWidgets import QMessageBox
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Warning)
            error_dialog.setWindowTitle("Impossible to delete the task")
            error_dialog.setText("The task is not empty!")
            error_dialog.setInformativeText("Please remove subtasks before")
            error_dialog.setStandardButtons(QMessageBox.Ok)
            error_dialog.exec()
            return False


        self.list_controller.remove_task(self.task_id)

    def handle_edit_task(self, new_title, new_description):
        task_id = self.task_widget.task_id
        success = self.nest.update_task(task_id, new_title, new_description)
        
        if success:
            self.task_widget.update_task(new_title, new_description)

    def update_task(self, title = None, description = None):
        success = self.nest.update_task(self.task_id, title, description)
        
        if success and (title or description):
            if title:
                self.task_widget.set_title(title)
            if description:
                self.task_widget.set_description(description)

        return success
    
