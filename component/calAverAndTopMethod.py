# -*- coding:utf-8 -*-

import pandas as pd

from Wilson.settings import Parameters
from Wilson.tools.utils import load, dump


class CalAverAndTopMethod(object):
    "Calculate Average And Top Information Method"
    def __init__(self):
        """Init"""

    def cal(self):
        """Calculate Function"""
        raise NotImplementedError


class CalTargetAverAndTopMethod(CalAverAndTopMethod):
    """Calculate Average And Top Infomation Of Target"""
    def cal(self):
        df = load("info")
        df = df.groupby(["tag", "target"]).apply(self.cal_aver_top)
        dump(df, "info")

    @staticmethod
    def cal_aver_top(df):
        df["top_target"] = df['model_target_ratings'].max()
        size = len(df)
        if size:
            df["aver_model_target_ratings"] = round(df['model_target_ratings'].sum() / size, 2)
        else:
            df["aver_model_target_ratings"] = 0
        return df


class CalTagAverAndTopMethod(CalAverAndTopMethod):
    """Calculate Average And Top Infomation Of Tag"""
    def cal(self):
        origin = load("info")
        df = origin.drop_duplicates(["brand", "model", "tag"])
        df = df.groupby(["tag"]).apply(self.cal_aver_top)
        df = df.drop_duplicates(["tag"])[["tag", "top_tag", "aver_model_tag_ratings"]]
        dump(pd.merge(origin, df, "left", on=["tag"]), "info")

    @staticmethod
    def cal_aver_top(df):
        df["top_tag"] = df['model_tag_ratings'].max()
        size = len(df)
        if size:
            df["aver_model_tag_ratings"] = round(df['model_tag_ratings'].sum() / size, 2)
        else:
            df["aver_model_tag_ratings"] = 0
        return df


class CalModelAverAndTopMethod(CalAverAndTopMethod):
    """Calculate Average And Top Infomation Of Model"""
    def cal(self):
        origin = load("info")
        df = origin.drop_duplicates(["brand", "model"])
        top, aver = self.cal_aver_top(df)
        origin["top_model"], origin["aver_model_ratings"] = top, aver
        dump(origin, "info")

    @staticmethod
    def cal_aver_top(df):
        top = df['model_ratings'].max()
        size = len(df)
        if size:
            aver = round(df['model_ratings'].sum() / size, 2)
        else:
            aver = 0
        return top, aver
