# -*- coding:utf-8 -*-

import pandas as pd

from Wilson.tools.utils import load, dump


class CalBaseLineMethod(object):
    """Calculate Baseline Method"""
    def __init__(self):
        """Init"""

    def cal(self):
        """Calculate Function"""
        raise NotImplementedError


class CalTargetBaseLineMethod(CalBaseLineMethod):
    """Calculate Target Baseline Info"""
    def cal(self):
        df = load("info")
        for inx, row in df.iterrows():
            if 1 == row["grade"]:
                df.at[inx, "u"] = row["frequency"]
                df.at[inx, "v"] = 0
            elif -1 == row["grade"]:
                df.at[inx, "u"] = 0
                df.at[inx, "v"] = row["frequency"]
        del df["frequency"], df["grade"]

        df = df.groupby(["brand", "model", "tag", "target"]).apply(
            self.cal_baseline)
        del df["u"], df["v"]
        df = df.drop_duplicates(["brand", "model", "tag", "target"])
        dump(df, "info")

    @staticmethod
    def cal_baseline(df):
        u, v = df["u"].sum(), df["v"].sum()
        n = u + v
        if n:
            p = u / n
        else:
            p = 0
        df["target_u"], df["target_v"], df["target_n"], df["target_p"] = u, v, n, p
        df["target_score"] = u - v
        return df


class CalTagBaseLineMethod(CalBaseLineMethod):
    """Calculate Tag Baseline Info"""
    def cal(self):
        df = load("info")
        df = df.groupby(["brand", "model", "tag"]).apply(
            self.cal_baseline)
        dump(df, "info")

    @staticmethod
    def cal_baseline(df):
        u, v = df["target_u"].sum(), df["target_v"].sum()
        n = u + v
        if n:
            p = u / n
        else:
            p = 0
        df["tag_u"], df["tag_v"], df["tag_n"], df["tag_p"] = u, v, n, p
        df["tag_score"] = u - v
        return df


class CalModelBaseLineMethod(CalBaseLineMethod):
    """Calculate Model Baseline Info"""
    def cal(self):
        origin = load("info")
        df = origin.drop_duplicates(["brand", "model", "tag"])[
            ["brand", "model", "tag_u", "tag_v"]]
        df = df.groupby(["brand", "model"]).apply(
            self.cal_baseline)
        del df["tag_u"], df["tag_v"]
        df = df.drop_duplicates(["brand", "model"])
        dump(pd.merge(origin, df, "left", on=["brand", "model"]), "info")

    @staticmethod
    def cal_baseline(df):
        u, v = df["tag_u"].sum(), df["tag_v"].sum()
        n = u + v
        if n:
            p = u / n
        else:
            p = 0
        df["model_u"], df["model_v"], df["model_n"], df["model_p"] = u, v, n, p
        df["model_score"] = u - v
        return df
