from PySide6.QtWidgets import QWidget, QHBoxLayout, QScrollArea, QPushButton, QLabel, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag

class BoardWidget(QWidget):
    add_list_requested = Signal()
    list_moved = Signal(str, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.drag_start_position = None
        self.dragged_list = None
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.board_title_label = QLabel("Board")
        self.board_title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 10px;")
        self.board_title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.board_title_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        board_container = QWidget()
        board_container.setAcceptDrops(True)
        self.board_layout = QHBoxLayout(board_container)
        self.board_layout.setContentsMargins(10, 10, 10, 10)
        self.board_layout.setSpacing(15)
        self.board_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        scroll_area.setWidget(board_container)
        main_layout.addWidget(scroll_area)
        
        self.add_list_button = QPushButton("+ Add a list")
        self.add_list_button.setFixedHeight(40)
        self.board_layout.addWidget(self.add_list_button)
        
        self.add_list_button.clicked.connect(self.add_list_requested.emit)
    
    def set_board_title(self, title):
        self.board_title_label.setText(title)
    
    def clear_board(self):
        add_button = None
        if self.board_layout.count() > 0:
            add_button = self.board_layout.itemAt(self.board_layout.count() - 1).widget()
            self.board_layout.removeWidget(add_button)
            
        while self.board_layout.count():
            item = self.board_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if add_button:
            self.board_layout.addWidget(add_button)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position()
            
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or not self.drag_start_position:
            return
            
        if (event.position() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
            
        self.dragged_list = self.get_list_at_position(self.drag_start_position.toPoint())
        if not self.dragged_list:
            return
            
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(f"list:{self.dragged_list.list_id}")
        drag.setMimeData(mime_data)
        
        drag.exec_(Qt.MoveAction)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith("list:"):
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith("list:"):
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        if not event.mimeData().hasText() or not event.mimeData().text().startswith("list:"):
            return
            
        list_id = event.mimeData().text().split(":")[1]
        target_position = self.get_list_position_at(event.position().toPoint())
        
        self.list_moved.emit(list_id, target_position)
        
        event.acceptProposedAction()
        
    def get_list_at_position(self, pos):
        for i in range(self.board_layout.count() - 1):
            widget = self.board_layout.itemAt(i).widget()
            if widget.geometry().contains(pos):
                return widget
        return None
        
    def get_list_position_at(self, pos):
        if pos.x() < self.board_layout.itemAt(0).widget().geometry().left():
            return 0
            
        for i in range(self.board_layout.count() - 1):
            widget = self.board_layout.itemAt(i).widget()
            widget_right = widget.geometry().right()
            
            if pos.x() < widget_right:
                return i
            
            if i < self.board_layout.count() - 2:
                next_widget = self.board_layout.itemAt(i+1).widget()
                if pos.x() < next_widget.geometry().left():
                    return i + 1
                    
        return self.board_layout.count() - 1