# -*- coding:utf-8 -*-

import os

from Wilson.tools.public import Entrance
from Wilson.settings import FileBase


class ClearFileMethod(object):
    """Clear File Method"""
    def __init__(self, *args, **kwargs):
        """Init"""

    def clear(self):
        """Clear Function"""
        raise NotImplementedError


class RemainFinalResultMethod(ClearFileMethod):
    """Clear All Temporary Directories And Files Except Results Files"""
    def __init__(self):
        self.keywords = set(["final"])

    def clear(self):
        pcid, cid = Entrance().params

        try:
            info_files = os.listdir(FileBase.infoPath)
        except FileNotFoundError:
            pass
        else:
            for file in info_files:
                os.remove(FileBase.infoPath+file)
            os.removedirs(FileBase.infoPath)

        path = FileBase.temporaryPath.format(pcid=pcid, cid=cid)
        try:
            result_files = os.listdir(path)
        except FileNotFoundError:
            pass
        else:
            for file in result_files:
                if file not in self.keywords:
                    os.remove(path + file)
            os.removedirs(path)


class ClearAllMethod(ClearFileMethod):
    """Clear All Temporary Directories And Files"""
    def clear(self):
        pcid, cid, _ = Entrance().params

        try:
            info_files = os.listdir(FileBase.infoPath)
        except FileNotFoundError:
            pass
        else:
            for file in info_files:
                os.remove(FileBase.infoPath+file)
            os.removedirs(FileBase.infoPath)

        path = FileBase.temporaryPath.format(pcid=pcid, cid=cid)
        try:
            result_files = os.listdir(path)
        except FileNotFoundError:
            pass
        else:
            for file in result_files:
                os.remove(path + file)
            os.removedirs(path)

        path = FileBase.resultPath.format(pcid=pcid, cid=cid)
        try:
            result_files = os.listdir(path)
        except FileNotFoundError:
            pass
        else:
            for file in result_files:
                os.remove(path + file)
            os.removedirs(path)


class ClearNothingMethod(ClearFileMethod):
    """Don't Clear Any Temporary Directories And Files"""
    def clear(self):
        pass
