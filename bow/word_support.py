__author__ = 'erwin'
#coding=utf-8

import codecs
import jieba
import jieba.posseg as pseg
import sys
import pickle
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
                                   u'不错', u'赞', u'差', u'挺好', u'还好'])

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
        fin = codecs.open('/Users/erwin/work/comment_labeled/part_of_comments3', 'r', encoding='utf-8')
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
        find similative tags
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

if __name__ == '__main__':
    word_support = WordSupport()
    word_support.train()
    word_support.debug()
    #word_support.find_relative()


