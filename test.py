import sqlite3
import sys
import uuid

import win32com.client
from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QPlainTextEdit, QSizePolicy, QPushButton, \
    QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard v0.0.4")
        self.setGeometry(100, 100, 400, 300)

        # Create a central widget and set it as the main window's central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout for the main window
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create a grid layout for the text input fields
        self.layout = QGridLayout()
        self.main_layout.addLayout(self.layout)

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

        # Create a panel widget for the buttons
        self.panel_widget = QWidget(self.central_widget)
        self.panel_layout = QHBoxLayout(self.panel_widget)
        self.panel_widget.setFixedSize(200, 50)

        # Create countdown button
        self.countdown_button = QPushButton("Countdown")
        self.countdown_button.clicked.connect(self.start_countdown)
        self.panel_layout.addWidget(self.countdown_button)

        # Create count-up button
        self.countup_button = QPushButton("Countup")
        self.countup_button.clicked.connect(self.start_countup)
        self.panel_layout.addWidget(self.countup_button)

        self.unread_emails_button = QPushButton("Emails: ")
        self.panel_layout.addWidget(self.unread_emails_button)

        # Add the panel widget to the main layout
        self.main_layout.addWidget(self.panel_widget)

        # Create counters
        self.countdown_counter = 60
        self.countup_counter = 1

        # Create timers
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countup_timer = QTimer()
        self.countup_timer.timeout.connect(self.update_countup)

        # Start the timers
        self.countdown_timer.start(60000)
        self.countup_timer.start(60000)

        # Create the label for current time
        self.current_time_label = QLabel(self)
        self.current_time_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        font = QFont()
        font.setPointSize(30)
        self.current_time_label.setFont(font)
        self.main_layout.addWidget(self.current_time_label)

        # Create a timer to update the current time label every second
        self.update_time_timer = QTimer()
        self.update_time_timer.timeout.connect(self.update_current_time)
        self.update_time_timer.start(1000)

        # Update the initial current time
        self.update_current_time()

        # Create a timer to update the current time label every second
        self.update_email_counter = QTimer()
        self.update_email_counter.timeout.connect(self.set_unread_email_count)
        self.update_email_counter.start(60000)

        self.intialize()

    def intialize(self):
        self.update_countdown()
        self.update_countup()

    def update_current_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.current_time_label.setText(current_time)

    def start_countdown(self):
        if self.countdown_timer.isActive():
            self.countdown_timer.stop()
            self.countdown_counter = 60
        else:
            self.countdown_timer.start(1000)

        self.update_countdown()

    def start_countup(self):
        if self.countup_timer.isActive():
            self.countup_timer.stop()
            self.countup_counter = 5
        else:
            self.countup_timer.start(1000)

        self.update_countup()

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
        elif event.button() == Qt.RightButton:
            sender = self.sender()
            if isinstance(sender, CustomLineEdit):
                self.delete_text_input(sender)

    def delete_text_input(self, pos):
        sender = self.sender()
        if isinstance(sender, CustomLineEdit):
            self.layout.removeWidget(sender)
            sender.deleteLater()

    def add_text_input_field(self, task_name=None):
        text_input = CustomLineEdit()
        text_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        text_input.setFixedSize(100, 100)
        self.layout.addWidget(text_input, self.field_row, self.field_col)

        # Connect the focusOut signal to the save_text_input method
        text_input.focusOut.connect(self.save_text_input)

        # Set the initial task name if provided
        if task_name:
            text_input.setPlainText(task_name)

        # Update field position in the grid
        self.field_col += 1
        if self.field_col == 4:
            self.field_col = 0
            self.field_row += 1

    def save_text_input(self):
        sender = self.sender()
        if isinstance(sender, CustomLineEdit):
            task_name = sender.toPlainText()
            color = sender.color
            uid = sender.uid
            if uid:
                self.cursor.execute("UPDATE tasks SET task_name=?, color=? WHERE uid=?", (task_name, color, uid))
            else:
                uid = str(uuid.uuid4())
                self.cursor.execute("INSERT INTO tasks (uid, task_name, color) VALUES (?, ?, ?)",
                                    (uid, task_name, color))
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

    def set_unread_email_count(self):
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)  # 6 represents the Inbox folder

        unread_count = 0
        for item in inbox.Items:
            if item.UnRead:
                unread_count += 1
        self.unread_emails_button.setText("Emails:" + str(unread_count))

class CustomLineEdit(QPlainTextEdit):
    focusOut = pyqtSignal()
    rightClicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.color = "white"
        self.uid = ""
        self.setFixedHeight(100)

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

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            super().mousePressEvent(event)

    def get_unread_email_count(self):
        return 0
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)  # 6 represents the Inbox folder

        unread_count = 0
        for item in inbox.Items:
            if item.UnRead:
                unread_count += 1

        return unread_count


app = QApplication(sys.argv)
window = MyWindow()
window.setWindowFlag(Qt.WindowStaysOnTopHint)  # Keep the window on top
window.show()
sys.exit(app.exec_())
