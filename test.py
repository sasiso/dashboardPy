import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLineEdit, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWheelEvent


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard v0.0.3")
        self.setGeometry(100, 100, 400, 300)

        # Create a central widget and set it as the main window's central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a grid layout for the text input fields
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        # Initialize field position in the grid
        self.field_row = 0
        self.field_col = 0

        # Connect to the SQLite database
        self.conn = sqlite3.connect('dashboard.db')
        self.cursor = self.conn.cursor()

        # Create the tasks table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task_name TEXT,
                color TEXT
            )
        ''')

        # Read tasks from the database and create text input fields
        self.load_tasks()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.add_text_input_field()

    def add_text_input_field(self, task_name=None):
        text_input = CustomLineEdit()
        text_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        text_input.setFixedSize(100, 100)
        self.layout.addWidget(text_input, self.field_row, self.field_col)

        # Connect the returnPressed signal to the save_text_input method
        text_input.returnPressed.connect(self.save_text_input)

        # Set the initial task name if provided
        if task_name:
            text_input.setText(task_name)

        # Update field position in the grid
        self.field_col += 1
        if self.field_col == 4:
            self.field_col = 0
            self.field_row += 1

    def save_text_input(self):
        sender = self.sender()
        if isinstance(sender, QLineEdit):
            task_name = sender.text()
            color = sender.color
            self.cursor.execute("INSERT INTO tasks (task_name, color) VALUES (?, ?)", (task_name, color))
            self.conn.commit()

    def load_tasks(self):
        self.cursor.execute("SELECT task_name, color FROM tasks")
        tasks = self.cursor.fetchall()
        for task in tasks:
            task_name = task[0]
            color = task[1]
            self.add_text_input_field(task_name)
            last_widget = self.layout.itemAt(self.layout.count() - 1).widget()
            last_widget.set_color(color)


class CustomLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.color = "white"

    def wheelEvent(self, event: QWheelEvent):
        colors = ["green", "yellow", "red", "white" ]
        current_color_index = colors.index(self.color)
        new_color_index = (current_color_index + 1) % len(colors)
        self.set_color(colors[new_color_index])

    def set_color(self, color):
        self.color = color
        if color == "green":
            self.setStyleSheet("background-color: green;")
        elif color == "red":
            self.setStyleSheet("background-color: red;")
        elif color == "yellow":
            self.setStyleSheet("background-color: yellow;")
        else:
            self.setStyleSheet("background-color: white;")


app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec_())
