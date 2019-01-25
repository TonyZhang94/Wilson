# -*- coding:utf-8 -*-


from Wilson.tools.myExceptions import TaskTypeException
from Wilson.tools.decorator import ignore_warning
from Wilson.component.tasksObj import *


class Tasks(object):
    def __init__(self):
        self.tasks = list()

    def assign(self, task):
        if isinstance(task, TasksObj):
            if not hasattr(task, "doc"):
                task.doc = task.obj.__doc__
            self.tasks.append(task)
        else:
            raise TaskTypeException

    @logging
    @ignore_warning
    def execute(self):
        for serial, task in enumerate(self, start=1):
            self.__execute(serial, task)

    @staticmethod
    def __execute(serial, task):
        print("\nStep", serial, "Processing ...")
        print("Task Doc:", task.doc)
        task.execute()

    def __iter__(self):
        return TasksIterator(self.tasks)


class TasksIterator(object):
    def __init__(self, tasks):
        self.tasks = tasks
        self.index = 0

    def __next__(self):
        try:
            task = self.tasks[self.index]
        except IndexError:
            raise StopIteration()
        self.index += 1
        return task

    def __iter__(self):
        return self
