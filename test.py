import pytz
import sqlite3
import sys
import uuid
# Import the required classes
from datetime import datetime
from pytz import timezone
from datetime import datetime, timezone
import win32com.client
from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QPlainTextEdit, QSizePolicy, QPushButton, \
    QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QStyleFactory
from  PyQt5.QtGui import QPalette, QColor
from PyQt5.QtGui import QTextCursor, QColor
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat, QFont, QWheelEvent

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

        # Create the label for current time
        self.current_time_label = QLabel(self)
        self.current_time_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        font = QFont()
        font.setPointSize(30)
        self.current_time_label.setFont(font)
        self.main_layout.addWidget(self.current_time_label)

        # Create the label for next meeting time
        self.next_meeting_label = QLabel(self)
        self.next_meeting_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        font = QFont()
        font.setPointSize(10)
        self.next_meeting_label.setFont(font)
        self.main_layout.addWidget(self.next_meeting_label)

        QApplication.setStyle(QStyleFactory.create("Fusion"))


        # Set initial transparency state
        self.is_transparent = False

        self._routine_task()

        # Create timers
        self._timer = QTimer()
        self._timer.timeout.connect(self._routine_task)
        # Start the timer
        self._timer.start(60000)


    def _routine_task(self):
        #self.set_unread_email_count() its very slow. 
        self.update_current_time()
        self.update_countdown()
        self.update_countup()
        #self.update_next_meeting_time()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if not self.is_transparent:
                self.setWindowOpacity(0.1)  # Set window to 20% transparency
                self.is_transparent = True
            else:
                self.setWindowOpacity(1.0)  # Restore full opacity
                self.is_transparent = False

        # Call the base class implementation to handle other key presses
        super().keyPressEvent(event)


    def update_next_meeting_time(self):
        import win32com.client
        import datetime
        from pytz import timezone

        # Connect to Outlook
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")

        # Get the default calendar folder
        calendar_folder = namespace.GetDefaultFolder(9)  # 9 represents the default calendar folder

        # Get the items in the calendar folder
        items = calendar_folder.Items

        # Sort the items by start time in ascending order
        items.Sort("[Start]")

        # Find the next meeting
        now = datetime.datetime.now()
        now = now.replace(tzinfo=timezone('UTC'))  # Replace 'Your_Time_Zone' with your actual time zone
        next_meeting = None
        for item in items:
            if item.Start >= now:
                next_meeting = item
                break

        # Calculate the remaining time for the next meeting
        if next_meeting:
            self.next_meeting_label.setText(
                next_meeting.location + "- " + str(next_meeting.Start) + "-" + next_meeting.subject)


    def get_next_meeting_time(self):
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        calendar = namespace.GetDefaultFolder(9)  # 9 represents the Calendar folder

        now = datetime.now(pytz.utc)  # Use UTC timezone for comparison
        next_meeting_time = None

        # Iterate over calendar items to find the next meeting in the future
        for item in calendar.Items:
            if item.MeetingStatus == 1 and item.Start >= now:
                next_meeting_time = item.Start
                break

        return next_meeting_time


    def update_current_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm")
        self.current_time_label.setText(current_time)


    def start_countdown(self):
        self.countdown_counter = 60
        self.update_countdown()


    def start_countup(self):
        self.countup_counter = 5
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
        if event.button() == Qt.LeftButton and event.modifiers() == Qt.AltModifier:
            self.add_text_input_field()
        elif event.button() == Qt.RightButton:
            sender = self.sender()
            if isinstance(sender, CustomLineEdit):
                self.delete_text_input(sender)

    def delete_text_input(self, uid):
        sender = self.sender()
        if isinstance(sender, CustomLineEdit):
            if sender.toPlainText().strip() == "":
                self.layout.removeWidget(sender)
                sender.deleteLater()

                # Remove the task from the database
                self.cursor.execute("DELETE FROM tasks WHERE uid=?", (uid,))
                self.conn.commit()


    def add_text_input_field(self, task_name=None):
        text_input = CustomLineEdit()
        text_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        text_input.setFixedSize(200, 200)
        self.layout.addWidget(text_input, self.field_row, self.field_col)

        # Connect the focusOut signal to the save_text_input method
        text_input.focusOut.connect(self.save_text_input)

        # Connect the rightClicked signal to the delete_text_input method
        text_input.rightClicked.connect(self.delete_text_input)

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
    rightClicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.color = "black"
        self.uid = ""
        self.setFixedHeight(200)
        self.setMinimumSize(200, 200)  # Ensuring minimum size
        font = QFont()
        font.setPointSize(15)  # Set minimum font size to 15
        self.setFont(font)
        self.setStyleSheet(f"background-color: {self.color};")
        
        

    def wheelEvent(self, event: QWheelEvent):
        colors = ["green", "yellow", "red", "white","black"]
        current_color_index = colors.index(self.color)
        new_color_index = (current_color_index + 1) % len(colors)
        self.set_color(colors[new_color_index])

    def set_color(self, color):
        self.color = color
        self.setStyleSheet(f"background-color: {color};")

        # Adjust text color based on background color
        if color in ["green", "red", "yellow"]:
            text_color = "black"
        else:
            text_color = "green"
        
        # Set text color and font size
        text_cursor = self.textCursor()
        text_cursor.select(QTextCursor.Document)
        text_format = self._get_text_format(QColor(text_color))
        text_format.setFontPointSize(15)  # Set font size to 15
        text_cursor.setCharFormat(text_format)
        text_cursor.movePosition( QTextCursor.End );
        self.setTextCursor(text_cursor)

    def _get_text_format(self, color):
        text_format = QTextCharFormat()
        text_format.setForeground(color)
        return text_format

    def focusOutEvent(self, event):
        self.focusOut.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.rightClicked.emit(self.uid)
        else:
            super().mousePressEvent(event)


    def get_unread_email_count(self):
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)  # 6 represents the Inbox folder

        unread_count = 0
        for item in inbox.Items:
            if item.UnRead:
                unread_count += 1

        return unread_count


app = QApplication(sys.argv)

dark_palette = QPalette()
dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
dark_palette.setColor(QPalette.WindowText, Qt.white)
dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
dark_palette.setColor(QPalette.ToolTipText, Qt.white)
dark_palette.setColor(QPalette.Text, Qt.white)
dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
dark_palette.setColor(QPalette.ButtonText, Qt.white)
dark_palette.setColor(QPalette.BrightText, Qt.red)
dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
dark_palette.setColor(QPalette.HighlightedText, Qt.black)
dark_palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
app.setPalette(dark_palette)
window = MyWindow()
window.setWindowFlag(Qt.WindowStaysOnTopHint)  # Keep the window on top
window.show()
sys.exit(app.exec_())
