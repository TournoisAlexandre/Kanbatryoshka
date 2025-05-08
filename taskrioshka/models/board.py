from datetime import datetime
import uuid
from .list import List

class Board:
    def __init__(self, title, description=""):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.lists = []
        
        self.add_list(List("À faire"))
        self.add_list(List("En cours"))
        self.add_list(List("Terminé"))
    
    def add_list(self, list_obj):
        self.lists.append(list_obj)
        self.updated_at = datetime.now()
        return list_obj
    
    def remove_list(self, list_id):
        self.lists = [l for l in self.lists if l.id != list_id]
        self.updated_at = datetime.now()
        return True