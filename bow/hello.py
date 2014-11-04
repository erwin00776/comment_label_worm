__author__ = 'erwin'
#coding=utf-8

import threading
import time
import codecs


class Foo(threading.Thread):
    def __init__(self, x):
        threading.Thread.__init__(self)
        self.x = x
        self.setName("thread-%d" % x)

    def run(self):
        time.sleep(self.x)
        print("%s %d" %(self.getName(), self.x))

import sys
if not "/Users/erwin/svn/libsvm-3.18/python" in sys.path:
    sys.path.append("/Users/erwin/svn/libsvm-3.18/python")
if not 'svmutil' in sys.modules:
    b = __import__('svmutil')
else:
    eval('import svmutil')
    b = eval('reload(svmutil)')
from svmutil import *


def test_svm():
    y, x = svm_read_problem('/Users/erwin/svn/libsvm-3.18/heart_scale')
    m = svm_train(y[:200], x[:200], '-c 4')
    p_label, p_acc, p_val = svm_predict(y[200:], x[200:], m)


def xx():
    fin = open('/users/erwin/work/comment_labeled/dict/sogou_lab.dic', 'r')
    fout = codecs.open('/users/erwin/work/comment_labeled/dict/sogou_lab.dict', 'w', encoding='utf-8')
    context = fin.read().decode('utf-8')
    for line in context.split("\n"):
        line = line.rstrip()
        tup = line.split()
        if len(tup) < 2:
            print(line)
            continue
        try:
            freq = float(tup[1])
        except:
            print(line)
        if len(tup) == 3:
            fout.write(tup[0] + " " + tup[1] + " " + tup[2].lower() + "\n")
        elif len(tup) == 2:
            fout.write(tup[0] + " " + tup[1] + "\n")
    fout.close()
    fin.close()

if __name__ == '__main__':
    '''
    query_list = [1, 2, 3, 4]
    worker = []
    for query in query_list:
        foo = Foo(query)
        worker.append(foo)
        foo.start()
    for w in worker:
        w.join()
    print("main done")
    '''
    #test_svm()
    xx()
