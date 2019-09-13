# encoding=utf-8
""" DAO module """

import datetime as dt
import dbm
import os
import os.path


def store(**args):
    """ Placeholder! """

    if os.path.basename(os.getcwd()) != "overseer":
        raise RuntimeError("Unexpected CWD")

    with dbm.open("dao/seen.dbm", "c") as db:
        key: str = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        db[key] = str(args)
        print("Stored:\t%s" % args)
