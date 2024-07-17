from task import Task
from database import Database

from add_task_window import AddTaskWindow
from edit_task_window import EditTaskWindow
from view_task_window import ViewTaskWindow
from farmWindow import FarmWindow

from datetime import date

from PyQt5 import QtCore
from PyQt5.QtWidgets import *


class MainWindow(QMainWindow):
    '''This is a class for creating the main window of the application.
    This window stores widgets, such as a button for adding a task,
    filtering and sorting selection field and task viewing window'''
    def __init__(self) -> None:
        super().__init__()
        
        # creating the window
        self.init_main()

        # connect to database
        self.db = Database('focus_farm.db')
        self.db.create_table_todo()
        self.db.create_table_user_settings()

        # Creating widgets for main window
        self.add_task_button = QPushButton("New task")
        self.add_task_button.clicked.connect(self.open_add_task_window)
        self.create_filter_box()
        self.create_task_display()

        # Adding widgets to the window
        self.layout.addWidget(self.add_task_button)
        self.layout.addWidget(self.filter_box)
        self.layout.addWidget(self.scroll_area)

    def init_main(self) -> None:
        '''Sets the main window properties'''
        self.setWindowTitle("Focus Farm")
        self.setGeometry(400, 400, 500, 500)
        stylesheet = "* { color: black; }"
        self.setStyleSheet(stylesheet)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(40, 40, 40, 40)
        central_widget.setLayout(self.layout)
  
    def create_filter_box(self) -> None:
        '''Filter box is a groupbox that stores all widgets
        meant for setting filtering and sorting of tasks.
        This method creates these widgets and places them in the box'''

        # creating group box for filters
        filter_box_layout = QGridLayout()
        filter_box_layout.setContentsMargins(10, 10, 10, 10)
        self.filter_box = QGroupBox()
        self.filter_box.setLayout(filter_box_layout)
        self.filter_box.setFixedSize(400, 100)

        # creating widgets for filtering
        self.not_done_filter = QCheckBox('To be completed')
        self.not_done_filter.setChecked(True)
        self.done_filter = QCheckBox('Completed')
        self.priority_sort = QRadioButton('Priority')
        self.due_date_sort = QRadioButton('Due date')
        self.display_tasks_button = QPushButton('Display tasks')
        self.display_tasks_button.clicked.connect(self.display_tasks)

        # adding filter widgets to the group box
        filter_box_layout.addWidget(self.not_done_filter, 0, 0)
        filter_box_layout.addWidget(self.done_filter, 0, 1)
        filter_box_layout.addWidget(self.priority_sort, 1, 0)
        filter_box_layout.addWidget(self.due_date_sort, 1, 1)
        filter_box_layout.addWidget(self.display_tasks_button, 2, 0, 1, 2)

    def create_task_display(self) -> None:
        '''Task display is a scrolable area in which
        filtered and sorted tasks from the database can be viewed'''
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.tasks_layout = QVBoxLayout()
        self.tasks_layout.setContentsMargins(10, 10, 10, 10)
        self.tasks_layout.setAlignment(QtCore.Qt.AlignTop)
        self.tasks = QWidget()
        self.tasks.setMinimumSize(400, 1000)
        self.tasks.setLayout(self.tasks_layout)
        self.scroll_area.setWidget(self.tasks)

    def display_tasks(self) -> None:
        self.clear_display()
        tasks_to_display = self.get_filtered_and_sorted_tasks()

        colors_display = {'white': 'white', 'red': '#FFC0CB', 'yellow': '#FFF68F', 'green': '#98FB98', 'blue': '#AEC6CF'}
        
        for task in tasks_to_display:
            # creating task box
            task_box_layout = QGridLayout()
            task_box_layout.setContentsMargins(10, 10, 10, 10)
            task_box = QGroupBox()
            task_box.setLayout(task_box_layout)
            task_box.setFixedSize(400, 100)
            task_box.setStyleSheet(f"background-color: {colors_display[task.color]}")

            # creating display widgets
            finished_checkbox = QCheckBox()
            finished_checkbox.setChecked(task.is_finished)
            finished_checkbox.clicked.connect((lambda clicked, task=task, finished_checkbox=finished_checkbox: self.done_not_done(task, finished_checkbox)))
            start_button = QPushButton('Start')
            start_button.clicked.connect(lambda clicked, task=task: self.open_timer_task_window(task))
            view_button = QPushButton('View')
            view_button.clicked.connect(lambda clicked, task=task: self.open_view_task_window(task))
            edit_button = QPushButton('Edit')
            edit_button.clicked.connect(lambda clicked, task=task: self.open_edit_task_window(task))
            delete_button = QPushButton('Delete')
            delete_button.clicked.connect(lambda clicked, task=task: self.delete_task(task))
         
            # adding widgets to a task box
            task_box_layout.addWidget(finished_checkbox, 0, 0)
            task_box_layout.addWidget(QLabel(task.title), 0, 1, 1, 3)
            task_box_layout.addWidget(start_button, 1, 0)
            task_box_layout.addWidget(view_button, 1, 1)
            task_box_layout.addWidget(edit_button, 1, 2)
            task_box_layout.addWidget(delete_button, 1, 3)

            # adding task box to tasks
            self.tasks_layout.addWidget(task_box)

    def clear_display(self) -> None:
        '''clears all earlier displayed tasks'''
        for i in reversed(range(self.tasks_layout.count())):
            item = self.tasks_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                self.tasks_layout.removeWidget(widget)
                widget.deleteLater()

        self.tasks_layout.update()

    def get_filtered_and_sorted_tasks(self) -> list[Task]:
        self.retrieved_tasks = self.db.retrieve_tasks()
        tasks_to_display = []

        # filtering tasks
        for task in self.retrieved_tasks:
            if self.not_done_filter.isChecked() and task.is_finished == False:
                tasks_to_display.append(task)
            if self.done_filter.isChecked() and task.is_finished == True:
                tasks_to_display.append(task)

        # sorting tasks according to priority (if selected), with highest priority first
        if self.priority_sort.isChecked():
            tasks_to_display = sorted(tasks_to_display, key=lambda x: x.priority, reverse=True)

        # sorting tasks according to due date (if selected)
        def date_sort_key(task: Task) -> tuple[int, date | None]:
            '''Orders tasks that have no due date after all other tasks'''
            if task.due_date is None:
                return (1, None)
            else:
                return (0, task.due_date)
            
        if self.due_date_sort.isChecked():
            tasks_to_display = sorted(tasks_to_display, key=date_sort_key)

        return tasks_to_display
    
    def done_not_done(self, task: Task, finished_checkbox: QCheckBox) -> None:
        task.is_finished = finished_checkbox.isChecked()
        self.db.edit_task(task)
        self.display_tasks()

    def open_add_task_window(self) -> None:
        '''The method is called when add task button is clicked.
        It opens the window for adding a task'''
        global add_task_window
        add_task_window = AddTaskWindow(self.db)
        add_task_window.show()

    def open_edit_task_window(self, task: Task) -> None:
        '''The method is called when edit button is clicked
        for a specific task. It opens the window for editing that task'''
        global edit_task_window
        edit_task_window = EditTaskWindow(self.db, task)
        edit_task_window.show()

    def open_view_task_window(self, task: Task) -> None:
        '''The method is called when view button is clicked
        for a specific task. It opens the window for viewing that task'''
        global view_task_window
        view_task_window = ViewTaskWindow(task)
        view_task_window.show()

    def open_timer_task_window(self, task: Task) -> None:
        '''The method is called when start button is clicked.
        It opens the pygame window with the farm'''
        fw = FarmWindow(self.db, task=task)
        fw.loop()

    def delete_task(self, task: Task) -> None:
        '''The method is called when delete button is clicked
        for a specific task. It deletes that task from the database'''
        self.db.delete_task(task)
        self.display_tasks()

