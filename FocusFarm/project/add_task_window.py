import sys
sys.path.append("project")
from task import Task
from task_window import TaskWindow
from database import Database
from datetime import datetime
from PyQt5.QtCore import QDate, QTime
from PyQt5.QtWidgets import *


class AddTaskWindow(TaskWindow):
    '''Subclass of TaskWindow used for adding new tasks to the database'''
    def __init__(self, db: Database) -> None:
        super().__init__(db)

        # setting placeholders
        self.title_edit.setPlaceholderText('Title')
        self.description_edit.setPlaceholderText('Task description')

        # setting default values
        self.priority_select.setValue(1)
        self.due_date_select.setDate(QDate.currentDate())
        self.est_duration_select.setTime(QTime(0, 30))

        # setting the function calls for clickable widgets
        self.due_date_optional.stateChanged.connect(self.date_edit_status)
        self.save_button.clicked.connect(self.add_task)

    def add_task(self) -> None:
        '''Gathers the input from the widgets and saves it to the database'''
        title = self.title_edit.text()
        description = self.description_edit.toPlainText()

        if self.due_date_optional.isChecked():
            '''This conversion is too comlex, think of better solution'''
            due_date_input = self.due_date_select
            qdate_str = due_date_input.date().toString('yyyy-MM-dd')
            due_date = datetime.strptime(qdate_str, '%Y-%m-%d').date()
        else:
            due_date = None

        time_selected = self.est_duration_select.time()
        est_duration = 60*time_selected.hour() + time_selected.minute()
        priority = self.priority_select.value()
        color = 'white'

        for button in self.color_buttons.keys():
            if button.isChecked():
                color = self.color_buttons[button]

        task = Task(title=title,
                    description=description,
                    est_duration=est_duration,
                    priority=priority,
                    color=color,
                    due_date=due_date)
        
        self.db.add_task(task)
        self.close()