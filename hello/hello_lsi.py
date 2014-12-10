__author__ = 'erwin'

#coding=utf-8

import numpy as np
from scipy.linalg import svd
import matplotlib.pyplot as plt

titles =[
    "The Neatest Little Guide to Stock Market Investing",
    "Investing For Dummies, 4th Edition",
    "The Little Book of Common Sense Investing: The Only Way to Guarantee Your Fair Share of Stock Market Returns",
    "The Little Book of Value Investing",
    "Value Investing: From Graham to Buffett and Beyond",
    "Rich Dad's Guide to Investing: What the Rich Invest in, That the Poor and the Middle Class Do Not!",
    "Investing in Real Estate, 5th Edition",
    "Stock Investing For Dummies",
    "Rich Dad's Advisors: The ABC's of Real Estate Investing: The Secrets of Finding Hidden Profits Most Investors Miss"
]
stopwords = ['and', 'edition', 'for', 'in', 'little', 'of', 'the', 'to']
ignorechars = ",:'!"

class HalloLSI:
    '''
    aka, LSA, latent semantic analysis,
    '''
    def __init__(self, stopwords, ignorechars, corpus=None):
        self.stopwords = stopwords
        self.ignorechars = ignorechars
        self.corpus = corpus
        self.wdict = {}
        self.doc_count = 0
        self.keys = None
        self.A = None

    def parse(self):
        for doc in self.corpus:
            for word in doc.split():
                word = word.lower().translate(None, self.ignorechars)
                if word in self.stopwords:
                    continue
                if word in self.wdict:
                    self.wdict[word].append(self.doc_count)
                else:
                    self.wdict[word] = [self.doc_count]
            self.doc_count += 1

    def build(self):
        self.keys = [k for k in self.wdict.keys() if len(self.wdict[k]) > 1]
        self.keys.sort()
        self.A = np.zeros([len(self.keys), self.doc_count])
        for i, k in enumerate(self.keys):
            for d in self.wdict[k]:
                self.A[i, d] += 1

        print(self.A)

    def train(self):
        self.parse()
        self.build()
        self.U, self.S, self.VT = svd(self.A)

    def printMatrix(self):
        plt.title("LSI/LSA")
        plt.xlabel(u"Dimension2")
        plt.ylabel(u"Dimension3")

        plt_titles = ['T' + str(k) for k in range(1, 10)]
        vdimension1 = self.VT[1]
        vdimension2 = self.VT[2]
        for j in range(len(vdimension1)):
            x = vdimension1[j]
            y = vdimension2[j]
            plt.text(x, y, plt_titles[j])
        plt.plot(vdimension1, vdimension2, '.')

        ut = self.U.T
        dimension1 = ut[1]
        dimension2 = ut[2]
        for j in range(len(dimension1)):
            x = dimension1[j]
            y = dimension2[j]
            plt.text(x, y, self.keys[j])
        plt.plot(dimension1, dimension2, '.')
        plt.show()

        print(vdimension1, vdimension2)
        print(dimension1, dimension2)


if __name__ == '__main__':
    my_lsi = HalloLSI(stopwords=stopwords, ignorechars=ignorechars, corpus=titles)
    my_lsi.train()
    my_lsi.printMatrix()
