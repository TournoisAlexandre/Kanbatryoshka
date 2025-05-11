from datetime import datetime
import uuid
from .board import Board

class Task:
    def __init__(self, title, description="", parent_board_id=None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        self.parent_board_id = parent_board_id

        self.board = Board(f"Board: {title}",
                           f"Board for task: {description}")
        self.board.parent_task_id = self.id
        self.board.parent_board_id = parent_board_id

    def update(self, title = None, description = None):
        if title is not None:
            self.title = title
            self.board.title = f"Board: {title}"

        if description is not None:
            self.description = description
            self.board.description = f"Board for task: {description}"

        self.updated_at = datetime.now()
        return True
    
    def get_nested_board(self):
        return self.board
