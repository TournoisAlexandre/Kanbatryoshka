from .board import Board
from .list import List
from .task import Task

class Nest:
    def __init__(self):
        self.boards = []
        self.current_board = None
        self.navigation_stack = []

    def create_board(self, title, description = ""):
        board = Board(title, description)
        self.boards.append(board)
        return board
    
    def delete_board(self, board_id):
        self.boards = [b for b in self.boards if b.id != board_id]
        if self.current_board and self.current_board == board_id:
            self.back_to_parent()
        return True
    
    def select_board(self, board_id):
        for board in self.boards:
            if board.id == board_id:
                self.current_board = board
                return True
        return False
    
    def get_current_board(self):
        return self.current_board
    
    def navigate_to_task_board(self, list_id, task_id):
        if not self.current_board:
            return False
        
        for list_obj in self.current_board.lists:
            if list_obj.id == list_id:
                for task in list_obj.tasks:
                    if task.id == task_id:
                        self.navigation_stack.append((self.current_board, list_id, task_id))
                        self.current_board = task.get_board()
                        return True
        return False
    
    def back_to_parent(self):
        if not self.navigation_stack:
            return False
        
        parent_info = self.navigation_stack.pop()
        self.current_board = parent_info[0]
        return True
    
    def add_list_to_current_board(self, title):
        if not self.current_board:
            return None
        
        list_obj = List(title)
        self.current_board.add_list(list_obj)
        return list_obj
    
    def remove_list_from_current_board(self, list_id):
        if not self.current_board:
            return False
        
        return self.current_board.remove_list(list_id)
    
    def add_task_to_list(self, list_id, title, description=""):
        if not self.current_board:
            return None
        
        for list_obj in self.current_board.lists:
            if list_obj.id == list_id:
                task = Task(title, description)
                list_obj.add_task(task)
                return task
            
        return None
    
    def move_task_between_lists(self, task_id, source_list_id, target_list_id):
        if not self.current_board:
            return False
        
        source_list = None
        target_list = None

        for list_obj in self.current_board.lists:
            if list_obj.id == source_list_id:
                source_list = list_obj
            elif list_obj.id == target_list_id:
                target_list = list_obj

        if not source_list or not target_list:
            return False
        
        task_to_move = None
        for task in source_list.tasks:
            if task.id == task_id:
                task_to_move = task
                break

        if not task_to_move:
            return False
        
        source_list.remove_task(task_id)
        target_list.add_task(task_to_move)

        return True
        
    def get_board_path(self):
        path = []
        for board_info in self.navigation_stack:
            board = board_info[0]
            path.append(board.title)

        if self.current_board:
            path.append(self.current_board.title)

        return path