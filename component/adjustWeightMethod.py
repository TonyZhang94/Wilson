# -*- coding:utf-8 -*-

from Wilson.tools.utils import load, dump


class AdjustWeightMethod(object):
    """Adjust Method"""
    def __init__(self):
        """Init"""

    def adjust(self):
        """Adjust Method"""
        raise NotImplementedError


class NotAdjustWeightMethod(AdjustWeightMethod):
    """Not Adjust Weight Method"""
    def adjust(self):
        df = load("info")
        del df["datamonth"]
        dump(df, "info")


class AdjustWeightByFussySetMethod(AdjustWeightMethod):
    """Adjust Weight By Fussy Set Method"""
    def adjust(self):
        pass
