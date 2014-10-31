__author__ = 'erwin'
#coding=utf-8

import gensim
import codecs
import jieba
import logging
import sys
sys.path.append('..')
import mass_dict

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
mass_dict = mass_dict.Dict(lazy_load=False)

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

#word_attrs = load_word_attr('/users/erwin/tmp/words_attr.txt')

def tokenize(sentencs):
    tokens = jieba.cut(sentencs, cut_all=False)
    l = []
    for t in tokens:
        types = mass_dict.word_attrs.get(t, None)
        if types is None or 'd' in types or 'y' in types:
            continue
        if not types is None and ('a' in types or 'n' in types or 'v' in types):
            l.append(t)
    return l


def hallo():
    fin = codecs.open('/Users/erwin/work/comment_labeled/part_of_comments', 'r', encoding='utf-8')
    lines = fin.readlines()
    words = []
    for line in lines:
        line = line.strip()
        words.append(tokenize(line))
    fin.close()

    dic = gensim.corpora.Dictionary(words)
    for (word, index) in dic.token2id.iteritems():
        print('word2index ' + word + "\t" + str(index))

    corpus = [dic.doc2bow(text) for text in words]

    # 分词然后向量化
    query_str = "合身"
    query = [dic.doc2bow(tokenize(query_str))]
    print(query)

    tfids = gensim.models.TfidfModel(corpus=corpus)
    for doc in tfids[corpus[16]]:
        print(doc)

    lsi_model = gensim.models.LsiModel(corpus=corpus, id2word=dic, num_topics=100)
    lsi_model.show_topics(10)

    # 建立相似矩阵
    index = gensim.similarities.MatrixSimilarity(lsi_model[corpus])
    query_lsi = lsi_model[query[0]]
    print('query_lsi', query_lsi)
    # 跟语料库里面的每个doc都计算相近距离
    lsi_sims = index[query_lsi]
    sort_sims = sorted(enumerate(lsi_sims), key=lambda item: -item[1])
    print(list(enumerate(lsi_sims)))
    for i in range(0, len(sort_sims)):
        if i > 20:
            break
        #print(sort_sims[i])
        doc_index, doc_sim = sort_sims[i]
        print(str(doc_index) + "\t" + str(doc_sim) + "\t" + lines[doc_index])

    '''
    logging.info("print lda")
    lda_model = gensim.models.LdaModel(corpus=corpus, id2word=dic, num_topics=100)
    lda_model.print_topics(10)
    index = gensim.similarities.MatrixSimilarity(lda_model[corpus])
    query_lda = lda_model[query[0]]
    lda_sims = index[query_lda]
    sort_sims = sorted(enumerate(lda_sims), key=lambda item: -item[1])
    for i in range(0, len(sort_sims)):
        if i > 20:
            break
        doc_index, doc_sim = sort_sims[i]
        print(str(doc_index) + "\t" + str(doc_sim) + "\t" + lines[doc_index])
    '''


if __name__ == '__main__':
    hallo()


