# -*- coding:utf-8 -*-

import datetime
import math

from Wilson.tools.utils import load, dump


class AdjustWeightMethod(object):
    """Adjust Method"""
    def __init__(self):
        """Init"""
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        self.current = (year - 2000 - 1) * 12 + month
        self.record = dict()

    def adjust(self):
        """Adjust Method"""
        raise NotImplementedError

    def make_record(self, datamonths):
        for datamonth in datamonths:
            text = str(datamonth)
            year = int(text[: 4])
            month = int(text[4:])
            self.record[datamonth] = (year - 2000 - 1) * 12 + month


class NotAdjustWeightMethod(AdjustWeightMethod):
    """Not Adjust Weight Method"""
    def adjust(self):
        df = load("info")
        del df["datamonth"]
        dump(df, "info")


class AdjustWeightByFussySetMethod(AdjustWeightMethod):
    """Adjust Weight By Fussy Set Method"""
    def __init__(self):
        super().__init__()
        self.publish = None

    def adjust(self):
        df = load("info")
        self.make_record(datamonths=set(df["datamonth"].values))
        self.publish = min(self.record.values())
        for k, v in df.iterrows():
            df.at[k, "frequency"] = v["frequency"] * math.e ** (
                    (self.record[v["datamonth"]] - self.publish) / (self.current - self.publish))
            # df.at[k, "frequency"] = v["frequency"] * (
            #         (self.record[v["datamonth"]] - self.publish) / (self.current - self.publish))
        del df["datamonth"]
        dump(df, "info")
