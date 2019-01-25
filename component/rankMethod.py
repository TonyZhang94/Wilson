# -*- coding:utf-8 -*-

import pandas as pd

from Wilson.tools.utils import load, dump


class RankMethod(object):
    """Rank Method"""
    def __init__(self):
        """Init"""

    def rank(self):
        """Rank Function"""
        raise NotImplementedError

    @staticmethod
    def rank_func(df, src, dst):
        df = df.sort_values(src, ascending=False)
        prev, rank = 0, 0
        for k, v in df.iterrows():
            if prev != v[src]:
                rank += 1
                prev = v[src]
            df.at[k, dst] = rank
        return df


class RankTargetByPMethod(RankMethod):
    """Rank Targets By Favorable Rate"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "tag", "target", "target_p"]]
        df = df.groupby(["target"]).apply(self.rank_func, "target_p", "target_p_rank")
        del df["target_p"]
        dump(pd.merge(origin, df, "left", on=["brand", "model", "tag", "target"]), "info")


class RankTagByPMethod(RankMethod):
    """Rank Tags By Favorable Rate"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "tag", "tag_p"]].drop_duplicates(["brand", "model", "tag"])
        df = df.groupby(["tag"]).apply(self.rank_func, "tag_p", "tag_p_rank")
        del df["tag_p"]
        dump(pd.merge(origin, df, "left", on=["brand", "model", "tag"]), "info")


class RankModelByPMethod(RankMethod):
    """Rank Models By Favorable Rate"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "model_p"]].drop_duplicates(["brand", "model"])
        df = self.rank_func(df, "model_p", "model_p_rank")
        del df["model_p"]
        dump(pd.merge(origin, df, "left", on=["brand", "model"]), "info")


class RankTargetByWilsonMethod(RankMethod):
    """Rank Models By Wilson Confidence Interval"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "tag", "target", "target_wilson"]]
        df = df.groupby(["target"]).apply(self.rank_func, "target_wilson", "target_wilson_rank")
        del df["target_wilson"]
        dump(pd.merge(origin, df, "left", on=["brand", "model", "tag", "target"]), "info")


class RankTagByWilsonMethod(RankMethod):
    """Rank Models By Wilson Confidence Interval"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "tag", "tag_wilson"]].drop_duplicates(["brand", "model", "tag"])
        df = df.groupby(["tag"]).apply(self.rank_func, "tag_wilson", "tag_wilson_rank")
        del df["tag_wilson"]
        dump(pd.merge(origin, df, "left", on=["brand", "model", "tag"]), "info")


class RankModelByWilsonMethod(RankMethod):
    """Rank Models By Wilson Confidence Interval"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "model_wilson"]].drop_duplicates(["brand", "model"])
        df = self.rank_func(df, "model_wilson", "model_wilson_rank")
        del df["model_wilson"]
        dump(pd.merge(origin, df, "left", on=["brand", "model"]), "info")
