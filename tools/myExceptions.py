# -*- coding:utf-8 -*-


class ReadDBException(Exception):
    """Choose Get Data From DB"""


class RegisterDBException(Exception):
    """Choose Get Data From DB"""


class InstantiationError(Exception):
    def __init__(self):
        err = "Instantiation Is Not Allowed"
        Exception.__init__(self, err)


class MultiEngineError(Exception):
    """MultiEngineError"""


class TaskTypeException(Exception):
    """TaskTypeException"""
