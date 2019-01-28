# -*- coding:utf-8 -*-

from Wilson.tools.public import Entrance
from Wilson.strategy.noRelationStrategy import NoRelationStrategy
from Wilson.strategy.noRelationWithWilsonAspectStrategy import NoRelationWithWilsonAspectStrategy
from Wilson.strategy.relationStrategy import RelationStrategy
from Wilson.strategy.relationWithWilsonAspectStrategy import RelationWithWilsonAspectStrategy
# from Wilson.strategy.relationByWilsonStrategy import RelationByWilsonStrategy
# from Wilson.strategy.relationByWilsonWithWilsonAspectStrategy import RelationByWilsonWithWilsonAspectStrategy


class Manager(object):
    def __init__(self, pcid, cid):
        Entrance(pcid=pcid, cid=cid)

    def run(self):
        """
        WithWilson 区别在于basic和basicPlus（serial的区别）
        Relation 的区别在于Tag和Model打分是否独立（以及Tag和Model排序和打分的先后关系）
        RelationByWilson 的区别在于 Target和Tag，Tag和Model的关系

        推荐：
        2. NoRelationWithWilsonAspectStrategy() 缺点：总分数可能超过部件分数区间
        4. RelationWithWilsonAspectStrategy() 缺点：计算总分方式有些简单

        其次：
        6. RelationByWilsonWithWilsonAspectStrategy() 理想状态下是最好的，但是还有待评定也没有写
        """
        # strategy = NoRelationStrategy()
        # strategy = NoRelationWithWilsonAspectStrategy()
        # strategy = RelationStrategy()
        strategy = RelationWithWilsonAspectStrategy()
        # strategy = RelationByWilsonStrategy()
        # strategy = RelationByWilsonWithWilsonAspectStrategy()
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
    # pcid = "4"
    # cid = "50012097"

    obj = Manager(pcid=pcid, cid=cid)
    obj.run()
