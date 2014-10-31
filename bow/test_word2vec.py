__author__ = 'erwin'
#coding=utf-8

import jieba
from gensim.models import word2vec
import numpy
import codecs
import sys


def load_clazz(file_path):
    fin = open(file_path, 'r')
    clazz_map = {}
    for line in fin.readlines():
        line = line.strip()
        pieces = line.split()
        if len(pieces) == 2:
            pieces.append(pieces[0])
        short_sentences = []
        for i in range(1, len(pieces)):
            seg_list = jieba.cut(pieces[i], cut_all=False)
            tmp = []
            for word in seg_list:
                tmp.append(word)
            short_sentences.append(tmp)
        clazz_map[pieces[0]] = short_sentences
    fin.close()
    return clazz_map


def load_clazz2(file_path):
    fin = open(file_path, 'r')
    clazz_map = {}
    for line in fin.readlines():
        line = line.strip()
        pieces = line.split()
        if len(pieces) == 1:
            pieces.append(pieces[0])
        short_sentences = []
        for i in range(1, len(pieces)):
            seg_list = jieba.cut(pieces[i], cut_all=False)
            tmp = []
            for word in seg_list:
                tmp.append(word)
            short_sentences.append(tmp)
        clazz_map[pieces[0]] = short_sentences
    fin.close()
    return clazz_map


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


def test():
    model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/all_tmall_comments.bin', binary=True)
    x = model.most_similar([u'偏大'], [u'问题', u'尺码'], topn=3)
    word_attrs = load_word_attr('/users/erwin/tmp/words_attr.txt')
    case = [u'质量', u'尺码', u'合适', u'没有', u'气味', u'好评']
    case = [u'外观', u'好看']
    s = u"物美价廉"
    s = u"价格实惠"
    while True:
        s = sys.stdin.readline()
        s = s.strip()
        case = []
        for word in jieba.cut(s, cut_all=False):
            case.append(word)
        print('/ '.join(case))

        #clazz_map = load_clazz('/Users/erwin/tmp/shoe_clazz')
        clazz_map = load_clazz('/Users/erwin/tmp/tea_clazz')

        top_list = []
        for (clazz_name, clazz_list) in clazz_map.items():
            max_distance = -1
            max_clazz = None
            for clazz in clazz_list[1:]:
                try:
                    a_list = []
                    b_list = []
                    for word in case:
                        attr = word_attrs.get(word, 'n')
                        if attr == 'n' or attr == 'v':
                            a_list.append(word)
                        elif attr == 'a':
                            b_list.append(word)
                    #a_list = a_list + clazz_list[0]

                    top_similar = model.most_similar(positive=a_list, topn=1)
                    if not top_similar is None and len(top_similar) == 1:
                        b_list.append(top_similar[0][0])
                        tmp = [] + case
                        tmp.append(top_similar[0][0])
                        print(clazz_list[0][0] + "    " + ("@ ".join(tmp)) + "    " + ("@ ".join(b_list)))
                        x = model.n_similarity(tmp, clazz)
                    else:
                        print("empty clazz %s " % clazz_name)
                except ReferenceError:
                    print("error!")
                    continue
                if isinstance(x, numpy.float64) and x > max_distance:
                    max_distance = x
                    max_clazz = clazz
                else:
                    #print("bad value!" + str(x) + "\t" + "#".join(clazz) + "\t\t" + "#".join(case))
                    pass
            if not max_clazz is None:
                top_list.append([max_distance, clazz_name, '#'.join(max_clazz), '#'.join(case)])

        top_list = sorted(top_list, key=lambda i: i[0], reverse=False)
        for item in top_list:
            #print(str(item[0]) + "\t" + item[1] + "\t\t" + item[2] + "\t\t" + item[3])
            print(str(item[0]) + "\t\t" + item[2] + "\t\t" + item[3])
        print("done")

def test_word_distance():
    w1 = u'磨脚'
    w2 = u'薄'
    model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/all_tmall_comments.bin', binary=True)
    x = model.similarity(w1, w2)
    print(x)

def test_english():
    model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/vectors_text8.bin', binary=True)
    x1 = 'the cat is walking in the bedroom'
    x2 = 'a dog was running in a room'
    x3 = 'an apple jumped over a river'
    distance = model.n_similarity(x1.split(), x2.split())
    print(distance)
    distance = model.n_similarity(x1.split(), x3.split())
    print(distance)

def test_chinese(x1, x2):
    model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/all_tmall_comments.bin', binary=True)
    word_attrs = load_word_attr('/users/erwin/tmp/words_attr.txt')

    #x1 = u'味道'
    #x2 = u'苦味'
    l1 = []
    l2 = []
    for i in jieba.cut(x1, cut_all=False):
        l1.append(i)
    for i in jieba.cut(x2, cut_all=False):
        l2.append(i)
    print('#'.join(l1))
    print('#'.join(l2))
    distance = model.n_similarity(l1, l2)
    print('distance', distance)


def clazz_n_similar(model=None, clazz_list=[], topn=30):
    clazz_like = {}
    for clazz in clazz_list:
        try:
            tmp = model.most_similar(positive=[clazz], topn=topn)
        except:
            continue
        like_lst = {clazz: 1}  # add self word
        for pair in tmp:
            #like_lst.append(pair[0])
            like_lst[pair[0]] = 1
        clazz_like[clazz] = like_lst
    return clazz_like


model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/all_tmall_comments.bin', binary=True)
word_attrs = load_word_attr('/users/erwin/tmp/words_attr.txt')
clazz_map = load_clazz2('/Users/erwin/tmp/clothes_clazz')
clazz_set = {}
clazz_list = []
for (clazz_name, clazz_value) in clazz_map.items():
    clazz_set[clazz_value[0][0]] = 1
    clazz_list.append(clazz_value[0][0])
clazz_simi = clazz_n_similar(model, clazz_list, topn=20)


def test_get_main_word(s):
    case1 = []
    case2 = []
    case2type = []
    most_like = {}
    orig_cut = []
    for i in jieba.cut(s, cut_all=False):
        orig_cut.append(i)
        type_set = word_attrs.get(i, None)
        if i in clazz_set:
            most_like[i] = 1
        if not type_set is None and ('c' in type_set or 'p' in type_set):
            continue
        if type_set is None or 'n' in type_set or 'v' in type_set:
            case1.append(i)
            case2type.append(i+'_nv')
        if not type_set is None and 'a' in type_set:
            case2.append(i)
            case2type.append(i+"_a")
    print("# ".join(orig_cut))
    x1 = []
    x2 = []
    if len(case1) > 0:
        x1 = model.most_similar(positive=case1, topn=20)
    if len(case2) > 0:
        x2 = model.most_similar(positive=case2, topn=10)
    lst = []
    for i in x1:
        lst.append(i[0])
    for i in x2:
        lst.append(i[0])

    print("# ".join(case2type))

    for i in lst:
        for (clazz_name, clazzes) in clazz_simi.items():
            if i in clazzes:
                count = most_like.get(clazz_name, 0)
                most_like[clazz_name] = count + 1
    print("n_similar " + "@ ".join(lst))

    xx = []
    for (clazz, count) in most_like.items():
        xx.append(clazz + '_' + str(count))
    print('most_like ' + "@ ".join(xx))

if __name__ == '__main__':
    '''
    while True:
        s1 = sys.stdin.readline().strip()
        s2 = sys.stdin.readline().strip()
        test_chinese(s1, s2)

    '''
    while True:
        s = sys.stdin.readline()
        s = s.strip()
        try:
            test_get_main_word(s)
        except KeyError:
            print("error")
            continue

    #test()
    #test_word_distance()
    #test_english()