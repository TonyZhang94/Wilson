# -*- coding:utf-8 -*-

import pandas as pd

from Wilson.settings import FileBase
from Wilson.tools.public import Entrance


def dump(data, name, repath=None):
    pcid, cid = Entrance().params
    if repath is None:
        repath = FileBase.temporary.format(pcid=pcid, cid=cid, name=name)
    data.to_csv(repath, encoding="utf_8_sig")
    print("dump len", len(data))


def load(name, repath=None):
    pcid, cid = Entrance().params
    if repath is None:
        repath = FileBase.temporary.format(pcid=pcid, cid=cid, name=name)
    df = pd.read_csv(repath, encoding="utf_8_sig", index_col=0)
    print("load len", len(df))
    return df
