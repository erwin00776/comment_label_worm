__author__ = 'erwin'
#coding=utf-8

import jieba
from gensim.models import word2vec
import numpy
import codecs
import os

def test_load_model():
    model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/vectors_text8.bin', binary=True)

    # find similar relation ship
    x = model.most_similar(['son', 'father'], ['daughter'], topn=3)
    print(x)
    # calc cosine similarity between two words
    y = model.similarity('asia', 'china')
    print(y)

    z = model.most_similar(['china'])
    print(z)


class_list = [u'款式', u'尺码', u'材料', u'性价比', u'舒服', u'味道大']
def load_model():
    clazz_map = {}
    model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/all_tmall_comments.bin', binary=True)
    for clazz in class_list:
        print(clazz)
        try:
            similar_list = model.most_similar([clazz], topn=50)
            clazz_map[clazz] = similar_list
        except KeyError:
            pass
    return (model, clazz_map)

def test_classify():
    '''
    直接把短句子分词，然后用word2vec跟每个标签算距离
    '''
    model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/all_tmall_comments.bin', binary=True)
    clazz_list = load_clazz('/Users/erwin/tmp/shoe_clazz')

    test_case = '/Users/erwin/tmp/xx'
    test_case = "/users/erwin/tmp/tmall_comments_shoes_37085498315_444339490.parsed"
    fin = codecs.open(test_case, 'r', encoding='utf-8')
    for line in fin.readlines():
        line = line.strip()
        short_sentences = get_short_sentences(line)

        max_distance = -1
        max_clazz_index = -1
        max_short = []
        for short in short_sentences:
            seg_list = jieba.cut(short, cut_all=False)
            clazz_index = -1
            short_list = []
            for word in seg_list:
                short_list.append(word)
            for clazz in clazz_list:
                try:
                    clazz_index += 1
                    distance = model.n_similarity(short_list, clazz)
                    if type(distance) == numpy.float64:
                        if distance > max_distance:
                            max_distance = distance
                            max_clazz_index = clazz_index
                            max_short = short_list
                    elif type(distance) == numpy.ndarray:
                        if any(distance) > max_distance:
                            max_distance = max(distance)
                            max_clazz_index = clazz_index
                            max_short = short_list
                except KeyError:
                    pass
            print("\t" + ''.join(clazz_list[max_clazz_index]) + "\t" + short + "\t\t" + str(max_distance))

        if max_clazz_index > -1:
            print("## " + ''.join(clazz_list[max_clazz_index]) + "\t" + ''.join(max_short))
        else:
            print("## no clazz")
        print(line)

    fin.close()


def get_top2_classify():
    '''
    直接对每个短句子分词，然后和每个标签背后的正规化的标签组进行cosine距离计算；
    '''
    model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/all_tmall_comments.bin', binary=True)
    #clazz_list = load_clazz('/Users/erwin/tmp/shoe_clazz')
    clazz_map = load_clazz2('/Users/erwin/tmp/make-up_clazz')

    test_case = "/users/erwin/svn/tmall_comments_shoes_37085498315_444339490.parsed"
    test_case = "/Users/erwin/tmp/all_tmall_comments_make-up"
    fin = codecs.open(test_case, 'r', encoding='utf-8')
    for line in fin.readlines():
        line = line.strip()
        short_sentences = get_short_sentences(line)

        top2 = []
        for short in short_sentences:
            seg_list = jieba.cut(short, cut_all=False)

            short_list = []
            for word in seg_list:
                short_list.append(word)

            max_distance = -1
            max_clazz = None
            for (clazz_name, clazz_list) in clazz_map.items():
                for clazz in clazz_list:
                    try:
                        x = model.n_similarity(short_list, clazz)
                    except:
                        continue
                    if isinstance(x, numpy.float64) and x > max_distance:
                        max_distance = x
                        max_clazz = clazz
                    else:
                        #print("bad value!" + str(x) + "\t" + "#".join(clazz) + "\t\t" + "#".join(short_list))
                        pass
            if not max_clazz is None:
                top2.append([max_distance, '' + clazz_name, '#'.join(max_clazz), '#'.join(short_list)])

        top2 = sorted(top2, key=lambda i: i[0], reverse=True)
        print(line)
        for i in range(0, len(top2)):
            if top2[i][0] < 0.3 or i > 3:
                break
            print("\t" + str(top2[i][0]) + "\t" + top2[i][2] + "\t\t" + top2[i][3])

    fin.close()


def test():
    model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/all_tmall_comments.bin', binary=True)
    x = model.most_similar([u'偏大'], [u'问题', u'尺码'], topn=3)
    case = [u'质量', u'尺码', u'合适', u'没有', u'气味', u'好评']
    case = [u'外观', u'好看']
    clazzs = [[u'鞋子', u'没有', u'怪味'],
              [u'色泽', u'不错'],
              [u'材质', u'一般'],
              [u'款色', u'漂亮']
                ]
    for clazz in clazzs:
        x = model.n_similarity(case, clazz)
        print(x)


def load_clazz(file_path):
    '''
    clazz, 标签背后应该有另一个比较正式的:
    例如："要留意尺码问题" 应该实际关联的是 "尺码偏大" 和 "尺码偏小"
    '''
    fin = open(file_path, 'r')
    clazz_list = []
    for line in fin.readlines():
        line = line.strip()
        seg_list = jieba.cut(line, cut_all=False)
        tmp = []
        for word in seg_list:
            tmp.append(word)
        clazz_list.append(tmp)
    fin.close()
    return clazz_list


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


def get_short_sentences(sentence,
                        splitters=[
                            u' ', u'，', u'。', u'；', u'！', u'、', u'：', u'　'
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


def to_each_sentences():
    fin = codecs.open(os.path.join("/users/erwin/tmp/makeup", "all_makeup"), 'r', encoding='utf-8')
    fout = codecs.open(os.path.join("/users/erwin/tmp", "make-up"), 'w', encoding='utf-8')
    for line in fin.readlines():
        line = line.strip()
        sentences = get_short_sentences(line)
        for s in sentences:
            words = []
            iter = jieba.cut(s, cut_all=False)
            for w in iter:
                words.append(w)
            fout.write(' '.join(words))
            fout.write("\n")
    fout.close()
    fin.close()


if __name__ == '__main__':
    #test_load_model()
    #load_model()
    #test_classify()
    get_top2_classify()
    #to_each_sentences()
    #test()