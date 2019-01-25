# -*- coding:utf-8 -*-


import sqlalchemy as sa

from Wilson.settings import DBDefault


class Engine(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            print("Creating Engine Singleton ...")
            cls.engines_pool = dict()
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, *args, **kwargs):
        pass

    def get_engine(self, db, info=DBDefault):
        try:
            conn = self.__class__.engines_pool[db]
            print("Find Existed Connection With", db, "...")
            return conn
        except KeyError:
            print("Try Create Connection With DB", db, "...")
            conn = sa.create_engine("postgresql://{USER}:{PASS}@{HOST}:{PORT}/{DB}".
                                    format(USER=info.user,
                                           PASS=info.password,
                                           HOST=info.host,
                                           PORT=info.port,
                                           DB=info.DB[db]))
            self.__class__.engines_pool[db] = conn
            return conn

    def __call__(self, db):
        return self.get_engine(db)


if __name__ == '__main__':
    engine = Engine()
    conn = engine("report_dg")
