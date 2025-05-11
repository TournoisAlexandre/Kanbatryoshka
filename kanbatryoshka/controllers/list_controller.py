from ..controllers.task_controller import TaskController

class ListController:
    def __init__(self, nest, list_widget, board_controller):
        self.nest = nest
        self.list_widget = list_widget
        self.board_controller = board_controller
        self.task_controllers = []
        self.setup_connections()
        self.load_tasks()

    def setup_connections(self):
        self.list_widget.add_task_requested.connect(self.handle_add_task)
        self.list_widget.edit_title_requested.connect(self.handle_rename_list)
        self.list_widget.delete_list_requested.connect(self.handle_delete_list)
        self.list_widget.task_moved.connect(self.handle_task_reordered)
        self.list_widget.task_moved_to_list.connect(self.handle_task_moved_to_list)

    def handle_add_task(self):
        title = "New Task"
        description = "New Task Descriptions"
        task = self.add_task(title, description)

        if task:
            for task_controller in self.task_controllers:
                if task_controller.task_id == task.id:
                    task_controller.task_widget.handle_edit_task()
                    break

    def add_task(self, title, description):
        list_id = self.list_widget.list_id
        task = self.nest.add_task_to_list(list_id, title, description)

        if task:
            task_widget = self.list_widget.add_task(task.title, task.description, task.id)
            task_controller = TaskController(self.nest, task_widget, self, task.id, list_id)
            self.task_controllers.append(task_controller)

        return task
    
    def remove_task(self, task_id):
        list_id = self.list_widget.list_id
        success = self.nest.remove_task_from_list(list_id, task_id)

        if success:
            self.list_widget.remove_task(task_id)
            self.task_controllers = [tc for tc in self.task_controllers if tc.task_id != task_id]

        return success
    
    def load_tasks(self):
        list_id = self.list_widget.list_id
        current_board = self.nest.get_current_board()
        
        if not current_board:
            return
            
        for list_obj in current_board.lists:
            if list_obj.id == list_id:
                for task in list_obj.tasks:
                    task_widget = self.list_widget.add_task(task.title, task.description, task.id)
                    task_controller = TaskController(self.nest, task_widget, self, task.id, list_id)

                    has_subtasks = self.nest.task_has_subtasks(task.id)
                    task_widget.set_has_subtasks(has_subtasks)
                    
                    self.task_controllers.append(task_controller)
                break

        self.list_widget.update_delete_button_state()

    def handle_rename_list(self, new_title):
        list_id = self.list_widget.list_id
        success = self.nest.rename_list(list_id, new_title)
        
        if success:
            self.list_widget.update_title(new_title)

    
    def handle_delete_list(self):
        list_id = self.list_widget.list_id

        if self.task_controllers:
            from PySide6.QtWidgets import QMessageBox
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Warning)
            error_dialog.setWindowTitle("Cannot delete list")
            error_dialog.setText("List is not empty!")
            error_dialog.setInformativeText("Remove all tasks from list first.")
            error_dialog.setStandardButtons(QMessageBox.Ok)
            error_dialog.exec()
            return False

        success = self.board_controller.remove_list(list_id)
        return success

    def handle_task_reordered(self, task_id, new_index):
        old_index = -1
        task_widget = None
        
        for i, tc in enumerate(self.task_controllers):
            if tc.task_id == task_id:
                old_index = i
                task_widget = tc.task_widget
                break
        
        if old_index == -1:
            return
        
        success = self.nest.reorder_task_in_list(self.list_widget.list_id, task_id, new_index)
        
        if success:
            self.list_widget.tasks_layout.removeWidget(task_widget)
            
            layout_count = self.list_widget.tasks_layout.count()
            if new_index > layout_count:
                new_index = layout_count
            
            self.list_widget.tasks_layout.insertWidget(new_index, task_widget)
            
            controller = self.task_controllers.pop(old_index)
            
            controller_count = len(self.task_controllers)
            if new_index > controller_count:
                new_index = controller_count
            
            self.task_controllers.insert(new_index, controller)
            
            task_widget.show()

    def handle_task_moved_to_list(self, task_id, source_list_id):
        target_list_id = self.list_widget.list_id
        
        if source_list_id == target_list_id:
            return
        
        success = self.nest.move_task_between_lists(task_id, source_list_id, target_list_id)
        
        if success:
            self.board_controller.update_view()
            