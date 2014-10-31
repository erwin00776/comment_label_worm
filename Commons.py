__author__ = 'erwin'


import datetime
import time

def weiboTimeToUnix(str):
    ctime = datetime.datetime.strptime(str, "%a %b %d %H:%M:%S +0800 %Y")
    unix_timestamp = time.mktime(ctime.timetuple())
    return unix_timestamp


def unixToString(unix_timestamp):
    return datetime.datetime.fromtimestamp(unix_timestamp).strftime("%m-%d %H:%M:%S")
