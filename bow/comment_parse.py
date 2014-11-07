__author__ = 'erwin'
#encoding=UTF-8

# @desciption: 这个是将json格式的评论单独取出来，只保留最主要的评语
#

import json
import codecs
import os
import chardet
import jieba
import sys


def cut_line(line):
    seg_list = jieba.cut(line, cut_all=True)
    return " ".join(seg_list)

def get_short_sentences(sentence,
                        splitters=[
                            u' ', u'，', u'。', u'；', u'！', u'、', u'：', u'　', u'～',
                            u',', u'.', u'!', u'~', u':', u';'
                        ]):
    short_sentences = []
    try:
        for split in splitters:
            sentence = sentence.replace(split, ',')
        lst = sentence.split(',')
        for short in lst:
            if len(short) > 1:
                short_sentences.append(short)
    except KeyError:
        pass
    return short_sentences


def parse(file_name, fout=None, auto_line=False, short_sentences=False, auto_cut=True):
    fout_auto_close = True
    if fout is None:
        fout = codecs.open(file_name+".parsed", 'w', encoding='utf-8')
        fout_auto_close = False

    fin = open(file_name, 'r')
    for line in fin.readlines():
        line = line.strip()
        if len(line) <= 0:
            continue
        line = line[13:]
        try:
            try:
                line = line.decode("GB18030")
            except UnicodeDecodeError as e:
                print("decode failed!?!", chardet.detect(line))
                print(e)

            rate_list = json.loads(line, encoding='utf-8')
            if rate_list is None or not 'rateList' in rate_list:
                continue
            for rate in rate_list['rateList']:
                comment = rate['rateContent']
                if short_sentences:
                    comments = get_short_sentences(comment)
                else:
                    comments = [comment]
                for c in comments:
                    if auto_cut:
                        comment_cutted = cut_line(c)
                        fout.write(comment_cutted)
                    else:
                        fout.write(c)
                    if auto_line:
                        fout.write("\n")
        except KeyError:
            print("parse line %s failed at %s" % (line, file_name))
            continue
        except:
            print("error failed at %s" % file_name)
            pass

    fin.close()
    if not fout_auto_close:
        fout.close()


def scan_tmp_dir(dir_name, class_name, auto_line=True, short_sentences=False, auto_cut=True):
    fout = codecs.open(os.path.join(dir_name, "../all_tmall_comments" + "_" + class_name), 'w', encoding='utf-8')
    if auto_line and auto_cut:
        # prepare for word2vec: multiline and cutted words
        fout.write("</b>\n")
    item_list = os.listdir(os.path.join(dir_name, class_name))
    for item in item_list:
        if item.find('tmall_comments') == 0:
            parse(os.path.join(dir_name, class_name, item), fout, auto_line=auto_line, short_sentences=short_sentences, auto_cut=auto_cut)
            print("parse file %s done" % item)
    fout.close()


def gen_freq_dict(file_name, freq_name=None):
    word2freq = {}
    fin = codecs.open(file_name, 'r', encoding='utf-8')
    fout = None
    if not freq_name is None:
        fout = codecs.open(freq_name, 'w', encoding='utf-8')

    line_count = 0
    for line in fin.readlines():
        line = line.strip()
        words = line.split()
        line_count += 1
        for w in words:
            freq = word2freq.get(w, 0)
            freq += 1
            word2freq[w] = freq
    total = 0
    for (word, word_freq) in word2freq.items():
        if not fout is None:
            freq = word_freq * 1.0 / total
            fout.write(word + ' ' + str(word_freq) + ' ' + str(freq) + '\n')
        total += word_freq
    if not fout is None:
        fout.close()
    fin.close()
    return word2freq, total, line_count


def test_freq():
    all_freq, all_total, all_line = gen_freq_dict("/users/erwin/tmp/all_tmall_comments", "/users/erwin/tmp/all.freq")
    commodity_freq, commodity_total, commodity_line = gen_freq_dict("/users/erwin/tmp/make-up",
                                                                    "/users/erwin/tmp/makeup.freq")
    while True:
        word = sys.stdin.readline()
        word = word.strip()
        word = word.decode("utf-8")
        af = all_freq.get(word, 0)
        cf = commodity_freq.get(word, 0)
        a_ratio = af*1.0 / all_line
        c_ratio = cf*1.0 / commodity_line
        print(a_ratio, c_ratio, c_ratio/a_ratio)

def load_word_attr(path_name):
    fin = codecs.open(path_name, 'r', encoding='utf-8')
    word_attrs = {}
    for line in fin.readlines():
        line = line.strip()
        pair = line.split()
        types_vec = pair[1].split('-')
        types_set = set()
        for t in types_vec:
            types_set.add(t)
        word_attrs[pair[0]] = types_set
    return word_attrs


def word_relation():
    '''
    对于每句话里面的每个动名词，上下文出现的次数进行统计
    '''
    words_relation = {}
    fin = codecs.open("/users/erwin/work/comment_labeled/all_tmall_comments", 'r', encoding='utf-8')
    word_attrs = load_word_attr('/users/erwin/tmp/words_attr.txt')
    for line in fin.readlines():
        line = line.strip()
        words = jieba.cut(line, cut_all=True)
        propertys = []
        for w in words:
            attr = word_attrs.get(w, {})
            if 'd' in attr:
                continue
            if 'n' in attr or 'v' in attr or 'a' in attr:
                propertys.append(w)
        for p1 in range(0, len(propertys)):
            for p2 in range(0, len(propertys)):
                if p1 == p2:
                    continue
                w1 = propertys[p1]
                w2 = propertys[p2]
                relations = words_relation.get(w1, None)
                if relations is None:
                    words_relation[w1] = {w2: 1, 'line_count': 1}
                else:
                    count = relations.get(w2, 0)
                    relations[w2] = count + 1
                    relations['line_count'] += 1
                    words_relation[w1] = relations
    fin.close()
    fout = codecs.open("/users/erwin/work/comment_labeled/words_relation", 'w', encoding='utf-8')
    for (word, relations) in words_relation.items():
        rel = []
        line_count = relations.get('line_count', 1)
        for (w, c) in relations.items():
            if w != 'line_count' and c*1.0/line_count > 0.01:
                rel.append(w + ":" + str(c))
        fout.write(word + "\t" + ' '.join(rel) + "\n")

    fout.close()


if __name__ == '__main__':
    scan_tmp_dir('/users/erwin/work/comment_labeled/raw_comments/',
                 'cosmetic',
                 auto_line=True,
                 short_sentences=True,
                 auto_cut=False)
    #word_relation()

    #test_freq()
    '''
    fout = codecs.open(os.path.join("/users/erwin/tmp", "tmall_comments_clothes_sentences"), 'w', encoding='utf-8')
    parse("/users/erwin/tmp/tmall_comments_clothes_40887946035_1579139371",
          fout=fout, auto_line=True, short_sentences=True, auto_cut=False)
    '''
