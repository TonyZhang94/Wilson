# -*- coding:utf-8 -*-


class Descriptor(object):
    __counter = 0

    def __init__(self, interface):
        cls = self.__class__
        prefix = cls.__name__
        index = cls.__counter
        self.storage_name = "_{}#{}".format(prefix, index)
        self.interface = interface
        cls.__counter += 1

    def __get__(self, instance, owner):
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        if value is None:
            return
        if isinstance(value, self.interface):
            setattr(instance, self.storage_name, value)
        else:
            raise ValueError("Parameter Must Be", self.interface.__name__)


class Entrance(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, **kwargs):
        if 0 != len(kwargs):
            try:
                self.__pcid = str(kwargs["pcid"])
                self.__cid = str(kwargs["cid"])
            except Exception as e:
                raise e

    @property
    def pcid(self):
        return self.__pcid

    @property
    def cid(self):
        return self.__cid

    @property
    def params(self):
        return self.__pcid, self.__cid
