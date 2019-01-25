# -*- coding:utf-8 -*-

import pandas as pd

from Wilson.tools.engine import Engine
from Wilson.tools.myExceptions import *


def read_data(src, fname, sql, db):
    try:
        if not src:
            raise ReadDBException
        df = pd.read_csv(fname, encoding="utf_8_sig", index_col=0)
    except (FileExistsError, FileNotFoundError, ReadDBException) as flag:
        print(sql)
        engine = Engine()
        try:
            df = pd.read_sql_query(sql, engine(db))
        except Exception as e:
            raise e
        else:
            if flag.__doc__ != "Choose Get Data From DB":
                df.to_csv(fname, encoding="utf_8_sig")
    except Exception as e:
        raise e
    return df
