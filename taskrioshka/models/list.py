from datetime import datetime
import uuid

class List:
    def __init__(self, title):
        self.id = str(uuid.uuid4())
        self.title = title
        self.created_at = datetime.now()
        self.tasks = []
    
    def add_task(self, task):
        self.tasks.append(task)
        return task
    
    def remove_task(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        return True