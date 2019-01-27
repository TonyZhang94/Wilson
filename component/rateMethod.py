# -*- coding:utf-8 -*-

import pandas as pd
import scipy.stats
import matplotlib.pyplot as plt

from Wilson.settings import Parameters, Mode
from Wilson.tools.utils import *


class RateMethod(object):
    """Rate Method"""
    def __init__(self):
        """Init"""

    def rate(self):
        """Rate Function"""
        raise NotImplementedError

    def show(self, x, y, title="", name="", xlabel="x", ylabel="y", sub_path="target"):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(x, y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        ax.set_title(title)
        plt.savefig(self.path.format(name=name))
        plt.close()


class RatingTargetIndependentMethod(RateMethod):
    """Rate Target Independently"""
    def __init__(self):
        self.mu, self.sigma = 0, 1

        self.zero_node = 1
        self.small_node = 10
        self.normal_node = 1000000

        self.info = None
        self.serial = None
        self.tag_serial = None

        self.max_blanks = dict()

        self.avg_base = 70
        self.avg_base_div = 0.025
        self.default_avg = 50
        self.default_target_sum = 0

        # normal
        # self.decay_base = 1
        # self.decay = 0
        self.decay_base = 0.85  # 可调
        self.decay = 0.07  # 可调

        pcid, cid = Entrance().params
        self.path = FileBase.showPath.format(pcid=pcid, cid=cid) + "TARGET_{name}.jpg"

    def rate(self):
        df = load("info")
        self.info = load_pkl("targetBasicAspectInfo")
        self.serial = load_pkl("targetNumInfo")
        self.tag_serial = load_pkl("tagBasicAspectInfo")
        df = df.groupby(["tag", "target"]).apply(self.rate_func)
        dump(df, "info")

    def rate_func(self, df):
        df, x, msg = self.rate_func_process(df)
        if Mode.showFlag:
            _x, _y = list(), list()
            ss = len([t for t in x if t == 100])
            if ss:
                print(df["tag"].values[0], df["target"].values[0])
                print("100 num", ss)
            for i in range(0, 101):
                cnt = len([t for t in x if i <= t < i + 1])
                if cnt != 0:
                    _x.append(i)
                    _y.append(cnt)
            self.show(x=_x, y=_y, title="target", name=msg, sub_path="target")
        return df

    def rate_func_process(self, df):
        tag, target = df["tag"].values[0], df["target"].values[0]
        side = self.serial[tag]
        info = self.info["%s-%s" % (tag, target)]
        serial_no, target_sum = info["serial"], info["score_sum"]
        try:
            avg = self.avg_base - serial_no / (side * self.avg_base_div)
        except ZeroDivisionError:
            if not side:
                avg = 50
            else:
                avg = self.avg_base

        base, mul, special = 5, 10, 15
        diff = len(df)
        if diff <= self.zero_node:
            if int(target_sum) < special:
                df["model_target_ratings"] = 0
            else:
                for k, v in df.iterrows():
                    score = ((v["target_score"] - special) / v["target_score"]) ** 2 / 0.02 + 46.66
                    df.at[k, "model_target_ratings"] = round(min(100, score), 2)
        elif self.zero_node < diff <= self.small_node:
            size = self.normal_node
            block = 1 / size
            try:
                max_blank = self.max_blanks[tag]
            except KeyError:
                max_blank = 100 - (
                            scipy.stats.norm.ppf(block * (size - size / (1 + side)), self.mu, self.sigma) + base) * mul
                # max_blank = max_blank
                # max_blank = max_blank * self.decay_base
                max_blank = max_blank * (self.decay_base - (self.tag_serial[tag]["serial"]) * self.decay)
                self.max_blanks[tag] = max_blank
            rectify = (0.04 * avg - 2) * max_blank

            dis, rank = round(100 / (diff + 5), 2), diff + 1
            for k, v in df.iterrows():
                rank -= 1
                df.at[k, "model_target_ratings"] = round(min(max(dis * rank + 0.1 * rectify, 0), 100), 2)
        elif self.small_node < diff:
            if diff < self.normal_node:
                size = self.normal_node
                step = size / (diff + 1)
            else:
                size = diff + 1
                step = 1
            block = 1 / size

            bottom = (scipy.stats.norm.ppf(block * 1 * step, self.mu, self.sigma) + base) * mul
            top = (scipy.stats.norm.ppf(block * diff * step, self.mu, self.sigma) + base) * mul
            blank = 100 - top

            if bottom < 0 or top > 100:
                print("adjust size =", diff)
                mul = 100 / (top - bottom)

            try:
                max_blank = self.max_blanks[tag]
            except KeyError:
                if not side:
                    side = 1
                max_blank = 100 - (
                            scipy.stats.norm.ppf(block * (size - size / (1 + side)), self.mu, self.sigma) + base) * mul
                # max_blank = max_blank
                # max_blank = max_blank * self.decay_base
                max_blank = max_blank * (self.decay_base - (self.tag_serial[tag]["serial"]) * self.decay)
                self.max_blanks[tag] = max_blank
            rectify = (0.04 * avg - 2) * max_blank

            rank = diff + 1
            for k, v in df.iterrows():
                rank -= 1

                co = rank / diff
                share = 0.01 * avg - 0.5
                if share > 0:
                    offset = -((2 - 2 * co) ** 2) * share * blank
                elif share < 0:
                    offset = -((2 * co) ** 2) * share * blank
                else:
                    offset = 0
                fx = rank * step * block
                ppf = scipy.stats.norm.ppf(fx, self.mu, self.sigma)
                ppf = round((ppf + base) * mul + offset, 2)
                df.at[k, "model_target_ratings"] = round(min(max(ppf + rectify, 0), 100), 2)
        else:
            print("error condition")

        if not Mode.showFlag:
            return df, None, None

        x = df["model_target_ratings"].values
        over_len = len([t for t in x if not 0 <= t <= 100])
        if over_len > 0:
            print("over len", over_len)
            print([t for t in x if not 0 <= t <= 100])
            x = [min(max(t, 0), 100) for t in x]

        msg = "tag {} pos {} {} size {} max {} min {} avg {} sigma={} sum {}".\
            format(tag, round(avg, 2), target, diff, round(max(x), 2), round(min(x), 2),
                   round(sum(x) / len(x), 2), self.sigma, target_sum)
        return df, x, msg


class RatingTagIndependentMethod(RateMethod):
    """Rate Tag Independently"""
    def __init__(self):
        self.mu, self.sigma = 0, 1

        self.zero_node = 1
        self.small_node = 10
        self.normal_node = 1000000

        self.info = None
        self.serial = None

        self.max_blanks = dict()

        self.avg_base = 55
        self.avg_base_div = 0.1
        self.default_avg = 50
        self.default_tag_sum = 0

        pcid, cid = Entrance().params
        self.path = FileBase.showPath.format(pcid=pcid, cid=cid) + "TAG_{name}.jpg"

    def rate(self):
        origin = load("info")
        self.info = load_pkl("tagBasicAspectInfo")
        self.serial = load_pkl("tagNumInfo")
        df = origin[["brand", "model", "tag", "tag_score"]].drop_duplicates(["brand", "model", "tag"])
        df = df.groupby(["tag"]).apply(self.rate_func)
        del df["tag_score"]
        dump(pd.merge(origin, df, "left", on=["brand", "model", "tag"]), "info")

    def rate_func(self, df):
        df, x, msg = self.rate_func_process(df)
        if Mode.showFlag:
            _x, _y = list(), list()
            for i in range(0, 100):
                cnt = len([t for t in x if i <= t < i + 1])
                if cnt != 0:
                    _x.append(i)
                    _y.append(cnt)
            self.show(x=_x, y=_y, title="tag", name=msg, sub_path="tag")
        return df

    def rate_func_process(self, df):
        tag = df["tag"].values[0]
        side = self.serial
        info = self.info[tag]
        serial_no, tag_sum = info["serial"], info["score_sum"]
        try:
            avg = self.avg_base - serial_no / (side * self.avg_base_div)
        except ZeroDivisionError:
            avg = self.avg_base

        base, mul, special = 5, 10, 200

        diff = len(df)
        if diff <= self.zero_node:
            if int(tag_sum) < special:
                df["model_tag_ratings"] = 0
            else:
                for k, v in df.iterrows():
                    score = ((v["tag_score"] - special) / v["tag_score"]) ** 2 / 0.02 + 46.66
                    df.at[k, "model_tag_ratings"] = round(min(100, score), 2)
        elif self.zero_node < diff <= self.small_node:
            size = diff + 1
            block = 1 / size
            try:
                max_blank = self.max_blanks[tag]
            except KeyError:
                max_blank = 100 - (
                        scipy.stats.norm.ppf(block * (size - size / (1 + side)), self.mu, self.sigma) + base) * mul
                self.max_blanks[tag] = max_blank
            rectify = (0.04 * avg - 2) * max_blank

            dis, rank = round(100 / (diff + 5), 2), diff + 1
            for k, v in df.iterrows():
                rank -= 1
                df.at[k, "model_tag_ratings"] = round(min(max(dis * rank + 0.1 * rectify, 0), 100), 2)
        elif self.small_node < diff:
            if diff < self.normal_node:
                size = self.normal_node
                step = size / (diff + 1)
            else:
                size = diff + 1
                step = 1
            block = 1 / size

            bottom = (scipy.stats.norm.ppf(block * 1 * step, self.mu, self.sigma) + base) * mul
            top = (scipy.stats.norm.ppf(block * diff * step, self.mu, self.sigma) + base) * mul
            blank = 100 - top

            if bottom < 0 or top > 100:
                print("adjust size =", diff)
                mul = 100 / (top - bottom)

            try:
                max_blank = self.max_blanks[tag]
            except KeyError:
                max_blank = 100 - (
                        scipy.stats.norm.ppf(block * (size - size / (1 + side)), self.mu, self.sigma) + base) * mul
                self.max_blanks[tag] = max_blank
            rectify = (0.04 * avg - 2) * max_blank

            rank = diff + 1
            for k, v in df.iterrows():
                rank -= 1

                co = rank / diff
                share = 0.01 * avg - 0.5
                if share > 0:
                    offset = -((2 - 2 * co) ** 2) * share * blank
                elif share < 0:
                    offset = -((2 * co) ** 2) * share * blank
                else:
                    offset = 0
                fx = rank * step * block
                ppf = scipy.stats.norm.ppf(fx, self.mu, self.sigma)
                ppf = round((ppf + base) * mul + offset, 2)
                df.at[k, "model_tag_ratings"] = round(min(max(ppf + rectify, 0), 100), 2)
        else:
            print("error condition")

        if not Mode.showFlag:
            return df, None, None

        x = df["model_tag_ratings"].values
        over_len = len([t for t in x if not 0 <= t <= 100])
        if over_len > 0:
            print("over len", over_len)
            print([t for t in x if not 0 <= t <= 100])
            x = [min(max(t, 0), 100) for t in x]
        msg = "tag {} pos {} size {} max {} min {} avg {} sigma={} sum {}". \
            format(tag, round(avg, 2), diff, round(max(x), 2), round(min(x), 2),
                   round(sum(x) / len(x), 2), self.sigma, tag_sum)
        return df, x, msg


class RatingModelIndependentMethod(RateMethod):
    """Rate Model Independently"""
    def __init__(self):
        self.mu, self.sigma = 0, 1

        self.zero_node = 1
        self.small_node = 10
        self.normal_node = 1000000

        self.info = None

        pcid, cid = Entrance().params
        self.path = FileBase.showPath.format(pcid=pcid, cid=cid) + "Model_{name}.jpg"

    def rate(self):
        origin = load("info")
        self.info = load_pkl("modelBasicAspectInfo")
        df = origin[["brand", "model", "model_score"]].drop_duplicates(["brand", "model"])
        df = self.rate_func(df)
        del df["model_score"]
        dump(pd.merge(origin, df, "left", on=["brand", "model"]), "info")

    def rate_func(self, df):
        df, x, msg = self.rate_func_process(df)
        if Mode.showFlag:
            _x, _y = list(), list()
            for i in range(0, 100):
                cnt = len([t for t in x if i <= t < i + 1])
                if cnt != 0:
                    _x.append(i)
                    _y.append(cnt)
            self.show(x=_x, y=_y, title="tag", name=msg, sub_path="tag")
        return df

    def rate_func_process(self, df):
        base, mul = 5, 10
        diff = len(df)
        if diff < self.normal_node:
            size = self.normal_node
            step = size / (diff + 1)
        else:
            size = diff + 1
            step = 1
        block = 1 / size

        bottom = (scipy.stats.norm.ppf(block * 1 * step, self.mu, self.sigma) + base) * mul
        top = (scipy.stats.norm.ppf(block * diff * step, self.mu, self.sigma) + base) * mul

        if bottom < 0 or top > 100:
            print("adjust size =", diff)
            mul = 100 / (top - bottom)

        if diff <= self.small_node:
            dis, rank = round(100 / (diff + 5), 2), diff + 1
            for k, v in df.iterrows():
                rank -= 1
                df.at[k, "model_ratings"] = round(min(max(dis * rank, 0), 100), 2)
        elif self.small_node < diff:
            rank = diff + 1
            for k, v in df.iterrows():
                rank -= 1
                fx = rank * step * block
                ppf = scipy.stats.norm.ppf(fx, self.mu, self.sigma)
                ppf = round((ppf + base) * mul, 2)
                df.at[k, "model_ratings"] = round(min(max(ppf, 0), 100), 2)
        else:
            print("error condition")

        if not Mode.showFlag:
            return df, None, None

        x = df["model_ratings"].values
        over_len = len([t for t in x if not 0 <= t <= 100])
        if over_len > 0:
            print("over len", over_len)
            print([t for t in x if not 0 <= t <= 100])
            x = [min(max(t, 0), 100) for t in x]
        msg = "size {} max {} min {} avg {} sigma={} sum {}".\
            format(diff, round(max(x), 2), round(min(x), 2),
                   round(sum(x) / len(x), 2), self.sigma, self.info["score_sum"])
        return df, x, msg
