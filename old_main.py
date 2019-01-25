# -*- coding:utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from Wilson.component.readData import *
from Wilson.tools.public import Entrance
from Wilson.tools.utils import *
from Wilson.graph import *


z = 5


class Manager(object):
    def __init__(self, pcid, cid, datamonth, cidname):
        Entrance(pcid=pcid, cid=cid, datamonth=datamonth, cidname=cidname)

    @staticmethod
    def get_target_data():
        pcid, cid, _ = Entrance().params
        try:
            df = pd.read_csv(FileBase.info.format(pcid=pcid, cid=cid, name="uvp_target"), index_col=0)
        except FileNotFoundError:
            df = get_review_info()
            df = df.groupby(["brand", "model", "tag", "target"]).apply(
                cal_abs_freq).drop_duplicates(["brand", "model", "tag", "target"])
            del df["grade"], df["frequency"]
            df.to_csv(FileBase.info.format(pcid=pcid, cid=cid, name="uvp_target"))
        return df

    @staticmethod
    def get_tag_data():
        pcid, cid, _ = Entrance().params
        try:
            df = pd.read_csv(FileBase.info.format(pcid=pcid, cid=cid, name="uvp_tag"), index_col=0)
        except FileNotFoundError:
            df = get_review_info()
            df = df.groupby(["brand", "model", "tag"]).apply(
                cal_abs_freq).drop_duplicates(["brand", "model", "tag"])
            del df["grade"], df["frequency"], df["target"]
            df.to_csv(FileBase.info.format(pcid=pcid, cid=cid, name="uvp_tag"))
        return df

    @staticmethod
    def get_model_data():
        pcid, cid, _ = Entrance().params
        try:
            df = pd.read_csv(FileBase.info.format(pcid=pcid, cid=cid, name="uvp_model"), index_col=0)
        except FileNotFoundError:
            df = get_review_info()
            df = df.groupby(["brand", "model"]).apply(
                cal_abs_freq).drop_duplicates(["brand", "model"])
            del df["grade"], df["frequency"], df["target"], df["tag"]
            df.to_csv(FileBase.info.format(pcid=pcid, cid=cid, name="uvp_model"))
        return df

    def cmp_target(self):
        df = self.get_target_data()
        for k, v in df.iterrows():
            df.at[k, "score"] = score(v["n"], v["p"], z=z)
        df = df.groupby(["target"]).apply(rank_func).sort_values(["target", "ScoreRank"], ascending=True)
        df.to_csv("result/target.csv", encoding="utf_8_sig")

    def cmp_tag(self):
        df = self.get_tag_data()
        for k, v in df.iterrows():
            df.at[k, "score"] = score(v["n"], v["p"], z=z)
        df = df.groupby(["tag"]).apply(rank_func).sort_values(["tag", "ScoreRank"], ascending=True)
        df.to_csv("result/tag.csv", encoding="utf_8_sig")

    def cmp_model(self):
        df = self.get_model_data()
        for k, v in df.iterrows():
            df.at[k, "score"] = score(v["n"], v["p"], z=z)
        df = rank_func(df)
        df.to_csv("result/model.csv", encoding="utf_8_sig")

    @ignore_warning
    def run(self):
        self.cmp_target()
        self.cmp_tag()
        self.cmp_model()
        # paint(1000, 1000)


if __name__ == '__main__':
    # tasks.append([9, 50012323])  # 羽毛球拍
    # tasks.append([0, 124086006])  # wifi设备
    # tasks.append([2, 50008882])  # 内裤
    # tasks.append([3, 50012677])  # 办公用品
    # tasks.append([4, 50012097])  # 料理机
    # tasks.append([4, 50005002])  # 美容仪
    # tasks.append([5, 50010796])  # 眼影
    # tasks.append([6, 50006077])  # 儿童车
    # tasks.append([7, 50020632])  # 布艺沙发 X
    # tasks.append([8, 123040002])  # 毛巾
    # tasks.append([13, 261706])  # 车载设备
    # tasks.append([100, 2018071815])  # 儿童车

    pcid = "100"
    cid = "2018101516"
    _ = "201810"
    _ = "料理机"

    start = time.time()
    obj = Manager(pcid=pcid, cid=cid, datamonth=_, cidname=_)
    obj.run()
    end = time.time()
    print("cost %0.2fs" % (end - start))
