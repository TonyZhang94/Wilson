# -*- coding:utf-8 -*-

from Wilson.tools.decorator import *
from Wilson.tools.public import Descriptor
from Wilson.component.initMethod import *
from Wilson.component.getDataMethod import *
from Wilson.component.adjustWeightMethod import *
from Wilson.component.calBaseLineMethod import *
from Wilson.component.evaluateMethod import *
from Wilson.component.rankMethod import *
from Wilson.component.clearFileMethod import *


class TasksObj(object):
    """Tasks Obj Base Class"""
    def __init__(self, *args, **kwargs):
        """Init Function"""

    def execute(self):
        """Excute Commands"""
        raise NotImplementedError


class InitCommand(TasksObj):
    obj = Descriptor(InitMethod)

    def __init__(self, method):
        self.obj = method()

    @logging
    def execute(self):
        self.obj.init()


class GetDataCommand(TasksObj):
    obj = Descriptor(GetDataMethod)

    def __init__(self, method, param=None):
        self.obj = method()
        if param is not None:
            self.obj.param = param

        if hasattr(self.obj, "param"):
            self.doc = self.obj.__doc__ + " // param " + str(self.obj.param)

    @logging
    def execute(self):
        self.obj.get()


class AdjustWeightCommand(TasksObj):
    obj = Descriptor(AdjustWeightMethod)

    def __init__(self, method):
        self.obj = method()

    @logging
    def execute(self):
        self.obj.adjust()


class CalBaseLineCommand(TasksObj):
    obj = Descriptor(CalBaseLineMethod)

    def __init__(self, method):
        self.obj = method()

    @logging
    def execute(self):
        self.obj.cal()


class EvaluateCommand(TasksObj):
    obj = Descriptor(EvaluateMethod)

    def __init__(self, method, z=None):
        self.obj = method()
        if z is not None:
            self.obj.z = z

        if hasattr(self.obj, "z"):
            self.doc = self.obj.__doc__ + " // z " + str(self.obj.z)

    @logging
    def execute(self):
        self.obj.evaluate()


class RankCommand(TasksObj):
    obj = Descriptor(RankMethod)

    def __init__(self, method):
        self.obj = method()

    @logging
    def execute(self):
        self.obj.rank()


class ClearFileCommand(TasksObj):
    obj = Descriptor(ClearFileMethod)

    def __init__(self, method):
        if Mode.clearLOCAL or method is None:
            self.obj = method()
        else:
            self.obj = ClearNothingMethod()

    @logging
    def execute(self):
        self.obj.clear()
