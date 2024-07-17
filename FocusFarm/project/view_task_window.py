from task import Task
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

class ViewTaskWindow(QWidget):
    '''Window that displays the task in detail'''

    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task = task

        # creating the window
        self.setWindowTitle("Focus Farm")
        self.setGeometry(100, 400, 400, 400)
        self.layout = QGridLayout()
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.setLayout(self.layout)

        colors_display = {'white': 'white', 'red': '#FFC0CB', 'yellow': '#FFF68F', 'green': '#98FB98', 'blue': '#AEC6CF'}
        self.color = colors_display[self.task.color]
        
        self.create_widgets()
        self.add_widgets()

    def create_widgets(self) -> None:
        '''Creates widgets of the task'''
        self.title = QLabel(self.task.title)
        big_font = QFont()
        big_font.setPointSize(16)
        self.title.setFont(big_font)
        self.title.setStyleSheet(f"background-color: {self.color}")
        self.due_date = QLabel(f'Due: {self.task.due_date}')
        self.description = QTextBrowser()
        self.description.setPlainText(self.task.description)
        self.progress_bar = QProgressBar()
        prog = self.task.progress/self.task.est_duration
        self.progress_bar.setValue(int(100*prog))
        priority_levels = {1: 'low', 2: 'medium', 3: 'high', 4: 'important', 5: 'urgent'}
        self.priority = QLabel(f'Priority: {priority_levels[self.task.priority]}')
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

    def add_widgets(self) -> None:
        '''Adds all task widgets to the window'''
        self.layout.addWidget(self.title, 0, 0, 2, 4)

        if self.task.due_date is not None:
            self.layout.addWidget(self.due_date, 0, 4, 1, 2)
        else:
            self.layout.addWidget(QLabel('No due date'), 0, 4, 1, 2)

        self.layout.addWidget(self.priority, 1, 4, 1, 2)
        self.layout.addWidget(self.progress_bar, 2, 0, 1, 6)
        self.layout.addWidget(QLabel(f'Added: {self.task.date_added}'), 3, 0, 1, 3)
        self.layout.addWidget(QLabel(f'Last Edited: {self.task.date_edited}'), 3, 3, 1, 3)
        self.layout.addWidget(self.description, 4, 0, 1, 6)
        self.layout.addWidget(self.close_button, 5, 2, 1, 2)
