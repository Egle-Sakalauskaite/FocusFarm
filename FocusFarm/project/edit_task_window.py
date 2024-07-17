from task import Task
from task_window import TaskWindow
from database import Database
from datetime import datetime
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import *


class EditTaskWindow(TaskWindow):
    '''Subclass of TaskWindow used for editing existing tasks from the database'''

    def __init__(self, db: Database, task: Task) -> None:
        super().__init__(db)
        self.db = db
        self.task = task

        self.set_default_values()

        # setting the function calls for clickable widgets
        self.due_date_optional.stateChanged.connect(self.date_edit_status)
        self.save_button.clicked.connect(self.edit_task)

    def set_default_values(self) -> None:
        '''sets the widgets according to the current task attributes'''
        self.title_edit.setText(self.task.title)
        self.description_edit.setPlainText(self.task.description)

        if self.task.due_date:
            self.due_date_optional.setChecked(True)
            self.due_date_select.setDate(self.task.due_date)

        hours = self.task.est_duration // 60
        minutes = self.task.est_duration % 60
        self.est_duration_select.setTime(QTime(hours, minutes))
        self.priority_select.setValue(self.task.priority)

        for button in self.color_buttons:
            if self.task.color == self.color_buttons[button]:
                button.setChecked(True)

    def edit_task(self):
        '''Gathers the input from the widgets and saves it to the database'''
        self.task.title = self.title_edit.text()
        self.task.description = self.description_edit.toPlainText()
        
        if self.due_date_optional.isChecked():
            due_date_input = self.due_date_select
            qdate_str = due_date_input.date().toString('yyyy-MM-dd')
            self.task.due_date = datetime.strptime(qdate_str, '%Y-%m-%d').date()
        else:
            self.task.due_date = None

        new_time_selected = self.est_duration_select.time()
        self.task.est_duration = 60*new_time_selected.hour() + new_time_selected.minute()
        self.task.priority = self.priority_select.value()

        self.task.color = 'white'

        for button in self.color_buttons.keys():
            if button.isChecked():
                self.task.color = self.color_buttons[button]

        self.db.edit_task(self.task)
        self.close()