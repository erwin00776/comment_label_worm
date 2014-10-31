__author__ = 'erwin'
#encoding=utf-8

import os

import weibo

from RedisMiddle import *


APP_KEY = '83693197'
APP_SECRET = 'cb7ce4af015d602aa8e1d2851c597f5c'
CALL_BACK = r'http://www.163.com'




class MyAPIClient(weibo.APIClient):
    def __init__(self, app_key, app_secret, redirect_uri=None, response_type='code',
                 domain='api.weibo.com', version='2'):
        weibo.APIClient.__init__(self, app_key, app_secret, redirect_uri=redirect_uri,
                                 response_type='code', domain='api.weibo.com', version='2')
        self.uid = ""

    def request_access_token_info(self, at):
        r = weibo._http_post('%s%s' % (self.auth_url, 'get_token_info'), access_token=at)
        current = int(time.time())
        expires = r.expire_in + current
        remind_in = r.get('remind_in', None)
        if remind_in:
            rtime = int(remind_in) + current
            if rtime<expires:
                expires = rtime
        return weibo.JsonDict(expires=expires, expires_in=expires, uid=r.get('uid', None))

    def set_uid(self, uid):
        self.uid = uid


TOKEN_FILE = 'token_record.log'
def load_tokens(filename=TOKEN_FILE):
    acc_tk_list = []
    try:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        f = open(filepath)
        acc_tk_list.append(f.readline().strip())
        f.close()
    except IOError:
        print("file not exists.")
    return acc_tk_list

def dump_tokens(tk, filename=TOKEN_FILE):
    try:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        f = open(filepath, 'a')
        f.write(tk)
        f.write('\n')
    except IOError:
        print("write file failed.")
    f.close()

def get_weibo_client(appkey, appsecret, callback):
    client = MyAPIClient(appkey, appsecret, callback)
    at_list = load_tokens()
    if at_list:
        access_token = at_list[-1]
        r = client.request_access_token_info(access_token)
        expires_in = r.expires_in
        print(" token expires in %f" % expires_in)
        if r.expires_in <= 0:
            return None
        client.set_uid(r.uid)
    else:
        #client = weibo.APIClient(APP_KEY, APP_SECRET, CALL_BACK)
        auth_url = client.get_authorize_url()
        print "auth_uri: " + auth_url
        code = raw_input("input the return code: ")
        r = client.request_access_token(code)
        access_token = r.access_token
        expires_in = r.expires_in
        dump_tokens(r.access_token)

    client.set_access_token(access_token, expires_in)
    client.set_uid(r.uid)
    return client


def autoWeiboFetch(redis_saver, FetchCount=100):
    '''
    auto crawl weibo tweet
    '''
    cur_tick = datetime.datetime.now().strftime("%s")
    try:
        fin = open('/tmp/auto_weibo.last_tick', 'r')
        last_tick = fin.readline()
        fin.close()
    except:
        last_tick = cur_tick

    fetch_count = FetchCount
    stop_time = int(cur_tick) - int(last_tick)
    if stop_time > 3600:
        fetch_count = fetch_count * (stop_time / 1800)

    client = get_weibo_client(APP_KEY, APP_SECRET, CALL_BACK)

    page = 1
    count = 50
    read = 0
    while read < FetchCount:
        timeline = client.statuses.home_timeline.get(page=page, count=count)
        for status in timeline['statuses']:
            redis_saver.put(status)
            read = read + 1
        page = page + 1

    print("read total: %d" % read)

    fout = open('/tmp/auto_weibo.last_tick', 'w')
    fout.write(datetime.datetime.now().strftime("%s"))
    fout.close()

def weiboFetch(redis_saver, FetchCount=100):
    '''
    crawl weibo tweet by api.
    and save to Redis.
    '''

    client = get_weibo_client(APP_KEY, APP_SECRET, CALL_BACK)

    page = 1
    count = 50
    read = 0
    mid_list = {}
    while read < FetchCount:
        timeline = client.statuses.home_timeline.get(page=page, count=count)
        for s in timeline['statuses']:
            # save the orig tweet in redis
            redis_saver.put(s)

            mid = s['mid']
            user = s['user']
            text = s['text']
            if 'retweeted_status' in s:
                retweet = s['retweeted_status']
                retweet_mid = retweet['mid']

                # find the same status
                if not retweet_mid in mid_list:
                    mid_list[retweet_mid] = [mid+"## " + user['screen_name'] + "## " + text]
                else:
                    mid_list[retweet_mid].append(mid+"## " + user['screen_name'] + "## " + text)
                #print("%d\t[ORIG]%s" % (read, processStatus(retweet['text'])))
                for msg in mid_list[retweet_mid]:
                    print("\n\t[RE] " + msg)

            else:
                print("%d\t%s\t%s" % (read, user['screen_name'], text))

            read = read+1
            last = s
        page = page+1
    print("auto fetch done, total %d" % read)


if __name__ == '__main__':
    redis_saver = RedisMiddle(host='localhost', port=6379)
    weibo_client = get_weibo_client(APP_KEY, APP_SECRET, CALL_BACK)

    #weiboFetch(redis_saver, FetchCount=500)
    autoWeiboFetch(redis_saver, FetchCount=500)
