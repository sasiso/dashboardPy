import sys
import os
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QGridLayout, QLabel, QMenu, QAction
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
import subprocess

class CustomWidget(QWidget):
    row = 0
    column = 0
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setWindowTitle("Dropped Files")
        self.db_connection = sqlite3.connect('file_list.db')
        self.create_table()
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.load_buttons_from_database()
        

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS files
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT)''')
        self.db_connection.commit()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            file_name = os.path.basename(file_path)
            self.create_button(file_name, file_path)
            self.insert_file(file_name, file_path)

        event.acceptProposedAction()

    def create_button(self, name, path):
        button = QPushButton()
        button.setFixedSize(150, 150)
        
        # generate a random color and apply it to the button
        button.setStyleSheet("background-color: #"+str(hex(hash(path)))[3:9])
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(lambda: self.show_context_menu(button, path))

        # label shall be spilt in multliple lines if lenght exceeds 100
        if(len(name)>20):
            name = name[:20] + '\n' + name[20:]
        label = QLabel(
            name)
        label.setWordWrap(True)
        
        label.setStyleSheet("font: 20px;")
        label.setWordWrap(True)  # Enable text wrapping on the label
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Center-align the text
        label.setMaximumWidth(200)  # Limit the label width
        label.setMargin(5)  # Add some margin around the text

        layout = QGridLayout(button)
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignLeft)  # Left-align the label within the button

        button.clicked.connect(lambda: self.launch_file_or_folder(path))
        self.layout.addWidget(button,CustomWidget.row, CustomWidget.column)
        CustomWidget.column +=1
        if(CustomWidget.column>=4):
            CustomWidget.column = 0
            CustomWidget.row +=1

    def insert_file(self, name, path):
        cursor = self.db_connection.cursor()
        cursor.execute("INSERT INTO files (name, path) VALUES (?, ?)", (name, path))
        self.db_connection.commit()

    def load_buttons_from_database(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT name, path FROM files")
        files = cursor.fetchall()
        for file in files:
            file_name, file_path = file
            self.create_button(file_name, file_path)

    def launch_file_or_folder(self, path):
        home_directory = os.path.expanduser("~")
        full_path = os.path.join(home_directory, path)
        if os.path.isfile(full_path):
            subprocess.run(['start', '', full_path], cwd=os.path.dirname(full_path), shell=True)
        elif os.path.isdir(full_path):
            subprocess.run(['start', '', full_path], cwd=full_path, shell=True)

    def show_context_menu(self, button, path):
        context_menu = QMenu(self)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_button(button, path))
        context_menu.addAction(delete_action)
        context_menu.exec_(self.mapToGlobal(button.pos()))

    def delete_button(self, button, path):
        self.layout.removeWidget(button)
        button.deleteLater()
        self.delete_file_from_database(path)

    def delete_file_from_database(self, path):
        cursor = self.db_connection.cursor()
        cursor.execute("DELETE FROM files WHERE path=?", (path,))
        self.db_connection.commit()


app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("PyQt Drag and Drop")
window.setGeometry(100, 100, 600, 200)
window.setWindowFlags(Qt.WindowStaysOnTopHint)  # Set the window to always stay on top

custom_widget = CustomWidget(window)
window.setCentralWidget(custom_widget)

window.show()

sys.exit(app.exec_())
