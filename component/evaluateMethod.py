# -*- coding:utf-8 -*-

import pandas as pd

from Wilson.settings import Parameters
from Wilson.tools.utils import load, dump


class EvaluateMethod(object):
    """Evaluate Method"""
    def __init__(self):
        """Init"""

    def evaluate(self):
        """Evaluate Function"""
        raise NotImplementedError

    @staticmethod
    def evaluate_score(n, p, z):
        try:
            y = (p + z ** 2 / (2 * n) - z * (p * (1 - p) / n + z ** 2 / (4 * n ** 2)) ** 0.5) / \
                (1 + z ** 2 / n)
        except ZeroDivisionError:
            y = 0
        return y


class EvaluateTargetByWilsonMethod(EvaluateMethod):
    """Evaluate Targets By Wilson Confidence Interval"""
    def __init__(self):
        self.z = Parameters.zTarget

    def evaluate(self):
        df = load("info")
        for k, v in df.iterrows():
            df.at[k, "target_wilson"] = self.evaluate_score(v["target_n"], v["target_p"], self.z)
        dump(df, "info")


class EvaluateTagByWilsonMethod(EvaluateMethod):
    """Evaluate Tags By Wilson Confidence Interval"""
    def __init__(self):
        self.z = Parameters.zTag

    def evaluate(self):
        origin = load("info")
        df = origin.drop_duplicates(["brand", "model", "tag"])
        for k, v in df.iterrows():
            df.at[k, "tag_wilson"] = self.evaluate_score(v["tag_n"], v["tag_p"], self.z)
        df = df[["brand", "model", "tag", "tag_wilson"]]
        dump(pd.merge(origin, df, "left", on=["brand", "model", "tag"]), "info")


class EvaluateModelByWilsonMethod(EvaluateMethod):
    """Evaluate Models By Wilson Confidence Interval"""
    def __init__(self):
        self.z = Parameters.zModel

    def evaluate(self):
        origin = load("info")
        df = origin.drop_duplicates(["brand", "model"])
        for k, v in df.iterrows():
            df.at[k, "model_wilson"] = self.evaluate_score(v["model_n"], v["model_p"], self.z)
        df = df[["brand", "model", "model_wilson"]]
        dump(pd.merge(origin, df, "left", on=["brand", "model"]), "info")
