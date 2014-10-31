__author__ = 'erwin'


import redis
import time
import datetime

def SorterByTime(pair):
    return pair[0]

class RedisMiddle():
    def __init__(self, host="localhost", port=6379, db=0):
        self.host = host
        self.port = port
        self.r = redis.Redis(self.host, self.port, db=db)
        if self.r is None:
            print("connect to redis(%s:%d) fail." % (self.host, self.port))

    def put(self, tweet):
        ctime = datetime.datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0800 %Y")
        unix_timestamp = time.mktime(ctime.timetuple())
        self.r.set(unix_timestamp, tweet)

    def get(self, key):
        return self.r.get(key)

    def rating_put(self, mid, action):
        self.r.hset("rating", mid, action)

    def rating_get(self, mid):
        return self.r.hget("rating", mid)

    def rating_scan(self):
        self.r.hgetall("rating")

    def mid_put(self, mid, text):
        self.r.hset("mid", mid, text)

    def mid_get(self, mid):
        return self.r.hget("mid", mid)

    def scan(self, cursor=0, match=None, count=100, reverse=False):
        count, key_list = self.r.scan(cursor=cursor, match=match, count=count)
        result = []
        if count > 0:
            for k in key_list:
                dot_pos = -1
                try:
                    dot_pos = k.index('.')
                except ValueError:
                    pass
                key = int(k[:dot_pos], 10)
                result.append([key, self.get(k)])
        else:
            print("scan return empty result.")

        result = sorted(result, key=lambda pair: pair[0], reverse=reverse)

        return result

    def scan_by_time(self, reverse=False, use_pattern=True):
        t = datetime.datetime.now().strftime("%s")
        if use_pattern:
            pattern = t[0:5] + '*'
        else:
            pattern = '*'
        next_iter = 1
        result = []
        while next_iter > 0:
            next_iter, key_list = self.r.scan(next_iter, match=pattern, count=10)
            next_iter = int(next_iter)
            for k in key_list:
                try:
                    dot_pos = k.index(".")
                    key = int(k[:dot_pos], 10)
                    result.append([key, self.get(k)])
                except ValueError:
                    print("bad key: %s" % k)
                    pass


        result = sorted(result, key=lambda pair: pair[0], reverse=reverse)
        return result

