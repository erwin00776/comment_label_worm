__author__ = 'erwin'
#coding=utf-8

import math
'''
@Name: Bag of Word
@Brief: determine emotions.
@Reference: http://blog.csdn.net/lingerlanlan/article/details/38418277
'''


class Dict:
    def __init__(self, path):
        self.word2index = {}
        self.word2count = {}
        self.index2word = []
        self.load_dict(path)

    def load_dict(self, path):
        fin = open(path, 'r')
        index = 0
        for line in fin.readlines():
            line = line.strip()
            for word in line.split():
                if word in self.word2count:
                    self.word2count[word] += 1
                else:
                    self.word2count[word] = 1
                    self.word2index[word] = index
                    self.index2word.append(word)
                    index += 1
        fin.close()


class BowModel:
    def __init__(self, all_path, good_path, bad_path):
        self.dict = Dict(all_path)
        self.good_mat = self.generateFeature(good_path)
        self.bad_mat = self.generateFeature(bad_path)
        self.good_path = good_path
        self.bad_path = bad_path
        self.train()
        self.dump()

    def docFeature(self, line, base=0):
        feature = [base] * len(self.dict.word2index)
        for word in line.split():
            if word in self.dict.word2index:
                feature[self.dict.word2index[word]] += 1
        return feature

    def generateFeature(self, path):
        fin = open(path, 'r')
        matrix = []
        for line in fin.readlines():
            feature = self.docFeature(line, base=1)
            matrix.append(feature)
        fin.close()
        return matrix

    def normMatrix(self, mat):
        mat1 = []
        for i in range(0, len(mat)):
            mat1.append(self.normVector(mat[i]))
        return mat1

    def normVector(self, vec):
        sum = 0
        sum = reduce(lambda i, sum: sum+i, map(lambda x: x*x, vec))
        sum = math.sqrt(sum)
        if sum == 0.0:
            return 0 * len(vec)
        v = map(lambda x: x*1.0/sum, vec)
        return v

    def distance(self, vec1, vec2):
        if len(vec1) != len(vec2):
            print("length not equal: [%d, %d]" % (len(vec1), len(vec2)))
        sum = 0
        for i in range(0, len(vec1)):
            sum += (vec1[i] - vec2[i])**2
        return sum

    def angle_cos(self, vec1, vec2):
        a = 0
        a = reduce(lambda i, a: a+i, map(lambda x,y: x*y, vec1, vec2))
        b1 = 0
        b2 = 0
        b1 = math.sqrt(reduce(lambda i, b1: b1+i, map(lambda x: x*x, vec1)))
        b2 = math.sqrt(reduce(lambda i, b2: b2+i, map(lambda x: x*x, vec2)))
        b = b1 + b2
        if b == 0:
            print(a, b, 0)
        else:
            print(a, b, a*1.0/b)

    def train(self):
        self.good_stardard = [0] * len(self.dict.word2index)
        self.bad_stardard = [0] * len(self.dict.word2index)
        for idx in range(0, len(self.good_mat)):
            self.good_stardard = map(lambda i, j: i+j, self.good_stardard, self.good_mat[idx])
        for idx in range(0, len(self.bad_mat)):
            self.bad_stardard = map(lambda i, j: i+j, self.bad_stardard, self.bad_mat[idx])

        len_good_mat = len(self.good_mat)
        len_bad_mat = len(self.bad_mat)
        self.good_stardard = map(lambda x: x*1.0/len_good_mat, self.good_stardard)
        self.bad_stardard = map(lambda x: x*1.0/len_bad_mat, self.bad_stardard)

    def dump(self):
        fout1 = open("/tmp/xx_good_mat", 'w')
        for j in range(0, len(self.good_stardard)):
            fout1.write("%0.6f\n" % self.good_stardard[j])
        fout1.close()

        fout1 = open("/tmp/xx_bad_mat", 'w')
        for j in range(0, len(self.bad_stardard)):
            fout1.write("%0.6f\n" % self.bad_stardard[j])
        fout1.close()

        fout = open("/tmp/xx_word2index", 'w')
        words = [''] * len(self.dict.word2index)
        for (k, v) in self.dict.word2index.items():
            words[v] = k
        for i in range(0, len(words)):
            fout.write("%s\n" % words[i])
        fout.close()

    def test(self):
        fin = open(self.good_path, 'r')
        count1 = 0
        error1 = 0
        for line in fin.readlines():
            line = line.strip()
            feature = self.normVector(self.docFeature(line))
            good_distance = self.distance(self.good_stardard, feature)
            bad_distance = self.distance(self.bad_stardard, feature)
            if good_distance > bad_distance:
                error1 += 1
            print("case %d %d" % (count1, good_distance-bad_distance))
            count1 += 1
        fin.close()

        fin = open(self.bad_path, 'r')
        count2 = 0
        error2 = 0
        for line in fin.readlines():
            line = line.strip()
            feature = self.normVector(self.docFeature(line))
            good_distance = self.distance(self.good_stardard, feature)
            bad_distance = self.distance(self.bad_stardard, feature)
            if good_distance < bad_distance:
                error2 += 1
            print("case %d %d" % (count2,  good_distance - bad_distance))
            count2 += 1
        fin.close()

        print(self.good_stardard)
        print(self.bad_stardard)
        print("good error rate: %f" % (error1*1.0/count1))
        print("bad error rate: %f" % (error2*1.0/count2))

    def detect(self, line):
        feature = self.normVector(self.docFeature(line))
        for i in range(0, len(feature)):
            if feature[i] > 0 and self.good_stardard[i] > 0:
                print('good %s %f' % (self.dict.index2word[i], self.good_stardard[i]))
            if feature[i] > 0 and self.bad_stardard[i] > 0:
                print('bad %s %f' % (self.dict.index2word[i], self.bad_stardard[i]))

        d1 = self.distance(feature, self.good_stardard)
        d2 = self.distance(feature, self.bad_stardard)
        print(d1, d2)



if __name__ == '__main__':
    path_prefix = '/users/erwin/tmp/jd_comments/'
    bow_model = BowModel(path_prefix+'all', path_prefix+'good', path_prefix+'bad')
    #bow_model.test()
    bow_model.detect("现在 的 洗衣机 咋 这么 单薄 的 很 不 皮实 甩干 人 不 拉住 就 跑 了 啥 东西 吗")

    bow_model.angle_cos([1, 0], [2, 2])
