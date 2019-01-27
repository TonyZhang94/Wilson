# -*- coding:utf-8 -*-

import pandas as pd

from Wilson.tools.utils import load, dump


class SelectMethod(object):
    """Select Method"""
    def __init__(self):
        """Init"""

    def select(self):
        """Select Function"""
        raise NotImplementedError


class SelectUsefulColumnsMethod(SelectMethod):
    """Select Useful Columns To Save"""
    def select(self):
        df = load("info")
        dump(df, "wholeInfo")
        df = df[["brand", "model", "tag", "target",
                 "model_score", "tag_score", "target_score",
                 "model_ratings", "model_tag_ratings", "model_target_ratings",
                 "model_rank", "model_tag_rank", "model_target_rank",
                 "aver_model_ratings", "aver_model_tag_ratings", "aver_model_target_ratings",
                 "top_model", "top_tag", "top_target"]]
        dump(df, "info")
