__author__ = 'erwin'
#coding=utf-8

import threading
import time


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

def test_svm():
    from svmutil import *
    y, x = svm_read_problem('/Users/erwin/svn/libsvm-3.18/heart_scale')
    m = svm_train(y[:200], x[:200], '-c 4')
    p_label, p_acc, p_val = svm_predict(y[200:], x[200:], m)

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
    test_svm()
