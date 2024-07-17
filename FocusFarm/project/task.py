from datetime import date


class Task:
    def __init__(self, **kwargs) -> None:
        self.id: int | None = kwargs.get('id', None)
        self.title: str = kwargs.get('title', 'New task')
        self.description: str = kwargs.get('description', '')
        self.est_duration: int = kwargs.get('est_duration', 30)
        self.priority: int = kwargs.get('priority', 1)
        self.color: str = kwargs.get('color', 'white')
        self.due_date: date | None = kwargs.get('due_date', None)
        self.progress: int = kwargs.get('progress', 0.0)
        self.date_added: date = kwargs.get('date_added', date.today())
        self.date_edited: date = kwargs.get('date_edited', date.today())
        self.is_started: bool = kwargs.get('is_started', False)
        self.is_finished: bool = kwargs.get('is_finished', False)
    
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, new_title):
        '''Sets the title with character limit of 40.'''
        if len(new_title) > 40:
            raise ValueError('The character limit is 40')
        self._title = new_title

    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, new_description: str) -> None:
        '''Sets the description with character limit of 200.'''
        if len(new_description) > 200:
            raise ValueError('The character limit is 200')
        self._description = new_description

    @property
    def est_duration(self) -> int:
        return self._est_duration
    
    @est_duration.setter
    def est_duration(self, new_est_duration: int) -> None:
        '''Sets the estimated duration ahecks that it is positive'''
        if new_est_duration < 0:
            raise ValueError('estimated duration must be positive')
        self._est_duration = new_est_duration

    @property
    def priority(self) -> int:
        return self._priority
    
    @priority.setter
    def priority(self, new_priority: int) -> None:
        '''Sets the priority level as an intiger between 1 - 5'''
        if 1 <= new_priority <= 5:
            self._priority = new_priority
        else:
            raise ValueError('Priority level must be between 1 - 5')

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, new_color: str) -> None:
        '''Sets the color to white, red, yellow, green or blue'''
        available_colors = ['white', 'red', 'yellow', 'green', 'blue']
        if new_color not in available_colors:
            raise ValueError(f'The available colors are: {available_colors}')
        self._color = new_color
        
    @property
    def due_date(self) -> date:
        return self._due_date
    
    @due_date.setter
    def due_date(self, new_due_date: date) -> None:
        '''Sets the due date and if this is a new task, checks that it is not set to date earlier than today'''
        if new_due_date is not None:
            if self.id is None and new_due_date < date.today():
                raise ValueError('Due date cannot be set to a date earlier than today')
        self._due_date = new_due_date            

    @property
    def progress(self) -> float:
        return self._progress
    
    @progress.setter
    def progress(self, new_progress: float) -> None:
        '''Sets the progress and checks that it is positive'''
        if new_progress < 0:
            raise ValueError('progress must be positive')
        self._progress = new_progress

    @property
    def is_finished(self) -> bool:
        return self._is_finished
    
    @is_finished.setter
    def is_finished(self, new_status: bool) -> None:
        '''sets the statu of completeness. When set to finished, sets the progress equal to estimted duration'''
        if new_status == True:
            self.progress = self.est_duration
        self._is_finished = new_status

    def start_task(self) -> None:
        self.is_started = True

    def finish_task(self) -> None:
        self.is_finished = True
    