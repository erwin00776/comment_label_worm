__author__ = 'erwin'


import math
import numpy
import scipy
from matplotlib import pyplot as plt
import pylab
import os


class MatrixBuilder:
    def __init__(self, path, stopword_path):
        self.path = path
        self.stopword_path = stopword_path
        self.stopwords = {}
        self.loadStopword()

        self.wordlist = {}
        self.doclist = {}
        self.wordCount = {}
        self.doc_wordcount = {}
        self.matrix = []

        self.id2doc = {}
        self.id2word = {}

    def loadStopword(self):
        fin = open(self.stopword_path)
        for w in fin.readlines():
            w = str(w)
            w = w.strip()
            self.stopwords[w.lower()] = 1
        fin.close()

    def createMatrix(self):
        self.loadStopword()
        self.createWordmap()

        self.matrix = []
        for i in range(self.word_count):
            self.matrix.append([])
            for j in range(self.doc_count):
                self.matrix[i].append(0)
        for i in range(self.doc_count):
            self.doc_wordcount[i] = 0

        word_index = 0;
        doc_index = 0;
        for fname in self.file_list:
            if fname == "." or fname == "..":
                continue
            fpath = os.path.join(self.path, fname)
            fin = open(fpath)
            for line in fin.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                line = line.replace(",", "").replace(".", "").replace(";", "").replace("-", " ").replace(":", " ")
                words = line.split()
                for word in words:
                    word = word.lower()
                    if word in self.stopwords:
                        continue
                    word_index = self.wordlist[word]
                    self.matrix[word_index][doc_index] = self.matrix[word_index][doc_index] + 1
                    self.doc_wordcount[doc_index] = self.doc_wordcount[doc_index] + 1
            doc_index = doc_index + 1


    def createWordmap(self):
        word_index = 0
        doc_index = 0

        self.file_list = os.listdir(self.path)
        for fname in self.file_list:
            if fname=="." or fname=="..":
                continue
            fpath = os.path.join(self.path, fname)

            fin = open(fpath)
            for line in fin.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                line = line.replace(",", "").replace(".", "").replace(";", "").replace("-", " ").replace(":", " ")
                words = line.split()
                for word in words:
                    word = word.lower()
                    if not word in self.stopwords and not word in self.wordlist:
                        #print(word, word_index)
                        self.wordlist[word] = word_index
                        self.id2word[word_index] = word
                        word_index = word_index + 1

            fin.close()

            self.doclist[fname] = doc_index
            self.id2doc[doc_index] = fname
            doc_index = doc_index+1

        self.word_count = word_index
        self.doc_count = doc_index

    def fixLen(self, s, n=16):
        if len(s) < n:
            for i in range(n-len(s)):
                s = s + ' '
        return s

    def getDocFreq(self, wordIndex):
        freq = 0
        for i in range(0, self.doc_count):
            if self.matrix[wordIndex][i]>0:
                freq = freq + 1
        return freq

    def calcTfIdf(self):
        for j in range(0, self.word_count):
            print("wordCount[%d]=%d" % (j, self.getDocFreq(j)))
        for word_index in range(0, self.word_count):
            for doc_index in range(0, self.doc_count):
                if self.matrix[word_index][doc_index]>0:
                    termfreq = 1.0 * self.matrix[word_index][doc_index] / self.doc_wordcount[doc_index]
                    idf = math.log((float)(self.doc_count)/self.getDocFreq(word_index))
                    print("%d %d=%f, %f %d %d" %
                          (word_index, doc_index, termfreq, idf, self.doc_count, self.getDocFreq(word_index)))
                    self.matrix[word_index][doc_index] = termfreq * idf

    def printMatrix(self):
        s = self.fixLen(' ')
        for i in range(self.doc_count):
            s = s + "\t" + self.id2doc[i]
        print(s)
        for i in range(self.word_count):
            s = self.fixLen(self.id2word[i])
            for j in range(self.doc_count):
                s = s + "\t" + str(self.matrix[i][j])
            print(s)



class MyLSA:
    def __init__(self, builder):
        self.LSA = 3
        self.builder = builder

    def calc(self):
        self.U, self.s, self.Vh = numpy.linalg.svd(self.builder.matrix)

        print("svd: U", self.U)
        print("svd: s", self.s)

    def query(self, q):
        self.calc()

        q = q.replace(",", "").replace(".", "").replace(";", "").replace("-", " ").replace(":", " ")
        q_tmp = q.split()
        q_vec = []
        for i in range(0, self.builder.word_count):
            q_vec.append(0)
        for word in q_tmp:
            if word in self.builder.wordlist:
                q_vec[self.builder.wordlist[word]] = q_vec[self.builder.wordlist[word]] + 1

        d_vec = []
        for i in range(0, self.LSA):
            sum = 0
            for j in range(0, self.builder.word_count):
                #sum = sum + q_vec[j] * self.builder.matrix[j][i]
                print("%d %d = %0.2f" % (i, j, self.U[j][i]))
                sum = sum + q_vec[j] * self.U[j][i]
            d_vec.append(sum)
        print("after sum: ", d_vec)

        for i in range(0, self.LSA):
            d_vec[i] = d_vec[i] * (1/self.s[i])


        print("d_svd", d_vec);

    def lda(self):
        pass

def composite(U, s, Vh, n):
    return numpy.dot(U[:, :n], s[:n, numpy.newaxis] * Vh[:n, :])

def hahaSVD():
    r, g, b = numpy.rollaxis(plt.imread("/Users/erwin/tmp/12.png"), 2).astype(float)
    img = 0.2989 * r + 0.5870 * g + 0.1140 * b
    img.shape
    U, s, Vh = numpy.linalg.svd(img)

    img10 = composite(U, s, Vh, 10)
    img20 = composite(U, s, Vh, 20)
    img50 = composite(U, s, Vh, 50)

    fig, axes = plt.subplots(1, 4, figsize=(10, 4))
    fig.subplots_adjust(wspace=0.02)
    for ax, _img in zip(axes, (img, img10, img20, img50)):
        ax.imshow(_img,  cmap="gray")
        ax.axis("off")

    pylab.show()

def test():
    x = numpy.array([[2, 4, 6, 8, 10],
         [1, 3, 5, 7, 9],
         [10, 12, 13, 14, 15]])

    u, s, v = numpy.linalg.svd(x)
    print(x.shape, " ", u.shape, " ", s.shape, " ", v.shape)
    print(u)
    print(v)
    print(s[:,numpy.newaxis])
    #x1 = numpy.dot(numpy.dot(u[:, :5], numpy.diag(s))[:,:numpy.newaxis], v[:3,:])
    n = 3
    x1 = numpy.dot(u[:, :n], s[:n, numpy.newaxis] * v[:n,:])
    print(x1)

def pp(builder):
    print(builder.wordlist)

if __name__=='__main__':
    builder = MatrixBuilder("/Users/erwin/downloads/LSA/corpus", "/Users/erwin/downloads/LSA/english.stop")
    builder.createMatrix()
    builder.printMatrix()

    builder.calcTfIdf()
    builder.printMatrix()

    mylsa = MyLSA(builder)
    mylsa.query("what a great day")
    #mylsa.query("human computer interaction")
    #pp(builder)
    #test()

    #hahaSVD()