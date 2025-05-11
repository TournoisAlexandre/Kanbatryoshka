from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QSizePolicy, QHBoxLayout, QPushButton, QDialog, QLineEdit, QTextEdit, QApplication
from PySide6.QtCore import Qt, Signal, QMimeData, QByteArray, QTimer
from PySide6.QtGui import QDrag
import uuid

class TaskWidget(QFrame):
    open_task_requested = Signal()
    edit_task_requested = Signal(str, str)
    delete_task_requested = Signal()


    def __init__(self, title, description, task_id = None):
        super().__init__()

        self.title = title
        self.description = description
        self.task_id = task_id if task_id else str(uuid.uuid4())
        self.has_subtasks = False
        self.drag_start_position = None
        self.is_dragging = False
        self.double_click_timer = None
        self.setup_ui()
        self.setup_connections()

        self.nested_indicator.setVisible(True)

    def setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            TaskWidget {
                background-color: white;
                border-radius: 4px;
                border: 1px solid #ddd;
                margin: 4px;
            }
            
            TaskWidget:hover {
                border: 1px solid #aaa;
            }
        """)

        self.setMinimumSize(80, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        header_layout = QHBoxLayout()

        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.title_label)

        self.edit_button = QPushButton("✏️")
        self.edit_button.setFixedSize(20,20)
        self.edit_button.setStyleSheet("""
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
        header_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("×")
        self.delete_button.setFixedSize(20, 20)
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
        
        layout.addLayout(header_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #dddddd; margin: 5px 0;")
        layout.addWidget(separator)

        self.description_label = QLabel(self.description)
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.description_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout.addWidget(self.description_label)

        self.nested_indicator = QLabel("📊 Contains a board")
        self.nested_indicator.setStyleSheet("color: #666; font-size: 10px;")
        self.nested_indicator.setAlignment(Qt.AlignRight)
        layout.addWidget(self.nested_indicator)

    def setup_connections(self):
        self.edit_button.clicked.connect(self.handle_edit_task)
        self.delete_button.clicked.connect(self.delete_task_requested.emit)

    def set_title(self, title):
        self.title = title
        self.title_label.setText(title)

    def set_description(self, description):
        self.description = description
        self.description_label.setText(description)

    def handle_edit_task(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Task")
        layout = QVBoxLayout(dialog)
        
        title_label = QLabel("Title:")
        title_input = QLineEdit(self.title)
        layout.addWidget(title_label)
        layout.addWidget(title_input)
        
        desc_label = QLabel("Description:")
        desc_input = QTextEdit(self.description)
        layout.addWidget(desc_label)
        layout.addWidget(desc_input)
        
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        cancel_btn.clicked.connect(dialog.reject)
        save_btn.clicked.connect(dialog.accept)
        
        if dialog.exec() == QDialog.Accepted:
            new_title = title_input.text()
            new_description = desc_input.toPlainText()
            if new_title:
                self.edit_task_requested.emit(new_title, new_description)

    def update_task(self, title=None, description=None):
        if title is not None:
            self.title = title
            self.title_label.setText(title)
        
        if description is not None:
            self.description = description
            self.description_label.setText(description)

    def update_delete_button_state(self, has_subtasks):
        if has_subtasks:
            self.delete_button.setEnabled(False)
            self.delete_button.setToolTip("Cannot delete a task with subtasks")
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
            
            self.nested_indicator.setText("📊 Contains subtasks (cannot delete)")
            self.nested_indicator.setStyleSheet("color: #f44336; font-size: 10px;")
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
            
            self.nested_indicator.setText("📊 Contains a board")
            self.nested_indicator.setStyleSheet("color: #666; font-size: 10px;")

    def set_has_subtasks(self, has_subtasks):
        self.has_subtasks = has_subtasks
        self.update_delete_button_state(has_subtasks)

#region Mouse

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

            if self.double_click_timer and self.double_click_timer.isActive():
                self.drag_start_position = None

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
            
        if not self.drag_start_position:
            return
            
        if self.double_click_timer and self.double_click_timer.isActive():
            return
            
        distance = (event.pos() - self.drag_start_position).manhattanLength()
        if distance < QApplication.startDragDistance():
            return
            
        self.is_dragging = True
        
        drag = QDrag(self)
        mime_data = QMimeData()
        
        mime_data.setText(f"{self.task_id}")
        mime_data.setData("application/x-task-id", QByteArray(self.task_id.encode()))
        
        drag.setMimeData(mime_data)
        
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        result = drag.exec(Qt.MoveAction)
        self.is_dragging = False
        self.drag_start_position = None

    def mouseReleaseEvent(self, event):
        if not self.is_dragging and self.drag_start_position:
            pass
            
        self.drag_start_position = None
        self.is_dragging = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if not self.double_click_timer:
            self.double_click_timer = QTimer()
            self.double_click_timer.setSingleShot(True)
            self.double_click_timer.timeout.connect(self.reset_double_click)
        
        self.double_click_timer.start(500)
        
        self.open_task_requested.emit()
        
        super().mouseDoubleClickEvent(event)

    def reset_double_click(self):
        self.drag_start_position = None
        self.is_dragging = False

#endregion Mouse