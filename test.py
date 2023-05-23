import sys
import sqlite3
import time
import uuid
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLineEdit, QSizePolicy, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QWheelEvent


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard v0.0.4")
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
                uid TEXT PRIMARY KEY,
                task_name TEXT,
                color TEXT
            )
        ''')

        # Read tasks from the database and create text input fields
        self.load_tasks()

        # Create countdown button
        self.countdown_button = QPushButton("60")
        self.countdown_button.clicked.connect(self.start_countdown)
        self.layout.addWidget(self.countdown_button, self.field_row, self.field_col)

        # Create count-up button
        self.countup_button = QPushButton("5")
        self.countup_button.clicked.connect(self.start_countup)
        self.layout.addWidget(self.countup_button, self.field_row, self.field_col + 1)

        # Create counters
        self.countdown_counter = 60
        self.countup_counter = 1

        # Create timers
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countup_timer = QTimer()
        self.countup_timer.timeout.connect(self.update_countup)

        # Start the timers
        self.countdown_timer.start(1000*60)
        self.countup_timer.start(1000*60)

    def start_countdown(self):
        if self.countdown_timer.isActive():
            self.countdown_timer.stop()
        else:
            self.countdown_timer.start(1000*60)

    def start_countup(self):
        if self.countup_timer.isActive():
            self.countup_timer.stop()
        else:
            self.countup_timer.start(1000*60)

    def update_countdown(self):
        self.countdown_counter -= 1
        self.countdown_button.setText(str(self.countdown_counter))

        if self.countdown_counter < 0:
            self.countdown_button.setStyleSheet("background-color: red;")
        else:
            self.countdown_button.setStyleSheet("background-color: green;")

    def update_countup(self):
        if self.countup_counter <= 5:
            self.countup_button.setStyleSheet("background-color: green;")
        else:
            self.countup_button.setStyleSheet("background-color: red;")

        self.countup_button.setText(str(self.countup_counter))
        self.countup_counter += 1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.add_text_input_field()

    def add_text_input_field(self, task_name=None):
        text_input = CustomLineEdit()
        text_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        text_input.setFixedSize(100, 100)
        self.layout.addWidget(text_input, self.field_row, self.field_col)

        # Connect the focusOut signal to the save_text_input method
        text_input.focusOut.connect(self.save_text_input)

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
        if isinstance(sender, CustomLineEdit):
            task_name = sender.text()
            color = sender.color
            uid = sender.uid
            if uid:
                self.cursor.execute("UPDATE tasks SET task_name=?, color=? WHERE uid=?", (task_name, color, uid))
            else:
                uid = str(uuid.uuid4())
                self.cursor.execute("INSERT INTO tasks (uid, task_name, color) VALUES (?, ?, ?)", (uid, task_name, color))
                sender.uid = uid
            self.conn.commit()

    def load_tasks(self):
        self.cursor.execute("SELECT uid, task_name, color FROM tasks")
        tasks = self.cursor.fetchall()
        for task in tasks:
            uid = task[0]
            task_name = task[1]
            color = task[2]
            self.add_text_input_field(task_name)
            last_widget = self.layout.itemAt(self.layout.count() - 1).widget()
            last_widget.set_color(color)
            last_widget.uid = uid


class CustomLineEdit(QLineEdit):
    focusOut = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.color = "white"
        self.uid = ""

    def wheelEvent(self, event: QWheelEvent):
        colors = ["green", "yellow", "red", "white"]
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

    def focusOutEvent(self, event):
        self.focusOut.emit()


app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec_())
