from .board import Board
from .list import List
from .task import Task
import json
from datetime import datetime

class Nest:
    def __init__(self):
        self.boards = []
        self.current_board = None
        self.navigation_stack = []
        self.current_list_id = None
        self.current_task_id = None

    def create_board(self, title, description="", parent_board_id=None, parent_task_id=None):
        board = Board(title, description)
        board.parent_board_id = parent_board_id
        board.parent_task_id  = parent_task_id
        self.boards.append(board)
        return board

    
    def select_board(self, board_id):
        b = next((b for b in self.boards if b.id == board_id), None)
        if not b: return False
        self.current_board = b
        return True
    
    def get_current_board(self):
        return self.current_board
    
    def navigate_to_task_board(self, list_id, task_id):
        if not self.current_board:
            return False

        for l in self.current_board.lists:
            if l.id == list_id:
                for t in l.tasks:
                    if t.id == task_id:
                        self.navigation_stack.append(
                            (self.current_board.id, list_id, task_id)
                        )
                        self.current_board = t.board
                        self.current_list_id = None
                        self.current_task_id = None
                        return True
        return False
    
    def back_to_parent(self):
        if not self.navigation_stack:
            return False

        parent_board_id, list_id, task_id = self.navigation_stack.pop()

        self.current_board = next(
            (b for b in self.boards if b.id == parent_board_id), None
        )

        self.current_list_id = list_id
        self.current_task_id = task_id

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
                task = Task(title, description, parent_board_id=self.current_board.id)
                nested = self.create_board(f"Board: {title}",
                                        f"Board pour la tâche: {description}",
                                        parent_board_id=self.current_board.id,
                                        parent_task_id=task.id)
                task.board = nested

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
    
    def get_task_by_id(self, task_id):
        task = self._find_task_in_board(self.current_board, task_id)
        if task:
            return task
        
        for board in self.boards.values():
            task = self._find_task_in_board(board, task_id)
            if task:
                return task
                
        return None

    def _find_task_in_board(self, board, task_id):
        if not board:
            return None
            
        for list_obj in board.lists:
            for task in list_obj.tasks:
                if task.id == task_id:
                    return task
                    
                if hasattr(task, 'board') and task.board:
                    nested_task = self._find_task_in_board(task.board, task_id)
                    if nested_task:
                        return nested_task
                        
        return None

    def task_has_subtasks(self, task_id):
        task = self.get_task_by_id(task_id)
        if not task or not hasattr(task, 'board') or not task.board:
            return False
        
        for list_obj in task.board.lists:
            if list_obj.tasks and len(list_obj.tasks) > 0:
                return True
        
        return False
        
    def get_board_path(self):
        path = []
        cur  = self.current_board
        while cur:
            path.insert(0, cur.title)
            pid = getattr(cur, "parent_board_id", None)
            cur = next((b for b in self.boards if b.id == pid), None)
        return path
    
    def remove_task_from_list(self, list_id, task_id):
        if not self.current_board:
            return False
        
        for list_obj in self.current_board.lists:
            if list_obj.id == list_id:
                return list_obj.remove_task(task_id)
            
        return False
    
    def update_task(self, task_id, title = None, description = None):
        if not self.current_board:
            return False
    
        for list_obj in self.current_board.lists:
            for task in list_obj.tasks:
                if task.id == task_id:
                    task.update(title, description)
                    return True
        
        return False
    
    def rename_list(self, list_id, new_title):
        if not self.current_board:
            return False
            
        for list_obj in self.current_board.lists:
            if list_obj.id == list_id:
                list_obj.title = new_title
                return True
                
        return False

    def reorder_task_in_list(self, list_id, task_id, new_index):
        if not self.current_board:
            return False
        
        target_list = None
        for list_obj in self.current_board.lists:
            if list_obj.id == list_id:
                target_list = list_obj
                break
        
        if not target_list:
            return False
        
        task_to_move = None
        task_index = -1
        for i, task in enumerate(target_list.tasks):
            if task.id == task_id:
                task_to_move = task
                task_index = i
                break
        
        if task_index == -1 or not task_to_move:
            return False
        
        if task_index == new_index:
            return True
        
        target_list.tasks.pop(task_index)
        
        if new_index >= len(target_list.tasks):
            target_list.tasks.append(task_to_move)
        else:
            target_list.tasks.insert(new_index, task_to_move)
        
        return True

    def move_list_in_current_board(self, list_id, new_position):
        board = self.get_current_board()
        if not board:
            return False
            
        list_indices = {lst.id: i for i, lst in enumerate(board.lists)}
        if list_id not in list_indices:
            return False
            
        current_position = list_indices[list_id]
        
        if current_position == new_position:
            return True

        list_to_move = board.lists.pop(current_position)
        board.lists.insert(new_position, list_to_move)
        
        return True
    
#region Save

    def save_to_file(self, file_path):
        data = self.serialize()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
        
    def load_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            success = self.deserialize(data)
            return success
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
        
    def serialize(self):
        boards_data = []
        
        for board in self.boards:
            board_data = {
                'id': board.id,
                'title': board.title,
                'description': board.description,
                'parent_board_id': getattr(board, 'parent_board_id', None),
                'parent_task_id': getattr(board, 'parent_task_id', None),
                'lists': []
            }
            
            for list_obj in board.lists:
                list_data = {
                    'id': list_obj.id,
                    'title': list_obj.title,
                    'created_at': list_obj.created_at.isoformat(),
                    'tasks': []
                }
                
                for task in list_obj.tasks:
                    task_data = {
                        'id': task.id,
                        'title': task.title,
                        'description': task.description,
                        'created_at': task.created_at.isoformat(),
                        'updated_at': task.updated_at.isoformat(),
                        'parent_board_id': task.parent_board_id,
                        'board_id': task.board.id if task.board else None
                    }
                    list_data['tasks'].append(task_data)
                
                board_data['lists'].append(list_data)
            
            boards_data.append(board_data)
        
        current_board_id = self.current_board.id if self.current_board else None
        
        serialized_stack = []
        for item in self.navigation_stack:
            board_id, list_id, task_id = item
            serialized_stack.append([board_id, list_id, task_id])
        
        data = {
            'boards': boards_data,
            'current_board_id': current_board_id,
            'navigation_stack': serialized_stack,
            'current_list_id': self.current_list_id,
            'current_task_id': self.current_task_id
        }
        
        return data
    
    def deserialize(self, data):
        try:
            self.boards = []
            self.current_board = None
            self.navigation_stack = []
            self.current_list_id = None
            self.current_task_id = None
            board_lookup = {}
            
            for board_data in data.get('boards', []):
                board = Board(board_data['title'], board_data['description'], create_default_lists=False)
                board.id = board_data['id']
                board.parent_board_id = board_data.get('parent_board_id')
                board.parent_task_id = board_data.get('parent_task_id')
                self.boards.append(board)
                board_lookup[board.id] = board
            
            task_board_mapping = {}
            
            for board_data in data.get('boards', []):
                board = board_lookup[board_data['id']]
                
                for list_data in board_data.get('lists', []):
                    list_obj = List(list_data['title'])
                    list_obj.id = list_data['id']
                    list_obj.created_at = datetime.fromisoformat(list_data['created_at'])
                    
                    for task_data in list_data.get('tasks', []):
                        task = Task(task_data['title'], task_data['description'], 
                                   task_data.get('parent_board_id'))
                        task.id = task_data['id']
                        task.created_at = datetime.fromisoformat(task_data['created_at'])
                        task.updated_at = datetime.fromisoformat(task_data['updated_at'])
                        
                        if task_data.get('board_id'):
                            task_board_mapping[task.id] = task_data['board_id']
                        
                        list_obj.tasks.append(task)
                    
                    board.lists.append(list_obj)
            
            for task_id, board_id in task_board_mapping.items():
                for board in self.boards:
                    for list_obj in board.lists:
                        for task in list_obj.tasks:
                            if task.id == task_id and board_id in board_lookup:
                                task.board = board_lookup[board_id]
            
            current_board_id = data.get('current_board_id')
            if current_board_id and current_board_id in board_lookup:
                self.current_board = board_lookup[current_board_id]
            
            for stack_item in data.get('navigation_stack', []):
                board_id, list_id, task_id = stack_item
                self.navigation_stack.append((board_id, list_id, task_id))
            
            self.current_list_id = data.get('current_list_id')
            self.current_task_id = data.get('current_task_id')
            
            return True
        
        except Exception as e:
            print(f"Error deserializing data: {e}")
            return False
        
#endregion Save