__author__ = 'erwin'
#coding=utf-8

from gensim.models import word2vec
import os
import codecs
import pickle


labels = [
    u"退",
    u"整体",
    u"发货",
    u"会",
    u"紧身",
    u"划算",
    u"肚腩",
    u"太胖",
    u"一般",
    u"贴身",
    u"手感",
    u"惊喜",
    u"弹性",
    u"涨价",
    u"大小",
    u"赞",
    u"态度",
    u"灰",
    u"超赞",
    u"全",
    u"时候",
    u"店",
    u"深灰色",
    u"外套",
    u"姐姐",
    u"订",
    u"是",
    u"一分货",
    u"样子",
    u"保暖",
    u"给力",
    u"廉价",
    u"还好",
    u"不错",
    u"女朋友",
    u"大家",
    u"价格",
    u"款式",
    u"色差",
    u"领子",
    u"差评",
    u"正合适",
    u"满意",
    u"超值",
    u"码",
    u"适合",
    u"身高",
    u"太慢",
    u"总体",
    u"打底",
    u"款型",
    u"人",
    u"老板",
    u"厚实",
    u"还行",
    u"给我发",
    u"胖",
    u"严重",
    u"好评",
    u"领口",
    u"评论",
    u"图片/好看",
    u"老",
    u"合适",
    u"肚子",
    u"东西",
    u"到",
    u"值",
    u"效果",
    u"重",
    u"慢",
    u"衣服",
    u"料",
    u"赘肉",
    u"纯棉",
    u"有",
    u"小",
    u"底裤",
    u"催",
    u"贵",
    u"开心",
    u"手",
    u"问题",
    u"便宜",
    u"变形",
    u"弹力",
    u"小肚子",
    u"好",
    u"不会",
    u"妈妈",
    u"裙子",
    u"显瘦",
    u"购物",
    u"冷",
    u"卖家",
    u"偏长",
    u"版型",
    u"有点",
    u"薄",
    u"性价比",
    u"大",
    u"同事",
    u"店家",
    u"建议",
    u"布料",
    u"上半身",
    u"料子",
    u"没穿",
    u"很漂亮",
    u"天",
    u"长",
    u"裙摆",
    u"收到",
    u"粘毛",
    u"身材",
    u"掉色",
    u"尺码",
    u"面料",
    u"知道",
    u"挺厚",
    u"很棒",
    u"舒服",
    u"瘦身",
    u"质感",
    u"短",
    u"想",
    u"价",
    u"想象",
    u"老婆",
    u"宝贝",
    u"厚",
    u"颜色",
    u"朋友",
    u"合身",
    u"质量",
    u"没洗",
    u"体验",
    u"评价",
    u"起来",
    u"暖和",
    u"样式",
    u"季节",
    u"蛮厚",
    u"太小",
    u"异味",
    u"店铺",
    u"穿",
    u"衣衣",
    u"柔软",
    u"不能",
    u"帮别人",
    u"没",
    u"好看",
    u"图片",
    u"朋友/买",
    u"妹妹",
    u"同事/买",
    u"感觉",
    u"裙",
    u"应该",
    u"做工",
    u"价钱",
    u"味道",
    u"绒",
    u"不值",
    u"货",
    u"很好",
    u"显胖",
    u"说",
    u"不好意思",
    u"码数",
    u"漂亮",
    u"天气",
    u"肉",
    u"同学",
    u"试穿",
    u"黑色",
    u"舒适",
    u"挺好",
    u"描述",
    u"价位",
    u"买",
    u"觉得",
    u"没有",
    u"物流",
    u"穿着",
    u"准备",
    u"高",
    u"修身",
    u"喜欢",
    u"腰身",
    u"很厚",
    u"减肥",
    u"快递",
    u"正好",
    u"瘦",
    u"购买",
    u"上身",
    u"速度",
    u"热情",
    u"下次",
    u"线头",
    u"气味",
    u"褪色",
    u"商品",
    u"呵呵",
    u"快",
    u"看",
    u"洗",
    u"网购",
    u"客服",
    u"起球",
    u"紧",
    u"儿",
    u"拍",
    u"体重",
    u"图",
]


class LabelClusters:
    '''
    把标签通过词相似形自动聚类起来
    '''
    def __init__(self):
        self.model = word2vec.Word2Vec.load_word2vec_format('/Users/erwin/svn/word2vec/all_tmall_comments.bin',
                                                            binary=True)
        self.label_relations = []
        self.prepare()

    def prepare(self):
        tmp_model_name = "/tmp/label_clusters.dat"
        if os.path.exists(tmp_model_name):
            fin = open(tmp_model_name, 'rb')
            self.label_relations = pickle.load(fin)
            fin.close()
            print("load from " + tmp_model_name + " done")
            return

        for label in labels:
            try:
                relations = self.model.most_similar(positive=[label], topn=10)
                words = []
                for (word, sim) in relations:
                    words.append(word)
                self.label_relations.append([label, words])
            except KeyError:
                continue
        fout = open(tmp_model_name, 'wb')
        pickle.dump(self.label_relations, fout)
        fout.close()

    def color(self, clusters):
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
                    sim = self.model.n_similarity(ws1, ws2)
                except ValueError:
                    continue
                if max_sim < sim:
                    max_label = lbl2
                    max_sim = sim
            if not max_label is None:
                rel_pair = clusters.get(lbl1, None)
                if rel_pair is None or rel_pair[1] < max_sim:
                    clusters[lbl1] = [max_label, max_sim]
                rel_pair = clusters.get(max_label, None)
                if rel_pair is None or rel_pair[1] < max_sim:
                    clusters[max_label] = [lbl1, max_sim]
                #print(lbl1 + "\t\t" + max_label + "\t\t" + str(max_sim))
            else:
                print("error!" + lbl1 + "\t\t" + str(max_sim))
        for (k, v) in clusters.items():
            if k <= v[0]:
                print(k + "\t" + v[0] + "\t" + str(v[1]))

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
            if not max_sim is None:
                color_sim_max[i] = [max_index, max_sim]
                rel_sim = color_sim_max.get(max_index, None)
                if rel_sim is None or rel_sim[1] < max_sim:
                    color_sim_max[max_index] = [i, max_sim]
        for (idx, pair) in color_sim_max.items():
            if idx < pair[0]:
                print(str(pair[1]) + "\t\t"
                      + '#'.join(color_groups[idx])
                      + "\t\t" + '#'.join(color_groups[pair[0]])
                    )

if __name__ == '__main__':
    label_clusters = LabelClusters()
    #label_clusters.cluster()