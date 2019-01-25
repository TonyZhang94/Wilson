# -*- coding:utf-8 -*-

import os

from Wilson.tools.utils import *


class InitMethod(object):
    """Init Method"""
    def __init__(self):
        """Init"""

    def init(self):
        """Init Function"""
        raise NotImplementedError


class InitFilesMethod(InitMethod):
    """Initialize Directory And Files For Processing"""
    def init(self):
        pcid, cid = Entrance().params
        try:
            os.makedirs("data")
        except FileExistsError:
            pass
        except Exception as e:
            raise e

        try:
            os.makedirs(FileBase.temporaryPath.format(pcid=pcid, cid=cid))
        except FileExistsError:
            pass
        except Exception as e:
            raise e

        try:
            os.makedirs(FileBase.resultPath.format(pcid=pcid, cid=cid))
        except FileExistsError:
            pass
        except Exception as e:
            raise e
