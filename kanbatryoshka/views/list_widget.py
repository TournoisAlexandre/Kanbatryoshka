from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QApplication,
                              QPushButton, QScrollArea, QInputDialog, QLineEdit)
from PySide6.QtCore import Qt, Signal, QMimeData, QPoint
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPainter, QColor, QDrag, QPixmap, QBrush
from .task_widget import TaskWidget
import uuid

class ListWidget(QFrame):

    add_task_requested = Signal()
    edit_title_requested = Signal(str)
    delete_list_requested = Signal()
    task_moved = Signal(str, int)
    task_moved_to_list = Signal(str, str)

    def __init__(self, title, list_id = None):
        super().__init__()
        self.title = title
        self.list_id = list_id if list_id else str(uuid.uuid4())
        self.task_widgets = {}
        self.setup_ui()
        self.update_delete_button_state()
        self.setup_connections()
        self.setAcceptDrops(True)
        self.drag_start_position = None

    def setup_connections(self):
        self.add_task_button.clicked.connect(self.add_task_requested)
        self.edit_button.clicked.connect(self.handle_edit_title)
        self.delete_button.clicked.connect(self.delete_list_requested)
        
    def setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            ListWidget {
                background-color: #f5f5f5;
                border-radius: 4px;
                min-width: 300px;
                max-width: 300px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10,10,10,10)
        main_layout.setSpacing(10)

        header_layout = QHBoxLayout()

        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.title_label)

        self.edit_button = QPushButton("✏️")
        self.edit_button.setFixedSize(20,20)
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #555;  /* Couleur du texte gris foncé */
                font-weight: bold;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                color: #f44336;  /* Rouge quand la souris passe dessus */
                background-color: #f0f0f0;
                border-radius: 12px;
            }
        """)
        header_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("x")
        self.delete_button.setFixedSize(20,20)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #555;  /* Couleur du texte gris foncé */
                font-weight: bold;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                color: #f44336;  /* Rouge quand la souris passe dessus */
                background-color: #f0f0f0;
                border-radius: 12px;
            }
        """)
        header_layout.addWidget(self.delete_button)

        main_layout.addLayout(header_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(0,0,0,0)
        self.tasks_layout.setSpacing(10)
        self.tasks_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.tasks_container)
        main_layout.addWidget(self.scroll_area)

        self.add_task_button = QPushButton("+ Add a task")
        main_layout.addWidget(self.add_task_button)
     

    def add_task(self, title, description = "", task_id = None):
        task_widget = TaskWidget(title, description, task_id)
        self.tasks_layout.addWidget(task_widget)

        if task_id:
            self.task_widgets[task_id] = task_widget

        self.update_delete_button_state()

        return task_widget


    def remove_task(self, task_id):
        if task_id in self.task_widgets:
            task_widget = self.task_widgets[task_id]
            self.tasks_layout.removeWidget(task_widget)
            task_widget.deleteLater()
            del self.task_widgets[task_id]

            self.update_delete_button_state()

            return True
        return False
    
    def handle_edit_title(self):
        new_title, ok = QInputDialog.getText(
            self, 
            "Renaming List", 
            "New Title:",
            QLineEdit.Normal,
            self.title
        )
        
        if ok and new_title:
            self.edit_title_requested.emit(new_title)

    def update_title(self, new_title):
        self.title = new_title
        self.title_label.setText(new_title)



    def find_task_index(self, task_id):
        for i in range(self.tasks_layout.count()):
            item = self.tasks_layout.itemAt(i)
            if item and item.widget():
                if hasattr(item.widget(), 'task_id') and item.widget().task_id == task_id:
                    return i
        return -1


    
    def find_parent_list(self, widget):
        if not widget:
            return None
            
        current = widget
        
        while current:
            if isinstance(current, ListWidget):
                return current
            current = current.parent()
            
        return None
    
    def get_drop_index(self, pos):
        num_tasks = self.tasks_layout.count()
        
        if num_tasks == 0:
            return 0
        
        for i in range(num_tasks):
            item = self.tasks_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:

                    widget_rect = widget.geometry()
                    if pos.y() < widget_rect.y() + widget_rect.height() / 2:
                        return i

        return num_tasks
    
    def update_delete_button_state(self):
        has_tasks = self.tasks_layout.count() > 0
        
        if has_tasks:
            self.delete_button.setEnabled(False)
            self.delete_button.setToolTip("Cannot delete lists with tasks")
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #aaa;
                    font-weight: bold;
                    font-size: 16px;
                    border: none;
                }
                QPushButton:hover {
                    color: #aaa;
                }
            """)
        else:
            self.delete_button.setEnabled(True)
            self.delete_button.setToolTip("")
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #555;
                    font-weight: bold;
                    font-size: 16px;
                    border: none;
                }
                QPushButton:hover {
                    color: #f44336;
                    background-color: #f0f0f0;
                    border-radius: 12px;
                }
            """)

#region Mouse

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            header_rect = self.title_label.rect().adjusted(0, 0, 0, 10)
            header_point = self.title_label.mapTo(self, QPoint(0, 0))
            header_rect.moveTo(header_point)
            
            if header_rect.contains(event.pos()):
                self.drag_start_position = event.pos()
        
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not hasattr(self, 'drag_start_position') or not self.drag_start_position:
            super().mouseMoveEvent(event)
            return
            
        if not (event.buttons() & Qt.LeftButton):
            super().mouseMoveEvent(event)
            return
            
        distance = (event.position() - self.drag_start_position).manhattanLength()
        if distance < QApplication.startDragDistance():
            super().mouseMoveEvent(event)
            return
            
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(f"list:{self.list_id}")
        drag.setMimeData(mime_data)
        
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        
        self.render(pixmap)
        
        temp_pixmap = QPixmap(pixmap.size())
        temp_pixmap.fill(QColor(0, 0, 0, 128))
        
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.drawPixmap(0, 0, temp_pixmap)
        painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())
        
        result = drag.exec(Qt.MoveAction)
        
        self.drag_start_position = None


    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat("application/x-task-id"):
            event.accept()
            self.setCursor(Qt.CursorShape.DragMoveCursor)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-task-id"):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        self.setCursor(Qt.CursorShape.ArrowCursor)

        if event.mimeData().hasFormat("application/x-task-id"):
            task_id = event.mimeData().data("application/x-task-id").data().decode()
            
            source_widget = event.source()
            source_list = self.find_parent_list(source_widget)
            
            drop_index = self.get_drop_index(event.pos())
            
            if source_list and source_list != self:
                source_list_id = source_list.list_id
                self.task_moved_to_list.emit(task_id, source_list_id)
            else:
                current_index = self.find_task_index(task_id)
                if current_index >= 0 and current_index < drop_index:
                    drop_index -= 1
                
                self.task_moved.emit(task_id, drop_index)
            
            event.accept()

#endregion Mouse