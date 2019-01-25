# -*- coding:utf-8 -*-

import time
import functools
import warnings
import numpy as np
import pandas as pd
import numbers


def format_args(*args, **kwargs):
    arg_list = list()
    if args:
        # arg_list.append(", ".join(str(arg) if isinstance(arg, (numbers.Number, str))
        #                           else "Type %s Size %d" % (str(type(arg)), len(arg)) for arg in args[0]))
        arg_list.append(", ".join(str(arg) if isinstance(arg, (numbers.Number, str))
                                  else "Type %s" % (str(type(arg))) for arg in args[0]))
    if kwargs:
        pairs = ["%s=%s" % (key, value) for key, value in kwargs.items() if isinstance(value, (numbers.Number, str))]
        arg_list.append(", ".join(pairs))
    arg_str = ", ".join(arg_list)
    return arg_str


def repr_result_info(_result):
    if isinstance(_result, tuple):
        msg = list()
        for item in _result:
            try:
                msg.append("Type %s Size %d" % (type(item), len(item)))
            except TypeError:
                msg.append("None")
        if len(msg):
            print("Return:", ", ".join(msg))
    else:
        try:
            print("Return:", "Type", type(_result), "Size", len(_result))
        except TypeError:
            pass


def logging(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        # print("\n===================================")
        name = func.__name__
        arg_str = format_args(args, **kwargs)
        print("START: %s(%s)" % (name, arg_str))
        start = time.time()
        _result = func(*args, **kwargs)
        end = time.time()
        print(("END: %s(%s) [%0.8fs]" % (name, arg_str, end-start)))
        repr_result_info(_result)
        print("===================================")
        return _result
    return _


def connect(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        name = func.__name__
        arg_str = format_args(args, **kwargs)
        print("Connection Info: %s(%s)" % (name, arg_str))
        try:
            _result = func(*args, **kwargs)
        except Exception as e:
            raise e
        else:
            print("Connect Success！")
        return _result
    return _


def ignore_warning(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        name = func.__name__
        arg_str = format_args(args, kwargs)
        warnings.filterwarnings("ignore")
        print("Ignore Warning: %s(%s)" % (name, arg_str))
        try:
            _result = func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            print("Reset Warning: %s(%s)" % (name, arg_str))
            warnings.filterwarnings("default")
        return _result
    return _


def coroutine(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return _


def process(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        name = func.__name__
        arg_str = format_args(args, **kwargs)
        start = time.time()
        _result = func(*args, **kwargs)
        end = time.time()
        print("\n***********************************")
        print("INFO: %s(%s)" % (name, arg_str))
        print(("COST: [%0.8fs]" % (end - start)))
        repr_result_info(_result)
        print("***********************************")
        return _result
    return _
