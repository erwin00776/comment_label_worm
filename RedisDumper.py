__author__ = 'erwin'

import os

import jieba

from RedisMiddle import RedisMiddle
from comment_label_worm.Commons import *

class RedisDumper:
    '''
    dump all rated tweets to files.
    '''

    def __init__(self):
        self.redis_middle = RedisMiddle()

    def cut_tweet(self, tweet):
        seg_list = jieba.cut(tweet, cut_all=False)
        return " ".join(seg_list)

    def dump_rating(self):
        result = self.redis_middle.scan(cursor=0, match="14*", count=5000, reverse=False)

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
            self.redis_middle.mid_put(mid, user['screen_name'] + " " + text)
            if 'retweeted_status' in tweet:
                retweet = tweet['retweeted_status']
                if not 'user' in retweet:
                    continue
                retweet_user = retweet['user']
                retweet_text = retweet['text']
                retweet_mid = retweet['mid']
                retweet_ctime = unixToString( weiboTimeToUnix(retweet['created_at']) )
                retweet_avatar_url = retweet_user['avatar_large']
                self.redis_middle.mid_put(retweet_mid, retweet_user['screen_name']+" "+retweet_text)
                if retweet_mid in tweets_map:
                    msg = "%s %s" % (retweet_user['screen_name'], text)
                    tweets_map[retweet_mid].append(mid)
                else:
                    msg = "%s %s\n%s %s" % \
                          (retweet_user['screen_name'], retweet_text,
                            user['screen_name'], text
                            )
                    new_list = [retweet_mid, mid]
                    tweets_list.append(new_list)
                    tweets_map[retweet_mid] = new_list
            else:
                msg = "%s %s" % (user['screen_name'], text)
                new_list = [mid]
                tweets_list.append(new_list)
                tweets_map[mid] = new_list

        tweets_list.reverse()
        for tweets in tweets_list:
            mid = tweets[0]
            rating = self.redis_middle.rating_get(mid)
            if rating is None:
                rating = "normal"
            elif rating=='star':
                rating = 'up'
            fname = os.path.join("/Users/erwin/tmp/weibo", rating, mid)
            fout = open(fname, 'w')
            for tweet_mid in tweets:
                tweet = self.redis_middle.mid_get(tweet_mid)
                if tweet is None:
                    print("none: " + tweet_mid)
                    continue
                cutted_tweet = self.cut_tweet(tweet)
                print(cutted_tweet)
                fout.write(cutted_tweet.encode("utf-8") + "\n")
            fout.close()

if __name__=='__main__':
    redis_dumper = RedisDumper()
    redis_dumper.dump_rating()
