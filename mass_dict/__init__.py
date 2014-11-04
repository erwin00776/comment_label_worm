__author__ = 'erwin'
#coding=utf-8
import codecs
import os


class Dict:
    def __init__(self, base_dir='/Users/erwin/work/comment_labeled/dict', lazy_load=True):
        self.base_dir = base_dir
        self.lazy_load = lazy_load
        self.user_dict_path = os.path.join(self.base_dir, 'userdict.txt')
        self.loaded = False

        self.word_attrs = {}
        self.stop_words = {}
        self.idf = {}
        if not lazy_load:
            self.init_dict()

    def init_dict(self):
        if self.loaded:
            return
        self.load_word_attr()
        self.load_stop_words()
        self.load_idf()
        self.loaded = True

    def load_word_attr(self):
        path_name = os.path.join(self.base_dir, 'words_attr.txt')
        fin = codecs.open(path_name, 'r', encoding='utf-8')
        for line in fin.readlines():
            line = line.strip()
            pair = line.split()
            types_vec = pair[1].split('-')
            types_set = set()
            for t in types_vec:
                types_set.add(t)
            self.word_attrs[pair[0]] = types_set
        fin.close()

    def load_stop_words(self):
        path_name = os.path.join(self.base_dir, 'words_attr.txt')
        fin = codecs.open(path_name, 'r', encoding='utf-8')
        for line in fin.readlines():
            line = line.rstrip()
            self.stop_words[line] = 1
        fin.close()

    def load_idf(self):
        path_name = '/Library/Python/2.7/site-packages/jieba/analyse/idf.txt'
        fin = codecs.open(path_name, 'r', encoding='utf-8')
        for line in fin.readlines():
            line = line.rstrip()
            w, idf = line.split()
            self.idf[w] = float(idf)
        fin.close()