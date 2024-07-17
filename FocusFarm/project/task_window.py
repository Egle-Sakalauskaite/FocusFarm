from database import Database
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont


class TaskWindow(QtWidgets.QWidget):
    '''Abstract task window that serves as a superclass for
    AddTaskWindow and EditTaskWindow'''
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db

        # creating the window
        self.setWindowTitle("Focus Farm")
        self.setGeometry(100, 400, 600, 400)
        self.layout = QGridLayout()
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.setLayout(self.layout)

        self.create_widgets()
        self.add_widgets()

    def create_widgets(self) -> None:
        '''Creates all the widgets for the window'''
        # text widgets
        self.title_edit = QLineEdit()
        big_font = QFont()
        big_font.setPointSize(16)
        self.title_edit.setFont(big_font)
        self.description_edit = QTextEdit()

        # date and time widgets
        self.due_date_optional = QCheckBox('Due date')
        self.due_date_select = QDateEdit()
        self.due_date_select.setCalendarPopup(True)
        self.due_date_select.setEnabled(False)
        self.est_duration_select = QTimeEdit()
        self.est_duration_select.setDisplayFormat("HH:mm")

        # priority slider
        self.priority_select = QSlider()
        self.priority_select.setOrientation(Qt.Horizontal)
        self.priority_select.setRange(1, 5)

        # color select radio buttons
        self.color_white = QRadioButton()
        self.color_white.setStyleSheet("QRadioButton { background-color: white}")
        self.color_red = QRadioButton()
        self.color_red.setStyleSheet("QRadioButton { background-color: #FFC0CB}")
        self.color_yellow = QRadioButton()
        self.color_yellow.setStyleSheet("QRadioButton { background-color: #FFF68F}")
        self.color_green = QRadioButton()
        self.color_green.setStyleSheet("QRadioButton { background-color: #98FB98}")
        self.color_blue = QRadioButton()
        self.color_blue.setStyleSheet("QRadioButton { background-color: #AEC6CF}")
        self.color_buttons = {self.color_white: 'white', self.color_red: 'red', self.color_yellow: 'yellow', self.color_green: 'green', self.color_blue: 'blue'}

        # save button
        self.save_button = QPushButton("Save")

    def add_widgets(self) -> None:
        '''Adds all widgets to the window'''
        self.layout.addWidget(self.title_edit, 0, 1, 1, 6)
        self.layout.addWidget(self.due_date_optional, 1, 0, 1, 2)
        self.layout.addWidget(self.due_date_select, 1, 2, 1, 2)
        self.layout.addWidget(QLabel("Estimated durration"), 1, 4, 1, 2)
        self.layout.addWidget(self.est_duration_select, 1, 6, 1, 2)
        self.layout.addWidget(self.description_edit, 2, 0, 1, 7)
        self.layout.addWidget(QLabel('Priority:'), 3, 0)
        self.layout.addWidget(QLabel('Low'), 3, 1)
        self.layout.addWidget(self.priority_select, 3, 2, 1, 5)
        self.layout.addWidget(QLabel('Urgent'), 3, 7)
        self.layout.addWidget(QLabel("Color"), 4, 1)

        col_index = 2
        for button in self.color_buttons.keys():
            self.layout.addWidget(button, 4, col_index)
            col_index += 1

        self.layout.addWidget(self.save_button, 5, 3, 1, 2)

    def date_edit_status(self) -> None:
        '''Disables the date selection widget if the due date option is unchecked'''
        if self.due_date_optional.isChecked():
            self.due_date_select.setEnabled(True)
        else:
            self.due_date_select.setEnabled(False)
