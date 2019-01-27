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


class RankTargetByScoreMethod(RankMethod):
    """Rank Targets By Favorable Rate"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "tag", "target", "target_score"]]
        df = df.groupby(["target"]).apply(self.rank_func, "target_score", "model_target_rank")
        del df["target_score"]
        dump(pd.merge(origin, df, "left", on=["brand", "model", "tag", "target"]), "info")


class RankTagByScoreMethod(RankMethod):
    """Rank Tags By Favorable Rate"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "tag", "tag_score"]].drop_duplicates(["brand", "model", "tag"])
        df = df.groupby(["tag"]).apply(self.rank_func, "tag_score", "model_tag_rank")
        del df["tag_score"]
        dump(pd.merge(origin, df, "left", on=["brand", "model", "tag"]), "info")


class RankModelByScoreMethod(RankMethod):
    """Rank Models By Favorable Rate"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "model_score"]].drop_duplicates(["brand", "model"])
        df = self.rank_func(df, "model_score", "model_rank")
        del df["model_score"]
        dump(pd.merge(origin, df, "left", on=["brand", "model"]), "info")


class RankTargetByWilsonMethod(RankMethod):
    """Rank Models By Wilson Confidence Interval"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "tag", "target", "target_wilson"]]
        df = df.groupby(["target"]).apply(self.rank_func, "target_wilson", "model_target_rank")
        del df["target_wilson"]
        dump(pd.merge(origin, df, "left", on=["brand", "model", "tag", "target"]), "info")


class RankTagByWilsonMethod(RankMethod):
    """Rank Models By Wilson Confidence Interval"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "tag", "tag_wilson"]].drop_duplicates(["brand", "model", "tag"])
        df = df.groupby(["tag"]).apply(self.rank_func, "tag_wilson", "model_tag_rank")
        del df["tag_wilson"]
        dump(pd.merge(origin, df, "left", on=["brand", "model", "tag"]), "info")


class RankModelByWilsonMethod(RankMethod):
    """Rank Models By Wilson Confidence Interval"""
    def rank(self):
        origin = load("info")
        df = origin[["brand", "model", "model_wilson"]].drop_duplicates(["brand", "model"])
        df = self.rank_func(df, "model_wilson", "model_rank")
        del df["model_wilson"]
        dump(pd.merge(origin, df, "left", on=["brand", "model"]), "info")


class RankTargetByRatingMethod(RankMethod):
    """Rank Targets By Rating"""
    def rank(self):
        origin = load("info")


class RankTagByRatingMethod(RankMethod):
    """Rank Tags By Rating"""
    def rank(self):
        origin = load("info")


class RankModelByRatingMethod(RankMethod):
    """Rank Models By Rating"""
    def rank(self):
        origin = load("info")
