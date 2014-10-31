__author__ = 'erwin'
#coding=utf-8

from gensim.models import word2vec
import codecs

class EmotionDict:
    def __init__(self):
        self.dict_path = '/Users/erwin/tmp/emotion.dict'
        self.word2vec_bin = '/Users/erwin/svn/word2vec/all_tmall_comments.bin'
        self.model = word2vec.Word2Vec.load_word2vec_format(self.word2vec_bin, binary=True)

    def get_by_seed(self, word, cur_depth=0, max_depth=2):
        cur_list = []
        cur_tmp = self.model.most_similar(positive=[word], topn=20)
        for k, v in cur_tmp:
            cur_list.append(k)
        cur_tmp = None
        if cur_depth < max_depth:
            more_list = []
            for x in cur_list:
                more_list += self.get_by_seed(x, cur_depth+1, max_depth)
            cur_list += more_list
        return cur_list

    def generate_by_seed(self, good_seed=[], bad_seed=[], good_depth=2, bad_depth=1):
        dict_out = codecs.open(self.dict_path, 'w', encoding='UTF-8')
        good_set = {}
        bad_set = {}
        for word in good_seed:
            lst = self.get_by_seed(word, cur_depth=0, max_depth=good_depth)
            for x in lst:
                if x in good_set:
                    continue
                dict_out.write("1 %s\n" % x)
                good_set[x] = 1
        for word in bad_seed:
            lst = self.get_by_seed(word, cur_depth=0, max_depth=bad_depth)
            for x in lst:
                if x in bad_set:
                    continue
                dict_out.write("0 %s\n" % x)
                bad_set[x] = 1
        dict_out.close()


if __name__ == '__main__':
    emotion_dict = EmotionDict()
    good_seed = [u'好']
    bad_seed = [u'一般', u'垃圾']
    emotion_dict.generate_by_seed(good_seed, bad_seed, good_depth=2, bad_depth=1)