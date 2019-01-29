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
        df = df.sort_values(["target_wilson"], ascending=False)
        df = df.groupby(["tag", "target"]).apply(self.rate_func)
        dump(df, "info")

    def rate_func(self, df):
        df, x, msg = self.rate_func_process(df)
        if Mode.showFlag:
            _x, _y = list(), list()
            # ss = len([t for t in x if t == 100])
            # if ss:
            #     print(df["tag"].values[0], df["target"].values[0])
            #     print("100 num", ss)
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
        df = df.sort_values(["tag_wilson"], ascending=False)
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
        df = df.sort_values(["model_wilson"], ascending=False)
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


class RatingTagByTargetMethod(RateMethod):
    """Rate Tag By Target Rating"""
    def __init__(self):
        self.threshold_share = 0.6
        self.threshold_base = 5

        pcid, cid = Entrance().params
        self.path = FileBase.showPath.format(pcid=pcid, cid=cid) + "TAG_{name}.jpg"

    def rate(self):
        df = load("info")
        df = df.sort_values(["model_target_ratings"], ascending=False)
        df = df.groupby(["brand", "model", "tag"]).apply(self.rate_func)
        self.show_func(df)
        dump(df, "info")

    def rate_func(self, df):
        target_min = min(min(df["target_score"].values), 0)
        total = 0
        add = {k: 0 for k in Parameters.tagList}
        cnt = {k: 0 for k in Parameters.tagList}
        threshold = max(len([x for x in df["model_target_ratings"].values if x > 0]) *
                        self.threshold_share, self.threshold_base)
        for k, v in df.iterrows():
            if 0 != v["model_target_ratings"]:
                if cnt[v["tag"]] >= threshold:
                    continue
                total = total + v["target_score"] - target_min
                add[v["tag"]] += (v["target_score"] - target_min) * v["model_target_ratings"]
                cnt[v["tag"]] += 1
        for tag in Parameters.tagList:
            pos = df["tag"] == tag
            if total != 0 and add[tag] / total > 100:
                print(df)
                print(tag, total, add[tag], target_min, cnt[tag])
            if 0 != total:
                df.loc[pos, "model_tag_ratings"] = max(round(add[tag] / total, 2), 0)
            else:
                df.loc[pos, "model_tag_ratings"] = total

        return df

    def show_func(self, df):
        if not Mode.showFlag:
            return

        temp = df.drop_duplicates(["brand", "model", "tag"])
        for tag in Parameters.tagList:
            x = temp[temp["tag"] == tag]["model_tag_ratings"].values
            over_len = len([t for t in x if not 0 <= t <= 100])
            if over_len > 0:
                print("over len", over_len)
                print([t for t in x if not 0 <= t <= 100])
                x = [min(max(t, 0), 100) for t in x]
            msg = "tag {} size {} max {} min {} avg {}". \
                format(tag, len(x), round(max(x), 2), round(min(x), 2),
                       round(sum(x) / len(x), 2))
            _x, _y = list(), list()
            for i in range(0, 100):
                cnt = len([t for t in x if i <= t < i + 1])
                if cnt != 0:
                    _x.append(i)
                    _y.append(cnt)
            self.show(x=_x, y=_y, title="tag", name=msg, sub_path="tag")


class RatingModelByTagMethod(RateMethod):
    """Rate Model By Tag Rating"""
    def __init__(self):
        pcid, cid = Entrance().params
        self.path = FileBase.showPath.format(pcid=pcid, cid=cid) + "MODEL_{name}.jpg"

    def rate(self):
        origin = load("info")
        df = origin.drop_duplicates(["brand", "model", "tag"])
        df = df.sort_values(["model_tag_ratings"], ascending=False)
        df = df.groupby(["brand", "model"]).apply(self.rate_func)
        df = df.drop_duplicates(["brand", "model"])[["brand", "model", "model_ratings"]]
        self.show_func(df)
        dump(pd.merge(origin, df, "left", on=["brand", "model"]), "info")

    @staticmethod
    def rate_func(df):
        tag_min = min(min(df["tag_score"].values), 0)
        total, score = 0, 0
        for k, v in df.iterrows():
            if 0 != v["model_tag_ratings"]:
                total = total + v["tag_score"] - tag_min
                score += (v["tag_score"] - tag_min) * v["model_tag_ratings"]
        if total != 0:
            df["model_ratings"] = max(round(score / total, 2), 0)
        else:
            df["model_ratings"] = total
        return df

    def show_func(self, df):
        if not Mode.showFlag:
            return

        x = df["model_ratings"].values
        over_len = len([t for t in x if not 0 <= t <= 100])
        if over_len > 0:
            print("over len", over_len)
            print([t for t in x if not 0 <= t <= 100])
            x = [min(max(t, 0), 100) for t in x]
        msg = "size {} max {} min {} avg {}". \
            format(len(x), round(max(x), 2), round(min(x), 2),
                   round(sum(x) / len(x), 2))
        _x, _y = list(), list()
        for i in range(0, 100):
            cnt = len([t for t in x if i <= t < i + 1])
            if cnt != 0:
                _x.append(i)
                _y.append(cnt)
        self.show(x=_x, y=_y, title="tag", name=msg, sub_path="model")


class RatingTagByTargetByWilsonMethod(RateMethod):
    """Rate Tag By Target Rating And Target Aspect Wilson"""

    def __init__(self):
        self.threshold_share = 1
        self.threshold_base = 0

        # 可调，tag缺失某个target的情况加惩罚
        self.co = 0.02

        self.info = None
        self.info_num = None

        pcid, cid = Entrance().params
        self.path = FileBase.showPath.format(pcid=pcid, cid=cid) + "TAG_{name}.jpg"

    def rate(self):
        df = load("info")
        self.info = load_pkl("targetBasicAspectInfo")
        self.info_num = load_pkl("targetNumInfo")
        df = df.sort_values(["model_target_ratings"], ascending=False)
        df = df.groupby(["brand", "model", "tag"]).apply(self.rate_func)
        self.show_func(df)
        dump(df, "info")

    def rate_func(self, df):
        total, tag = 0, df["tag"].values[0]
        add = {k: 0 for k in Parameters.tagList}
        cnt = {k: 0 for k in Parameters.tagList}
        threshold = max(len([x for x in df["model_target_ratings"].values if x > 0]) *
                        self.threshold_share, self.threshold_base)
        for k, v in df.iterrows():
            if 0 != v["model_target_ratings"]:
                if cnt[v["tag"]] >= threshold:
                    continue
                total = total + self.info["%s-%s" % (v["tag"], v["target"])]["wilson"]
                add[v["tag"]] += self.info["%s-%s" % (v["tag"], v["target"])]["wilson"] * v["model_target_ratings"]
                cnt[v["tag"]] += 1
        total += self.co * (self.info_num[tag]+1 - cnt[tag])
        for tag in Parameters.tagList:
            pos = df["tag"] == tag
            if total != 0 and add[tag] / total > 100:
                print(df)
                print(tag, total, add[tag], cnt[tag])
            if 0 != total:
                df.loc[pos, "model_tag_ratings"] = max(round(add[tag] / total, 2), 0)
            else:
                df.loc[pos, "model_tag_ratings"] = total

        return df

    def show_func(self, df):
        if not Mode.showFlag:
            return

        temp = df.drop_duplicates(["brand", "model", "tag"])
        for tag in Parameters.tagList:
            x = temp[temp["tag"] == tag]["model_tag_ratings"].values
            over_len = len([t for t in x if not 0 <= t <= 100])
            if over_len > 0:
                print("over len", over_len)
                print([t for t in x if not 0 <= t <= 100])
                x = [min(max(t, 0), 100) for t in x]
            msg = "tag {} size {} max {} min {} avg {}". \
                format(tag, len(x), round(max(x), 2), round(min(x), 2),
                       round(sum(x) / len(x), 2))
            _x, _y = list(), list()
            for i in range(0, 100):
                cnt = len([t for t in x if i <= t < i + 1])
                if cnt != 0:
                    _x.append(i)
                    _y.append(cnt)
            self.show(x=_x, y=_y, title="tag", name=msg, sub_path="tag")


class RatingModelByTagByWilsonMethod(RateMethod):
    """Rate Model By Tag Rating And Tag Aspect Wilson"""
    def __init__(self):
        # 可调，model缺失某个tag的情况加惩罚
        self.co = 1.2

        self.info = None

        pcid, cid = Entrance().params
        self.path = FileBase.showPath.format(pcid=pcid, cid=cid) + "MODEL_{name}.jpg"

    def rate(self):
        origin = load("info")
        self.info = load_pkl("tagBasicAspectInfo")
        df = origin.drop_duplicates(["brand", "model", "tag"])
        df = df.sort_values(["model_tag_ratings"], ascending=False)
        df = df.groupby(["brand", "model"]).apply(self.rate_func)
        df = df.drop_duplicates(["brand", "model"])[["brand", "model", "model_ratings"]]
        self.show_func(df)
        dump(pd.merge(origin, df, "left", on=["brand", "model"]), "info")

    def rate_func(self, df):
        total, score = 0, 0
        tags = set(Parameters.tagList)
        for k, v in df.iterrows():
            if 0 != v["model_tag_ratings"]:
                total += self.info[v["tag"]]["wilson"]
                try:
                    tags.remove(v["tag"])
                except KeyError:
                    pass
                score += self.info[v["tag"]]["wilson"] * v["model_tag_ratings"]
        for tag in tags:
            total += self.info[tag]["wilson"] * self.co
        if total != 0:
            df["model_ratings"] = max(round(score / total, 2), 0)
        else:
            df["model_ratings"] = total
        return df

    def show_func(self, df):
        if not Mode.showFlag:
            return

        x = df["model_ratings"].values
        over_len = len([t for t in x if not 0 <= t <= 100])
        if over_len > 0:
            print("over len", over_len)
            print([t for t in x if not 0 <= t <= 100])
            x = [min(max(t, 0), 100) for t in x]
        msg = "size {} max {} min {} avg {}". \
            format(len(x), round(max(x), 2), round(min(x), 2),
                   round(sum(x) / len(x), 2))
        _x, _y = list(), list()
        for i in range(0, 100):
            cnt = len([t for t in x if i <= t < i + 1])
            if cnt != 0:
                _x.append(i)
                _y.append(cnt)
        self.show(x=_x, y=_y, title="tag", name=msg, sub_path="model")
