# -*- coding:utf-8 -*-

from Wilson.tools.public import Entrance
from Wilson.strategy.noRelationStrategy import NoRelationStrategy


class Manager(object):
    def __init__(self, pcid, cid):
        Entrance(pcid=pcid, cid=cid)

    def run(self):
        strategy = NoRelationStrategy()
        strategy().execute()


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

    obj = Manager(pcid=pcid, cid=cid)
    obj.run()
