from datetime import datetime
import uuid
from .board import Board

class Task:
    def __init__(self, title, description=""):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.board = Board(f"Board: {title}", f"Board pour la tâche: {title}")

    def get_board(self):
        return self.board