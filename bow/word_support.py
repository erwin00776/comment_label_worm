__author__ = 'erwin'
#coding=utf-8

import codecs
import math
import sys
import pickle

import jieba
import jieba.posseg as pseg
import numpy as np

sys.path.append('..')
import mass_dict

mass_dict = mass_dict.Dict(lazy_load=False)

# Ontology

class WordSupport:
    def __init__(self, train_set='', test_set=''):
        self.train_set = train_set
        self.test_set = test_set
        self.support = {}
        self.revert_support = {}
        self.word_blacklist = set([u'好', u'一般', u'说', u'看', u'喜欢', u'蛮好', u'还行',
                                   u'不错', u'赞', u'差', u'挺好', u'还好', u'太次'])
        self.word_count = {}
        self.doc_word_count = {}

        self.tmp_file_name = '/tmp/word_support.tmp'

    @staticmethod
    def _add_support(s, w1, w2):
        w_set = s.get(w1, None)
        if w_set is None:
            w_set = {w2: 1}
            s[w1] = w_set
        else:
            w = w_set.get(w2, None)
            if w is None:
                w_set[w2] = 1
            else:
                w_set[w2] += 1

    def __dump__(self):
        fout = open(self.tmp_file_name, 'wb')
        pickle.dump(self.support, fout)
        pickle.dump(self.revert_support, fout)
        fout.close()
        print("save to tmp cache %s done." % self.tmp_file_name)

    def __load__(self):
        import os
        if os.path.exists(self.tmp_file_name):
            fin = open(self.tmp_file_name, 'rb')
            self.support = pickle.load(fin)
            self.revert_support = pickle.load(fin)
            fin.close()
        if not self.support is None and not self.revert_support is None and \
                len(self.support) > 0 and len(self.revert_support) > 0:
            print("load from tmp cache: %s done." % self.tmp_file_name)
            return True
        return False


    def add_support(self, w1, w2):
        if w1 in self.word_blacklist or w2 in self.word_blacklist:
            return
        self._add_support(self.support, w1, w2)
        self._add_support(self.revert_support, w2, w1)

    def train(self):
        if self.__load__():
            return

        jieba.load_userdict(mass_dict.user_dict_path)
        #fin = codecs.open('/Users/erwin/work/comment_labeled/all_tmall_comments_clothes', 'r', encoding='utf-8')
        fin = codecs.open('/Users/erwin/work/comment_labeled/all_tmall_comments_cosmetic', 'r', encoding='utf-8')
        for line in fin.readlines():
            sel_words = []
            sel_flags = []
            tokens = pseg.cut(line)
            for t in tokens:
                if t.flag == 'a' or t.flag == 'n' or t.flag == 'v':
                    sel_words.append(t.word)
                    sel_flags.append(t.flag)
            flags = '_'.join(sel_flags)
            if flags == 'n_a' or flags == 'n_n' or flags == 'n_v':
                self.add_support(sel_words[0], sel_words[1])
            elif flags == 'n_n_a':
                self.add_support(sel_words[0], sel_words[1])
                self.add_support(sel_words[1], sel_words[2])
        fin.close()

        self.__dump__()

    def word_relation(self, word):
        pass

    def find_relative(self, alpha=0.66, beta=0.8, zeta=2):
        '''
        find similative tags: by document similative.
        find common tags
        '''
        support = {}
        for (k, wset) in self.support.items():
            s = set([])
            for (w, c) in wset.items():
                if c > 1:
                    s.add(w)
            support[k] = s

        similars = []
        common_tags = []
        for (k1, wset1) in support.items():
            diff_count = 0
            calc_count = 0
            for (k2, wset2) in support.items():
                if k1 == k2 or k2 > k1:
                    continue
                calc_count += 1
                tmp = wset1.intersection(wset2)
                if len(tmp) == 0 or len(wset1) <= 1 or len(wset2) <= 1:
                    continue
                r1 = len(tmp) * 1.0 / len(wset1)
                r2 = len(tmp) * 1.0 / len(wset2)

                if r1 > alpha or r2 > alpha:
                    similars.append([k1, k2])
                    print(k1 + '\t' + k2 + '\t' + str(r1) + '\t' + str(r2))

                    if r1 / r2 > zeta or r2 / r1 > zeta:
                        diff_count += 1
            if diff_count > 2 and calc_count * beta > diff_count:
                common_tags.append(k1)

        print("common tag support reasoning: ")
        for tag in common_tags:
            print("\t" + tag)

        common_set = set(common_tags)
        similar_groups = []
        for (w1, w2) in similars:
            if w1 in common_set or w2 in common_set:
                continue
            join = False
            for group in similar_groups:
                if w1 in group or w2 in group:
                    group.add(w1)
                    group.add(w2)
                    join = True
                    break
            if not join:
                similar_groups.append(set([w1, w2]))

        print("similar tag support reasoning: ")
        for group in similar_groups:
            print("\t" + " ".join(group))

    @staticmethod
    def doc_cosine(ws1, wc1, ws2, wc2, alpha=0.000001):
        words1 = set(ws1.keys())
        words2 = set(ws2.keys())
        words = words1.union(words2)
        p1 = []
        p2 = []
        if wc1 == 0 or wc2 == 0 or len(ws1) < 3 or len(ws2) < 3:
            return 0.0
        for word in words:
            p1.append(ws1.get(word, alpha) * 1.0 / wc1)
            p2.append(ws2.get(word, alpha) * 1.0 / wc2)
        if len(p1) == 0 or len(p2) == 0:
            return 0.0
        a = np.dot(p1, p2)
        b1 = math.sqrt(reduce(lambda b1, i: b1 + i,
                              map(lambda x: x*x, p1)))
        b2 = math.sqrt(reduce(lambda b2, i: b2 + i,
                              map(lambda x: x*x, p2)))
        '''
        print('-'.join(words1))
        print('-'.join(words2))
        print('-'.join(words))
        print(a, b1, b2)
        print(p1)
        print(p2)
        '''
        return a * 1.0 / (b1 * b2)

    def similarity(self):
        support = {}
        for (k, w_set) in self.support.items():
            doc_wc = 0
            ws = {}
            for (w, c) in w_set.items():
                if c > 1:
                    ws[w] = c
                    count = self.word_count.get(w, 0)
                    self.word_count[w] = count + c
                    doc_wc += c
            support[k] = ws
            self.doc_word_count[k] = doc_wc

        pairs = []
        for (k1, wset1) in support.items():
            for (k2, wset2) in support.items():
                if k1 == k2 or k1 > k2:
                    continue
                cos = self.doc_cosine(wset1, self.doc_word_count[k1],
                                      wset2, self.doc_word_count[k2])
                if cos > 0.66:
                    #print(k1 + "\t" + k2 + "\t" + str(cos))
                    pairs.append([k1, k2])
        similar_groups = []
        for (w1, w2) in pairs:
            join = False
            for group in similar_groups:
                if w1 in group or w2 in group:
                    group.add(w1)
                    group.add(w2)
                    join = True
                    break
            if not join:
                similar_groups.append(set([w1, w2]))

        print("similar tag support reasoning: ")
        for group in similar_groups:
            print("\t" + " ".join(group))


    def debug(self):
        # output support relations
        for (k, w_set) in self.support.items():
            if len(w_set) > 1:
                fathers = []
                for (w, c) in self.revert_support.get(k, {}).items():
                    if c > 1 and w != k and not w in w_set:
                        fathers.append(w)
                print(k + "\t" + "-".join(fathers))
                for (w, c) in w_set.items():
                    if c > 1:
                        print("\t" + w + "\t\t" + str(c))

    def find_fathers(self):
        '''
        find the common words.
        '''
        father_support = {}
        for (k, wset) in self.support.items():
            if len(wset) > 1:
                fathers = []
                for (w, c) in self.revert_support.get(k, {}).items():
                    if c > 1 and w != k and not w in wset:
                        fathers.append(w)
                for f in fathers:
                    count = father_support.get(f, 0)
                    father_support[f] = count + 1

        x = sorted(father_support.items(), key=lambda (f, c): c, reverse=True)
        print('fathers: ')
        for (f, c) in x:
            if c > 1:
                print(f + "\t" + str(c))
        return father_support.keys()

    def find_common_supportor(self):
        supporter = {}
        for (k, wset) in self.revert_support.items():
            if len(wset) > 1:
                supporter[k] = len(wset)
        x = sorted(supporter.items(), key=lambda (k, c): c, reverse=True)
        print('sons: ')
        for (k, c) in x:
            if k in self.support:
                continue
            print(k + "\t" + str(c))
        return supporter.keys()

    def diff_father_son(self):
        fathers = set(self.find_fathers())
        sons = set(self.find_common_supportor())
        same = fathers.intersection(sons)
        for f in fathers.difference(same):
            print("\t f: " + f)
        for s in sons.difference(same):
            print("\t s: " + s)

if __name__ == '__main__':
    word_support = WordSupport()
    word_support.train()
    #word_support.debug()
    #word_support.find_relative()
    #word_support.similarity()
    #word_support.find_fathers()
    word_support.find_common_supportor()
    #word_support.diff_father_son()


