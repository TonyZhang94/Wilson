# -*- coding:utf-8 -*-

import pandas as pd

from Wilson.settings import Parameters
from Wilson.tools.utils import load, dump_pkl


class CalAspectMethod(object):
    """Calculate Aspect Method"""

    def __init__(self):
        """Init"""

    def cal(self):
        """Calculate Function"""
        raise NotImplementedError


class CalTargetBasicAspectMethod(CalAspectMethod):
    """Calculate Target Basic Aspect Info"""
    def cal(self):
        df = load("info")[["tag", "target", "target_score", "target_u", "target_v", "target_n"]]
        df = df.groupby(["tag", "target"]).apply(self.aspect_info)
        self.make_info(df)

    @staticmethod
    def aspect_info(df):
        df["target_min"] = df["target_score"].min()
        df["target_score_sum"] = df["target_score"].sum()

        u = df["target_u"].sum()
        df["target_u_sum"] = u
        df["target_v_sum"] = df["target_v"].sum()
        n = df["target_n"].sum()
        df["target_n_sum"] = n
        if n:
            df["target_p_sum"] = u / n
        else:
            df["target_p_sum"] = 0
        return df

    @staticmethod
    def make_info(df):
        del df["target_score"], df["target_u"], df["target_v"], df["target_n"]
        df = df.drop_duplicates(["tag", "target"]).sort_values('target_score_sum', ascending=False)
        info = dict()
        serial = {key: -1 for key in Parameters.tagList}
        prev = {key: -99999 for key in Parameters.tagList}
        for k, v in df.iterrows():
            key = "%s-%s" % (v["tag"], v["target"])
            if v["target_score_sum"] != prev[v["tag"]]:
                serial[v["tag"]] += 1
                prev[v["tag"]] = v["target_score_sum"]
            info[key] = {"serial": serial[v["tag"]], "min": v["target_min"], "score_sum": v["target_score_sum"],
                         "u": v["target_u_sum"], "v": v["target_v_sum"], "n": v["target_n_sum"],
                         "p": v["target_p_sum"]}
        dump_pkl(info, "targetBasicAspectInfo")
        dump_pkl(serial, "targetNumInfo")


class CalTagBasicAspectMethod(CalAspectMethod):
    """Calculate Tag Basic Aspect Info"""
    def cal(self):
        df = load("info")[["tag", "tag_score", "tag_u", "tag_v", "tag_n"]]
        df = df.groupby(['tag']).apply(self.aspect_info)
        self.make_info(df)

    @staticmethod
    def aspect_info(df):
        df["tag_min"] = df["tag_score"].min()
        df["tag_score_sum"] = df["tag_score"].sum()

        u = df["tag_u"].sum()
        df["tag_u_sum"] = u
        df["tag_v_sum"] = df["tag_v"].sum()
        n = df["tag_n"].sum()
        df["tag_n_sum"] = n
        if n:
            df["tag_p_sum"] = u / n
        else:
            df["tag_p_sum"] = 0
        return df

    @staticmethod
    def make_info(df):
        del df["tag_score"], df["tag_u"], df["tag_v"], df["tag_n"]
        df = df.drop_duplicates(["tag"]).sort_values('tag_score_sum', ascending=False)
        info = dict()
        serial = -1
        prev = -99999
        for k, v in df.iterrows():
            if v["tag_score_sum"] != prev:
                serial += 1
                prev = v["tag_score_sum"]
            info[v["tag"]] = (serial, v)
            info[v["tag"]] = {"serial": serial, "min": v["tag_min"], "score_sum": v["tag_score_sum"],
                              "u": v["tag_u_sum"], "v": v["tag_v_sum"], "n": v["tag_n_sum"],
                              "p": v["tag_p_sum"]}
        dump_pkl(info, "tagBasicAspectInfo")
        dump_pkl(serial, "tagNumInfo")


class CalModelBasicAspectMethod(CalAspectMethod):
    """Calculate Model Basic Aspect Info"""
    def cal(self):
        df = load("info")[["brand", "model", "model_score", "model_u", "model_v", "model_n"]]
        df = self.aspect_info(df)
        self.make_info(df)

    @staticmethod
    def aspect_info(df):
        df["model_min"] = df["model_score"].min()
        df["model_score_sum"] = df["model_score"].sum()

        u = df["model_u"].sum()
        df["model_u_sum"] = u
        df["model_v_sum"] = df["model_v"].sum()
        n = df["model_n"].sum()
        df["model_n_sum"] = n
        if n:
            df["model_p_sum"] = u / n
        else:
            df["model_p_sum"] = 0
        return df

    @staticmethod
    def make_info(df):
        df = df[: 1]
        info = {"min": df["model_min"].values[0], "score_sum": df["model_score_sum"].values[0],
                "u": df["model_u_sum"].values[0], "v": df["model_v_sum"].values[0],
                "n": df["model_n_sum"].values[0], "p": df["model_p_sum"].values[0]}
        dump_pkl(info, "modelBasicAspectInfo")


class CalTargetBasicPlusAspectMethod(CalAspectMethod):
    """Calculate Target Basic And Wilson Aspect Info"""
    def __init__(self):
        self.z = Parameters.zTargetAspect

    def cal(self):
        df = load("info")[["tag", "target", "target_score", "target_u", "target_v", "target_n"]]
        df = df.groupby(["tag", "target"]).apply(self.aspect_info)
        self.make_info(df)

    def aspect_info(self, df):
        df["target_min"] = df["target_score"].min()
        df["target_score_sum"] = df["target_score"].sum()

        u = df["target_u"].sum()
        df["target_u_sum"] = u
        df["target_v_sum"] = df["target_v"].sum()
        n = df["target_n"].sum()
        df["target_n_sum"] = n
        if n:
            p = u / n
        else:
            p = 0
        df["target_p_sum"] = p
        try:
            y = (p + self.z ** 2 / (2 * n) - self.z * (p * (1 - p) / n + self.z ** 2 / (4 * n ** 2)) ** 0.5) / \
                (1 + self.z ** 2 / n)
        except ZeroDivisionError:
            y = 0
        df["target_wilson_sum"] = y
        return df

    @staticmethod
    def make_info(df):
        del df["target_score"], df["target_u"], df["target_v"], df["target_n"]
        df = df.drop_duplicates(["tag", "target"]).sort_values('target_wilson_sum', ascending=False)
        info = dict()
        serial = {key: -1 for key in Parameters.tagList}
        prev = {key: -99999 for key in Parameters.tagList}
        for k, v in df.iterrows():
            key = "%s-%s" % (v["tag"], v["target"])
            if v["target_wilson_sum"] != prev[v["tag"]]:
                serial[v["tag"]] += 1
                prev[v["tag"]] = v["target_wilson_sum"]
            info[key] = {"serial": serial[v["tag"]], "min": v["target_min"], "score_sum": v["target_score_sum"],
                         "u": v["target_u_sum"], "v": v["target_v_sum"], "n": v["target_n_sum"],
                         "p": v["target_p_sum"], "wilson": v["target_wilson_sum"]}
        dump_pkl(info, "targetBasicAspectInfo")
        dump_pkl(serial, "targetNumInfo")


class CalTagBasicPlusAspectMethod(CalAspectMethod):
    """Calculate Tag Basic And Wilson Aspect Info"""
    def __init__(self):
        self.z = Parameters.zTagAspect

    def cal(self):
        df = load("info")[["tag", "tag_score", "tag_u", "tag_v", "tag_n"]]
        df = df.groupby(['tag']).apply(self.aspect_info)
        self.make_info(df)

    def aspect_info(self, df):
        df["tag_min"] = df["tag_score"].min()
        df["tag_score_sum"] = df["tag_score"].sum()

        u = df["tag_u"].sum()
        df["tag_u_sum"] = u
        df["tag_v_sum"] = df["tag_v"].sum()
        n = df["tag_n"].sum()
        df["tag_n_sum"] = n
        if n:
            p = u / n
        else:
            p = 0
        df["tag_p_sum"] = p
        try:
            y = (p + self.z ** 2 / (2 * n) - self.z * (p * (1 - p) / n + self.z ** 2 / (4 * n ** 2)) ** 0.5) / \
                (1 + self.z ** 2 / n)
        except ZeroDivisionError:
            y = 0
        df["tag_wilson_sum"] = y
        return df

    @staticmethod
    def make_info(df):
        del df["tag_score"], df["tag_u"], df["tag_v"], df["tag_n"]
        df = df.drop_duplicates(["tag"]).sort_values('tag_wilson_sum', ascending=False)
        info = dict()
        serial = -1
        prev = -99999
        for k, v in df.iterrows():
            if v["tag_wilson_sum"] != prev:
                serial += 1
                prev = v["tag_wilson_sum"]
            info[v["tag"]] = (serial, v)
            info[v["tag"]] = {"serial": serial, "min": v["tag_min"], "score_sum": v["tag_score_sum"],
                              "u": v["tag_u_sum"], "v": v["tag_v_sum"], "n": v["tag_n_sum"],
                              "p": v["tag_p_sum"], "wilson": v["tag_wilson_sum"]}
        dump_pkl(info, "tagBasicAspectInfo")
        dump_pkl(serial, "tagNumInfo")


class CalModelBasicPlusAspectMethod(CalAspectMethod):
    """Calculate Model Basic And Wilson Aspect Info"""
    def __init__(self):
        self.z = Parameters.zModelAspect

    def cal(self):
        df = load("info")[["brand", "model", "model_score", "model_u", "model_v", "model_n"]]
        df = self.aspect_info(df)
        self.make_info(df)

    def aspect_info(self, df):
        df["model_min"] = df["model_score"].min()
        df["model_score_sum"] = df["model_score"].sum()

        u = df["model_u"].sum()
        df["model_u_sum"] = u
        df["model_v_sum"] = df["model_v"].sum()
        n = df["model_n"].sum()
        df["model_n_sum"] = n
        if n:
            p = u / n
        else:
            p = 0
        df["model_p_sum"] = p
        try:
            y = (p + self.z ** 2 / (2 * n) - self.z * (p * (1 - p) / n + self.z ** 2 / (4 * n ** 2)) ** 0.5) / \
                (1 + self.z ** 2 / n)
        except ZeroDivisionError:
            y = 0
        df["tag_wilson_sum"] = y
        return df

    @staticmethod
    def make_info(df):
        df = df[: 1]
        info = {"min": df["model_min"].values[0], "score_sum": df["model_score_sum"].values[0],
                "u": df["model_u_sum"].values[0], "v": df["model_v_sum"].values[0],
                "n": df["model_n_sum"].values[0], "p": df["model_p_sum"].values[0],
                "wilson": df["tag_wilson_sum"].values[0]}
        dump_pkl(info, "modelBasicAspectInfo")
