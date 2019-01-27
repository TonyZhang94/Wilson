# -*- coding:utf-8 -*-

import pandas as pd
import json

from Wilson.tools.utils import load, dump


class TransToJsonMethod(object):
    """Transform To Json Method"""
    def __init__(self):
        """Init"""

    def trans(self):
        """Transform Function"""
        raise NotImplementedError


class TargetTransToTagMethod(TransToJsonMethod):
    """Transform Target Information To Tag"""
    def trans(self):
        df = load("info")
        df = df.groupby(["brand", "model", "tag"]).apply(self.trans_func)
        del df["target"]
        df = df.drop_duplicates(["brand", "model", "tag"])
        dump(df, "info")

    @staticmethod
    def trans_func(df):
        target_score, target_rating, target_rank, target_aver_rating, target_top_rating \
            = dict(), dict(), dict(), dict(), dict()
        for k, v in df.iterrows():
            target_score[v["target"]] = v["target_score"]
            target_rating[v["target"]] = v["model_target_ratings"]
            target_rank[v["target"]] = v["model_target_rank"]
            target_aver_rating[v["target"]] = v["aver_model_target_ratings"]
            target_top_rating[v["target"]] = v["top_target"]
        df["target_score"] = json.dumps(target_score, ensure_ascii=False)
        df["model_target_ratings"] = json.dumps(target_rating, ensure_ascii=False)
        df["model_target_rank"] = json.dumps(target_rank, ensure_ascii=False)
        df["aver_model_target_ratings"] = json.dumps(target_aver_rating, ensure_ascii=False)
        df["top_target"] = json.dumps(target_top_rating, ensure_ascii=False)
        return df


class TagTransToModelMethod(TransToJsonMethod):
    """Transform Tag Information To Model"""
    def trans(self):
        df = load("info")
        df = df.groupby(["brand", "model"]).apply(self.trans_func)
        del df["tag"]
        df = df.drop_duplicates(["brand", "model"])
        dump(df, "info")

    @staticmethod
    def trans_func(df):
        target_score, target_rating, target_rank, target_aver_rating, target_top_rating \
            = dict(), dict(), dict(), dict(), dict()
        tag_score, tag_rating, tag_rank, tag_aver_rating, tag_top_rating \
            = dict(), dict(), dict(), dict(), dict()
        for k, v in df.iterrows():
            target_score['\"%s\"' % v['tag']] = v['target_score']
            target_rating['\"%s\"' % v['tag']] = v['model_target_ratings']
            target_rank['\"%s\"' % v['tag']] = v['model_target_rank']
            target_aver_rating['\"%s\"' % v['tag']] = v['aver_model_target_ratings']
            target_top_rating['\"%s\"' % v['tag']] = v['top_target']

            tag_score[v['tag']] = float(v['tag_score'])
            tag_rating[v['tag']] = float(v['model_tag_ratings'])
            tag_rank[v['tag']] = v['model_tag_rank']
            tag_aver_rating[v['tag']] = float(v['aver_model_tag_ratings'])
            tag_top_rating[v['tag']] = v['top_tag']

        df['target_score'] = str(target_score)
        df['model_target_ratings'] = str(target_rating)
        df['model_target_rank'] = str(target_rank)
        df['aver_model_target_ratings'] = str(target_aver_rating)
        df['top_target'] = str(target_top_rating)

        df['tag_score'] = json.dumps(tag_score, ensure_ascii=False)
        df['model_tag_ratings'] = json.dumps(tag_rating, ensure_ascii=False)
        df['model_tag_rank'] = json.dumps(tag_rank, ensure_ascii=False)
        df['aver_model_tag_ratings'] = json.dumps(tag_aver_rating, ensure_ascii=False)
        df['top_tag'] = json.dumps(tag_top_rating, ensure_ascii=False)

        return df


class JsonReviseMethod(TransToJsonMethod):
    """Transform Some Symbols"""
    def trans(self):
        df = load("info")

        df['target_score'] = df['target_score'].str.replace('\'"', '"')
        df['target_score'] = df['target_score'].str.replace('"\'', '"')
        df['target_score'] = df['target_score'].str.replace('\'', '')
        df['target_score'] = df['target_score'].str.replace('\\', '')

        df['model_target_ratings'] = df['model_target_ratings'].str.replace('\'"', '"')
        df['model_target_ratings'] = df['model_target_ratings'].str.replace('"\'', '"')
        df['model_target_ratings'] = df['model_target_ratings'].str.replace('\'', '')
        df['model_target_ratings'] = df['model_target_ratings'].str.replace('\\', '')

        df['model_target_rank'] = df['model_target_rank'].str.replace('\'"', '"')
        df['model_target_rank'] = df['model_target_rank'].str.replace('"\'', '"')
        df['model_target_rank'] = df['model_target_rank'].str.replace('\'', '')
        df['model_target_rank'] = df['model_target_rank'].str.replace('\\', '')

        df['aver_model_target_ratings'] = df['aver_model_target_ratings'].str.replace('\'"', '"')
        df['aver_model_target_ratings'] = df['aver_model_target_ratings'].str.replace('"\'', '"')
        df['aver_model_target_ratings'] = df['aver_model_target_ratings'].str.replace('\'', '')
        df['aver_model_target_ratings'] = df['aver_model_target_ratings'].str.replace('\\', '')

        df['top_target'] = df['top_target'].str.replace('\'"', '"')
        df['top_target'] = df['top_target'].str.replace('"\'', '"')
        df['top_target'] = df['top_target'].str.replace('\'', '')
        df['top_target'] = df['top_target'].str.replace('\\', '')
