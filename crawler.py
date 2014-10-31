__author__ = 'erwin'
#encoding=utf-8

import urllib2
import codecs
import os

import weibo

from comment_label_worm.Commons import *
from RedisMiddle import *


APP_KEY = '83693197'
APP_SECRET = 'cb7ce4af015d602aa8e1d2851c597f5c'
CALL_BACK = r'http://www.163.com'


class Worm:
    def __init__(self, redis_middle, weibo_client):
        self.redis_middle = redis_middle
        self.weibo_client = weibo_client

    def FetchFriends(self, uid, max_count=1000):
        '''
        把某个人的所有朋友都获取下来
        '''
        #timeline = self.weibo_client.statuses.home_timeline.get()
        #print(self.weibo_client.account.get_uid.get())
        print(self.weibo_client.users.show.get(uid=uid))
        '''
        friends = self.weibo_client.friendships.friends.get(uid=uid)
        i = 0
        for f in friends['users']:
            print(f)
        '''

        hots = self.weibo_client.trends.weekly.get()
        #print(hots)

        #fout = codecs.open("/users/erwin/tmp/xxx", "w", "utf-8")
        for hot in hots['trends'].values():
            for x in hot:
                msg = "%s, amount:%s name:%s\n" % (x['query'], x['amount'], x['name'])
                print(msg)
                #print(x)
                #fout.write(msg)
        #fout.close()

        #persons = self.weibo_client.place.nearby_users.list.get(lat=39.54, long=116.23)
        persons = self.weibo_client.place.nearby.users.get(lat=39.54, long=116.23)
        for p in persons['users']:
            print(p)

        status = self.weibo_client.statuses.user_timeline.get(uid=uid)#2941081491)
        for s in status['statuses']:
            print(s)

        self.weibo_client.statuses.update.post(status="bad bad bad bad bad open.weibo.com", lat=38.897930, long=-77.036430)


    def FetchRecent(self, uid, max_count=1000):
        '''
        把某人的最近的一些tweet都获取下来
        '''
        pass




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


def testWeibo():
    client = get_weibo_client(APP_KEY, APP_SECRET, CALL_BACK)

    while True:
        content = raw_input(">> ")
        if content:
            client.statuses.update.post(status=content)
            print("ok.")
        else:
            print("not ok.")

def processStatus(status):
    import jieba
    seg_list = jieba.cut(status, cut_all=False)
    return "/ ".join(seg_list)

def weiboFetch(redis_saver, FetchCount=100):
    '''
    crawl weibo tweet by api.
    and save to Redis.
    '''

    client = get_weibo_client(APP_KEY, APP_SECRET, CALL_BACK)

    page = 1
    count = 50
    read = 0
    last = None
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
                print("%d\t[ORIG]%s" % (read, processStatus(retweet['text'])))
                for msg in mid_list[retweet_mid]:
                    print("\n\t[RE] " + msg)

            else:
                print("%d\t%s\t%s" % (read, user['screen_name'], text))

            read = read+1
            last = s
        page = page+1

    print(last)

def crawl(url, path):
    resp = urllib2.urlopen(url)
    html = resp.read()
    print html


def get_rate_button(mid):
    return '''
        <button onclick="get('%s', 'star')"> Star </button> \
        <button onclick="get('%s', 'up')"> Up </button> \
        <button onclick="get('%s', 'down')"> Down </button>
    ''' % (mid, mid, mid)



def formatPrint():
    '''
    output a html web page, formatted.
    '''

    result = redis_saver.scan(cursor=0, match="14*", count=1000, reverse=False)

    tweets_map = {}
    tweets_list = []

    for r in result:
        ctime = r[0]
        ctime_str = datetime.datetime.fromtimestamp(ctime).strftime("%m-%d %H:%M:%S")
        tweet = None
        try:
            tweet = eval(r[1])
        except RuntimeError:
            print("parse tweet error %d, %s" % (ctime, r[1]))
            continue
        user = tweet['user']
        avatar_url = user['avatar_large']
        text = tweet['text']
        mid = tweet['mid']
        if 'retweeted_status' in tweet:
            retweet = tweet['retweeted_status']
            if not 'user' in retweet:
                continue
            retweet_user = retweet['user']
            retweet_text = retweet['text']
            retweet_mid = retweet['mid']
            retweet_ctime = unixToString( weiboTimeToUnix(retweet['created_at']) )
            retweet_avatar_url = retweet_user['avatar_large']
            if retweet_mid in tweets_map:
                msg = """
                    <div style="left:5px; border:1px dotted green;"> &nbsp;&nbsp;
                        <img src="%s" width="30px" height="30px"  alt="[todo]" />
                        <b>%s</b>(%s)&nbsp;%s
                    </div>
                """ % (retweet_avatar_url, retweet_user['screen_name'], retweet_ctime, text)
                tweets_map[retweet_mid].append(msg)
            else:
                msg = """
                    <div id="item-%s" style="border:1px dotted pink;">
                        %s <br/>
                        <img src="%s" width="50px" height="50px"  alt="[todo]" />
                        <b>%s</b>(%s): <br/> &nbsp;&nbsp;&nbsp;&nbsp; <b> %s </b>
                        <br/>
                        &nbsp;&nbsp;&nbsp;&nbsp;
                            <div style="left:5px; border:1px dotted green;">
                                <img src="%s" width="30px" height="30px"  alt="[todo]" />
                                <b> %s </b> %s &nbsp; %s
                            </div>
                    <br/> </div> <br/>\n
                """ % (retweet_mid, get_rate_button(retweet_mid), retweet_avatar_url, retweet_user['screen_name'], retweet_ctime, retweet_text,
                        avatar_url, user['screen_name'], ctime_str, text
                        )
                new_list = [msg]
                tweets_list.append(new_list)
                tweets_map[retweet_mid] = new_list
        else:
            # orignal tweet
            msg = """<div id="item-%s" style="border:1px dotted pink;">
                    %s <br/>
                    <img src="%s" width="50px" height="50px"  alt="[todo]" />
                    <b>%s</b>(%s): <br/> &nbsp;&nbsp;&nbsp;&nbsp; %s
                    <br/> </div> <br/>\n""" % \
              (mid, get_rate_button(mid), avatar_url, user['screen_name'], ctime_str, text)
            new_list = [msg]
            tweets_list.append(new_list)
            tweets_map[mid] = new_list


    # start to reder template
    HEADER = """
    <!DOCTYPEhtmlPUBLIC"-//W3C//DTDXHTML1.1//EN"
        "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
    <html>
        <title> Weibo(Defined) </title>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
        <script type="text/javascript">
            function get(mid, action){
                xmlHttp = new XMLHttpRequest();
                var url = "http://localhost:8000/rating?mid=" + mid + "&action=" + action;
                xmlHttp.open("GET", url, true);
                xmlHttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;");
                xmlHttp.send();
            }
        </script>

        <body>
            <center> <h1> Weibo(Defined) </h1></center>
            <div id="content" align="left" style="position:absolute;
                left:200px;top:30px; width:800px; border:2px solid #333;">
    """
    FOOTER = """
            </div>

        </body>
    </html>
    """

    file_name = "/Users/erwin/tmp/weibo/weibo_defined.html"
    fout = codecs.open(file_name, "w", "utf-8")
    fout.write(HEADER)

    tweets_list.reverse()
    for tweets in tweets_list:
        for tweet in tweets:
            fout.write(tweet)

    fout.write(FOOTER)
    fout.close()


def get_timeline(redis_saver, use_pattern=False):
    fout = codecs.open("/users/erwin/tmp/xxx", "w", "utf-8")
    timeline = redis_saver.scan_by_time(reverse=True, use_pattern=use_pattern)
    for pair in timeline:
        try:
            tweet = eval(pair[1])
            ts = datetime.datetime.fromtimestamp(int(pair[0])).strftime('%Y-%m-%d %H:%M:%S')
            fout.write("[%s] %s\n" % (ts, tweet['text']))
        except RuntimeError:
            print("parse tweet error %d, %s" % (pair[0], pair[1]))
            continue
    fout.close()

    print("total read records: %d" % len(timeline))

if __name__=='__main__':
    redis_saver = RedisMiddle(host='localhost', port=6379)
    weibo_client = get_weibo_client(APP_KEY, APP_SECRET, CALL_BACK)

    get_timeline(redis_saver, False)

    #testWeibo()
    #weiboFetch(redis_saver, FetchCount=100)
    #formatPrint()

    #worm = Worm(redis_saver, weibo_client)
    #worm.FetchFriends(1671432083)
    #worm.FetchFriends(2045933955)

