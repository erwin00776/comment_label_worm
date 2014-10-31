__author__ = 'erwin'
#coding=utf-8

import jieba
import codecs
import urllib
import urllib2
import re
import threading
import chardet
import time


query_done_set = {}

def cut_line(line):
    seg_list = jieba.cut(line, cut_all=False)
    return " ".join(seg_list)


def cut_words(src, dst):
    fin = codecs.open(src, 'r', 'utf-8')
    fout = codecs.open(dst, 'w', 'utf-8')
    for line in fin.readlines():
        line = line.strip()
        prefix = 9
        if line.find("contenttitle") > 0:
            prefix = 15
        l = len(line)
        if l <= prefix*2+1:
            continue
        line = line[prefix:l-prefix]
        fout.write(cut_line(line))
    fin.close()
    fout.close()

def download_comments(itemid, sellerid, query=''):
    fout = open("/users/erwin/tmp/tmall_comments_%s_%s_%s" % (query, itemid, sellerid), 'w')
    for pageid in range(1, 200):
        url_prefix = "http://rate.tmall.com/list_detail_rate.htm?itemId=%s&spuId=&sellerId=%s&order=1&currentPage=%d" % (itemid, sellerid, pageid)
        url = url_prefix + '&append=0&content=1&tagId=&posi=&picture=&ua=248YlJgThc3UTYWOBgrdllqXG9aa1liUGtefiF%2B%7CYVJ8T3lKekp5Q3FGdUN2RRo%3D%7CYFB%2BJwdWNVEyQikJJwc9HTMTXD9efiF%2B%7CZ1RkSmpZb1xsXG9VZ1BjVWBTa1l1RnZBcUp%2FRXJFdENzSHJCeEJiPQ%3D%3D%7CZlVuQBkoBjUHNgIsHDISIBc3aDc%3D%7CZVR6IxMiDD4QIxMpGzUOOQ48EiERKxk3DT8NIxAgGigGMwM2aTY%3D%7CZFJ8JQUlCzELPRMiEigSPAk7DThnOA%3D%3D%7Ca11zKgoqBDEBNRsrHS4eMAs%2BBD9gPw%3D%3D%7CalxyKwsrBTIJMx0uFSUQPg03BzIJVgk%3D%7CaV9xKAgoBj0NOhQnECAXOQk7CDkNUg0%3D%7CaF9xKAgoBl9kUWRKeU5%2FTBM9DyEBIQ8%2FDTgJO2Q7%7Cb1l3Lg4uADUCMx0uGiofMQEyAzEBXgE%3D%7Cbll3Lg4uAFlsXm9BckZwQR4wAiwMLAIyATYAM2wz%7CbVt1LAwsAjkNPRMgESESPAw9DjkJVgk%3D%7CbFt1LAwsAltgVW9BckNyRxg2BCoKKgQ0BTIGMG8w%7Cc0VrMhIyHCkZLgAxADYNIxMmEyEWSRY%3D%7CckRqMxMzHSYRJwk4CToPIRErGCkcQxw%3D%7CcUZoMRExH0Z9SnxSY1JhVHpBckNvW2tcckR1R2lSYU9%2BRRo0BigIKAY2DD0KO2Q7%7CcEZ0RmhadERqWW9cckN0QW9Zd0R2WGNNd1lsQnFGaF9xQnNdbEJxQmxfcUNtVwg%3D&_ksTS=1412218079834_3853&callback=jsonp3854'
        try:
            page = None
            try_times = 0
            while page is None and try_times < 5:
                page = urllib2.urlopen(url, timeout=3)
                try_times += 1
        except:
            print("exception %s" % url)
            pass
        line = page.read()
        if len(line) <= 256:
            return
        fout.write(line)
        page.close()
        print('download comment %s page %d' % (query, pageid))
    fout.close()


def get_item_seller_id(file_path, query=''):
    fin = open(file_path, 'r')
    is_tmall = False
    for line in fin.readlines():
        line = line.strip()
        if line.find('data-pid') > 0:
            if line.find('tmall') > 0:
                is_tmall = True
            else:
                is_tmall = False
        if is_tmall and line.find('col seller feature-dsi-tgr') > 0:
            sid = re.search('sid=\d+', line).group()
            bid = re.search('bid=\d+', line).group()

            sid = sid.split('=')[1]     # seller id
            bid = bid.split('=')[1]     # item id

            download_comments(itemid=bid, sellerid=sid, query=query)
            print("download comment %s %s %s done." % (query, bid, sid))

    fin.close()

class CommentDownloader(threading.Thread):
    def __init__(self, query):
        threading.Thread.__init__(self)
        self.query = query
        self.max_retries = 3

    def run(self):
        retries = 0
        ret = 1
        while retries < self.max_retries and ret != 0:
            ret = self.try_to_download()
            retries += 1

    def try_to_download(self):
        try:
            file_path = '/users/erwin/tmp/tmall_search_result_' + self.query
            fout = open(file_path, 'w')
            url = "http://s.taobao.com/search?spm=a230r.1.8.3.VcgCfO&sort=sale-desc&initiative_id=staobaoz_20141002&tab=all&q=%s" % self.query
            url = url_encode(url+'&stats_click=search_radio_all%253A1#J_relative')
            page = urllib2.urlopen(url, timeout=3)
            fout.write(page.read())
            fout.close()

            self.get_item_seller_id(file_path, query=self.query)

            page.close()
            print("[%s] download query %s done." % (self.getName(), self.query))
            return 0
        except KeyError:
            print("[%s] download query %s failed." % (self.getName(), self.query))
            return -1

    def get_item_seller_id(self, file_path, query):
        fin = open(file_path, 'r')
        is_tmall = False
        for line in fin.readlines():
            line = line.strip()
            if line.find('data-pid') > 0:
                if line.find('tmall') > 0:
                    is_tmall = True
                else:
                    is_tmall = False
            if is_tmall and line.find('col seller feature-dsi-tgr') > 0:
                sid = re.search('sid=\d+', line).group()
                bid = re.search('bid=\d+', line).group()

                sid = sid.split('=')[1]     # seller id
                bid = bid.split('=')[1]     # item id

                download_comments(itemid=bid, sellerid=sid, query=query)
                print("[%s] download comment %s %s %s done." % (self.getName(), query, bid, sid))



def download_search_result(query=""):
    try:
        file_path = '/users/erwin/tmp/tmall_search_result_' + query
        fout = open(file_path, 'w')
        url = "http://s.taobao.com/search?spm=a230r.1.8.3.VcgCfO&sort=sale-desc&initiative_id=staobaoz_20141002&tab=all&q=%s" % query
        url = url_encode(url+'&stats_click=search_radio_all%253A1#J_relative')
        page = urllib2.urlopen(url, timeout=3)
        fout.write(page.read())
        fout.close()

        get_item_seller_id(file_path, query=query)

        page.close()
        global query_done_set
        query_done_set[query] = 1
        print("download query %s done." % query)
    except:
        print("download query %s failed." % query)


def url_encode(url):
    x = url.decode('UTF-8')
    y = x.encode('GB2312')
    return y


def download_all_comments():
    global query_done_set
    query_list = ["中跟女鞋","短靴","英伦 复古 绒", "平底", "女式鞋单鞋","秋季女式鞋","单鞋","马丁靴","高跟鞋","头层牛皮"]
    query_list = ["短靴", "中跟女鞋", "平跟 蝴蝶结", "马丁靴", "单鞋", "短筒", "高跟鞋", "女式鞋单鞋", "皮鞋", "皮鞋男", "商务休闲", "滑板鞋男款", "帆布鞋男款", "滑板鞋男", "马丁靴男", "男式鞋休闲鞋", "运动鞋男", "豆豆鞋男"]
    query_list = ['茶叶', '食品', '水果', '牛奶', '零食', '饼干', '饮料', '牛肉干', '猪肉脯']
    query_list = ['铁观音', '红茶', '绿茶', '普洱', '花茶', '龙井']
    query_list = ['化妆品', '护肤套装', '面膜', '乳液', '面霜', '眼霜', '身体护理', '男士护理', '洁面', '化妆水', '精油芳疗', '丰胸', 'T区护理', '防晒'
                  '唇部护理', '去角化', '按摩霜', '敏感修护', '补水'
                ]
    worker_set = set()
    for query in query_list:
        try:
            while len(worker_set) > 5:
                time.sleep(1)
                for t in worker_set:
                    t.join(timeout=1)
                    if not t.isAlive():
                        worker_set.remove(t)
            foo = CommentDownloader(query)
            worker_set.add(foo)
            foo.start()
        except:
            print("except %s, skip this." % query)
            pass
    for t in worker_set:
        t.join()

if __name__ == '__main__':
    #download_all_comments()
    #cut_words("/Users/erwin/tmp/all_tmall_comments", "/Users/erwin/tmp/all_tmall_comments.cut")
    download_comments(itemid='8095482851', sellerid='519286239', query='make-up')


