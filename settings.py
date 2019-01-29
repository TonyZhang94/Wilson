# -*- coding:utf-8 -*-

from DBparam import *
from Wilson.tools.myExceptions import *

# class Outer99(object):
#     host = $ip$
#     port = $port$
#     user = $username$
#     password = $password$
#
#     DB = dict()
#     DB["standard_library"] = "standard_library"
#     DB["fact_library"] = "fact_library"
#     DB["zhuican_web"] = "zhuican_web"
#     DB["raw_mj_category"] = "raw_mj_category"
#     DB["report_dg"] = "report_dg"
#     DB["raw_tb_comment_notag"] = "raw_tb_comment_notag"


# DBDefault = Outer99
DBDefault = DB99


class Mode(object):
    """For Test"""
    srcLOCAL = True
    useDate = False
    showFlag = True
    clearLOCAL = False

    """For Use"""
    # srcLOCAL = True
    # useDate = True
    # showFlag = False
    # clearLOCAL = True

    def __new__(cls, *args, **kwargs):
        raise InstantiationError


class Parameters(object):
    tagList = ["质量", "款式", "功能", "服务"]

    """可调"""
    zTarget = 10
    zTag = 10
    zModel = 10

    """可调"""
    zTargetAspect = 1.96
    zTagAspect = 1.96
    zModelAspect = 1.96

    def __new__(cls, *args, **kwargs):
        raise InstantiationError


class FileBase(object):
    info = "data/info_{name}_pcid{pcid}cid{cid}.csv"
    infoPath = "data/"

    temporary = "temporary/pcid{pcid}cid{cid}/{name}.csv"
    temporaryPKL = "temporary/pcid{pcid}cid{cid}/{name}.pkl"
    temporaryPath = "temporary/pcid{pcid}cid{cid}/"

    show = "show//pcid{pcid}cid{cid}/{name}.jpg"
    showPath = "show//pcid{pcid}cid{cid}/"

    result = "result/pcid{pcid}cid{cid}/{name}.csv"
    resultPath = "result/pcid{pcid}cid{cid}/"


if __name__ == '__main__':
    try:
        m = Mode()
    except Exception as e:
        print(e)
