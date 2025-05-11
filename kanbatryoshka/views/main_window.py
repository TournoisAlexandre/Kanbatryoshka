from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QMessageBox, QFileDialog,
                              QStatusBar, QPushButton, QLabel, 
                              QToolBar)
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from ..views.board_widget import BoardWidget
import os

class MainWindow(QMainWindow):
    add_list_requested = Signal()
    new_board_requested = Signal()
    save_requested = Signal(str)
    load_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kanbatryoshka")
        self.resize(1440, 720)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):

        self.setup_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        toolbar = QToolBar("Navigation")
        self.addToolBar(toolbar)

        self.back_button = QPushButton("⬅ Back")
        self.back_button.setToolTip("Get Back One Layer")
        toolbar.addWidget(self.back_button)

        self.path_label = QLabel()
        toolbar.addWidget(self.path_label)

        main_layout = QVBoxLayout(central_widget)

        self.board_widget = BoardWidget()
        main_layout.addWidget(self.board_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new)
        file_menu.addAction(new_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)
        
        load_action = QAction("&Load", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.on_load)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def setup_connections(self):
        self.board_widget.add_list_requested.connect(self.add_list_requested.emit)
    
    def set_board_title(self, title):
        self.board_widget.set_board_title(title)

    def update_navigation_path(self, path):
        path_text = " > ".join(path)
        self.path_label.setText(path_text)

    def on_new(self):
        reply = QMessageBox.question(self, 'New Board', 
                                     'Are you sure you want to create a new kanban board? Any unsaved work will be lost.',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.new_board_requested.emit()
            self.status_bar.showMessage("Created new kanban board")
    
    def on_save(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Kanban Board", "", "Kanbatryoshka Files (*.ktb);;JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            if not os.path.splitext(file_path)[1]:
                file_path += ".ktb"
                
            self.save_requested.emit(file_path)
            self.status_bar.showMessage(f"Saved to {file_path}")
    
    def on_load(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Kanban Board", "", "Kanbatryoshka Files (*.ktb);;JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.load_requested.emit(file_path)
            self.status_bar.showMessage(f"Loaded from {file_path}")