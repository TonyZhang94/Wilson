# -*- coding:utf-8 -*-

from Wilson.tools.utils import *


if __name__ == '__main__':
    pcid = "100"
    cid = "2018101516"

    Entrance(pcid=pcid, cid=cid)

    try:
        x = load_pkl("modelBasicAspectInfo")
        print(x)
    except Exception:
        pass

    for k, x in load_pkl("tagBasicAspectInfo").items():
        print(k, x)

    print("=======================")
    for k, x in load_pkl("targetBasicAspectInfo").items():
        print(k, x)
