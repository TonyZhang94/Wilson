# -*- coding:utf-8 -*-

import pandas as pd

from Wilson.settings import Mode, FileBase, Parameters
from Wilson.tools.public import Entrance
from Wilson.tools.readData import read_data
from Wilson.tools.utils import dump


class GetDataMethod(object):
    def __init__(self):
        """Init"""

    def get(self):
        """Get Function"""
        raise NotImplementedError


class GetReviewsMethod(GetDataMethod):
    """Get Data From 99: 5433 report_dg comment.review_analysis_pcid_cid"""
    def __init__(self):
        self.src = Mode.srcLOCAL

    def get(self):
        pcid, cid = Entrance().params
        fname = FileBase.info.format(name="comments", pcid=pcid, cid=cid)
        fields = ["brand", "model", "tag", "target", "grade", "frequency", "datamonth"]
        field, table = ", ".join(fields), "comment.review_analysis_pcid{pcid}_cid{cid}".format(pcid=pcid, cid=cid)
        sql = "SELECT {field} FROM {table} WHERE cid='{cid}';".format(
            field=field, table=table, cid=cid)
        df = read_data(self.src, fname=fname, sql=sql, db="report_dg")
        dump(df, "info")


class GetSpecialTagReviewsMethod(GetDataMethod):
    """Get Special Tag Data From 99: 5433 report_dg comment.review_analysis_pcid_cid"""
    def __init__(self):
        self.src = Mode.srcLOCAL

    def get(self):
        pcid, cid = Entrance().params
        fname = FileBase.info.format(name="comments", pcid=pcid, cid=cid)
        fields = ["brand", "model", "tag", "target", "grade", "frequency", "datamonth"]
        field, table = ", ".join(fields), "comment.review_analysis_pcid{pcid}_cid{cid}".format(pcid=pcid, cid=cid)
        sql = "SELECT {field} FROM {table} WHERE cid='{cid}';".format(
            field=field, table=table, cid=cid)
        temp = read_data(self.src, fname=fname, sql=sql, db="report_dg")

        df = pd.DataFrame()
        for k in Parameters.tagList:
            row_index = temp[temp['tag'] == k]
            df = pd.concat([df, row_index])
        dump(df, "info")
