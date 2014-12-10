__author__ = 'erwin'
#coding=utf-8

from gensim.models import word2vec
import os
import codecs
import pickle

import sys
sys.path.append('..')
import mass_dict

mass_dict = mass_dict.Dict(lazy_load=False)


class LabelClusters:
    '''
    把标签通过词相似形自动聚类起来
    '''
    def __init__(self):
        # self.model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/all_tmall_comments.bin',
        #                                                    binary=True)
        self.model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/clothes.bin',
                                                            binary=True)
        self.label_relations = []
        self.cluster_sims = {}
        self.lables_count = {}
        self.prepare()

    def load_labels_from_file(self):
        file_name = '/Users/erwin/work/comment_labeled/labels'
        fin_labels = codecs.open(file_name, 'r', encoding='utf-8')
        labels_vec = []
        for line in fin_labels.readlines():
            line = line.rstrip()
            pair = line.split()
            labels_vec.append(pair[0])
            self.lables_count[pair[0]] = int(pair[1])
        return labels_vec

    def prepare(self):
        tmp_model_words = "/tmp/label_clusters.dat"
        tmp_model_sim = "/tmp/label_clusters.sim"

        # load label to words.
        if os.path.exists(tmp_model_words):
            fin = open(tmp_model_words, 'rb')
            self.label_relations = pickle.load(fin)
            fin.close()
            print("load from " + tmp_model_words + " done.")
        else:
            labels = self.load_labels_from_file()
            for label in labels:
                try:
                    relations = self.model.most_similar(positive=[label], topn=10)
                    words = []
                    for (word, sim) in relations:
                        words.append(word)
                    self.label_relations.append([label, words])
                except KeyError:
                    continue
            fout = open(tmp_model_words, 'wb')
            pickle.dump(self.label_relations, fout)
            fout.close()
            print("dump " + tmp_model_words + " done.")

        # load label similarity distances matrix.
        if os.path.exists(tmp_model_sim):
            fin = open(tmp_model_sim, 'rb')
            self.cluster_sims = pickle.load(fin)
            fin.close()
            print("load from " + tmp_model_sim + " done.")
        else:
            for i in range(0, len(self.label_relations)-1):
                lbl1 = self.label_relations[i][0]
                ws1 = self.label_relations[i][1]
                for j in range(i+1, len(self.label_relations)):
                    lbl2 = self.label_relations[j][0]
                    ws2 = self.label_relations[j][1]
                    try:
                        sim = self.model.n_similarity(ws1, ws2)
                    except ValueError:
                        continue
                    x = self.cluster_sims.get(i, {})
                    x[j] = sim
                    self.cluster_sims[i] = x
                    y = self.cluster_sims.get(j, {})
                    y[i] = sim
                    self.cluster_sims[j] = y
            fout = open(tmp_model_sim, 'wb')
            pickle.dump(self.cluster_sims, fout)
            fout.close()
            print("dump " + tmp_model_sim + " done.")

    @staticmethod
    def color(clusters):
        print('begin color')
        color_groups = []
        color = 0
        colored_set = {}
        for (k, v) in clusters.items():
            if k in colored_set:
                continue
            if v[0] in colored_set:
                color_id = colored_set[v[0]]
                colored_set[k] = color_id
                color_groups[color_id].add(k)
                continue
            group = set([])
            lst = [k]
            while len(lst) != 0:
                label = lst.pop()
                group.add(label)
                colored_set[label] = color
                if not v[0] in colored_set:
                    lst.append(v[0])
            color_groups.append(group)
            color += 1

        print(len(color_groups))
        for g in color_groups:
            print("\t".join(g))

        return color_groups

    def cluster_knn(self, k=0.7, alpha=0.667):
        groups = [[0]]
        for i in range(1, len(self.label_relations)):
            max_sims = None
            max_index = None
            for p in range(0, len(groups)):
                sims = []
                for q in range(0, len(groups[p])):
                    if self.cluster_sims[i][groups[p][q]] > alpha:
                        sims.append(self.cluster_sims[i][groups[p][q]])
                if len(sims) < k*len(groups[p]):
                    continue
                avg_sims = reduce(lambda x, sum_sims: sum_sims + x, sims, 0) / len(sims)
                if avg_sims > max_sims:
                    max_sims = avg_sims
                    max_index = p
            if max_index is None:
                groups.append([i])
            else:
                groups[max_index].append(i)
        for i in range(0, len(groups)):
            words = []
            for j in range(0, len(groups[i])):
                word_rel = self.label_relations[groups[i][j]]
                words.append(word_rel[0])
            print('#'.join(words))

    def cluster(self):
        # 1) filter unuseful label
        # 2) converge
        clusters = {}

        for i in range(0, len(self.label_relations)-1):
            lbl1 = self.label_relations[i][0]
            ws1 = self.label_relations[i][1]
            max_sim = -999999
            max_label = None
            for j in range(i+1, len(self.label_relations)):
                lbl2 = self.label_relations[j][0]
                ws2 = self.label_relations[j][1]
                try:
                    sim = self.cluster_sims[i][j]
                except ValueError:
                    continue
                if max_sim < sim:
                    max_label = lbl2
                    max_sim = sim
            if max_label is not None:

                rel_pair = clusters.get(lbl1, None)
                if rel_pair is None or rel_pair[1] < max_sim:
                    clusters[lbl1] = [max_label, max_sim]
                rel_pair = clusters.get(max_label, None)
                if rel_pair is None or rel_pair[1] < max_sim:
                    clusters[max_label] = [lbl1, max_sim]
                # print(lbl1 + "\t\t" + max_label + "\t\t" + str(max_sim))
            else:
                print("error!" + lbl1 + "\t\t" + str(max_sim))
        for (k, v) in clusters.items():
            poc_lbl1 = ''.join(list(mass_dict.word_attrs.get(k, "")))
            poc_lbl2 = ''.join(list(mass_dict.word_attrs.get(v[0], "")))
            print(k + " " + poc_lbl1 + "\t" + v[0] + " " + poc_lbl2 + "\t" + str(v[1]))

        # 合并color相似的group
        color_groups = self.color(clusters)
        color_sim_max = {}
        for i in range(0, len(color_groups)-1):
            max_sim = None
            max_index = 0
            for j in range(i+1, len(color_groups)):
                sim = self.model.n_similarity(color_groups[i], color_groups[j])
                if max_sim is None or max_sim < sim:
                    max_sim = sim
                    max_index = j
            # max_sim = None
            if max_sim is not None:
                color_sim_max[i] = [max_index, max_sim]
                rel_sim = color_sim_max.get(max_index, None)
                if (rel_sim is None or rel_sim[1] < max_sim) and max_sim > 0.6:
                    color_sim_max[max_index] = [i, max_sim]

        for (idx, pair) in color_sim_max.items():
            if idx < pair[0] and pair[1] > 0.4:
                print(str(pair[1]) + "\t\t"
                      + '#'.join(color_groups[idx])
                      # + "\t\t" + '#'.join(color_groups[pair[0]]))
                      + "#" + '#'.join(color_groups[pair[0]]))

if __name__ == '__main__':
    label_clusters = LabelClusters()
    label_clusters.cluster()
    # label_clusters.cluster_knn(alpha=0.5)
