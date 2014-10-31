__author__ = 'erwin'
#coding=utf-8

from numpy import *
from numpy.linalg import *
from scipy import *
import matplotlib.pyplot as plt
from scipy import optimize
from scipy import stats

def foo(x, y):
    return 10 * x + y


def hello_numpy_base():
    a = arange(15).reshape(3, 5)
    print(a, a.shape, a.ndim, a.dtype)
    b = array([6, 7, 8, 9]).reshape(2, 2)
    print(b)
    c = array([1, 2, 3], dtype=complex)
    print(c)
    d = zeros((2, 2))
    d1 = ones( (2,3,4), dtype='int16' )
    print('zeros', d, d1)

    a = array([20, 30, 40, 50]).reshape(2, 2)
    b = arange(4).reshape(2, 2)
    print(a-b)
    print(a**b)
    print(a*b)

    r = (100 * random.random((2, 3)))
    r1 = array(r, dtype='int32')
    print('random matrix', r, r1)

    print(a.sum(axis=0)) # min, cumsum

    #print(sqrt(a))

    b = fromfunction(foo, (5, 4), dtype=int)
    print(b, b[2, 3], b[:, 1], b[ : : -1]) # last one is reversed

    #print(floor(10*random.random((3, 4))))
    print(b.ravel())        # flatten the array
    print(b.transpose())    # transpose
    print('reshape', a.reshape(4, -1))
    print(a.resize((1, 4)), a)

    c = a.view()    # view or shallow copy
    print("c is a", c is a, "c.base is a", c.base is a)
    c[0, 1] = 1000
    print(a, c)
    d = a.copy()    # deep copy

    print("mean of d %s is %d, cov: %d, std: %d" % (d, mean(d), cov(d), std(d)))
    #print(beta(a=1, b=10, size=(2, 2)))
    a = arange(4)**2
    a = a.reshape((2, 2))
    print('inv', inv(a), 'eye', eye(3))
    x = array([2, 3, 4, 5]).reshape((2, 2))
    y = array([[5.0], [7.0]], dtype=float)
    print('solve', solve(x, y))

    j = array([[0.0, -1.0],
               [1.0, 0.0]])
    print('eig', eig(j))    # eigenvalue


def hello_matrix():
    A = matrix('1.0 2.0; 3.0 4.0')
    Y = matrix('5.0 7.0')
    print(A, A.T, A.I)
    #print(solve(A, Y))
    A = arange(12)
    A.shape = (3, 4)
    M = mat(A.copy())


def f(x):
    return x**2 + 10 * sin(x)

def f2(x, a, b):
    return a * (x**2) + b * (sin(x))

def hallo_scipy():
    print('hallo scipy')
    A = matrix([[1, 1, 1],
                [4, 4, 3],
                [7, 8, 5]])
    b = matrix([1, 2, 1]).transpose()
    print(det(A))       # 值
    print(inv(A)*b)     #
    print(eig(A))       # 特征矩阵
    print(svd(A))

    x = arange(-10, 10, 0.1)
    plt.plot(x, f(x))
    #plt.show()

    # find the min point by BFGS, 拟牛顿法
    print(optimize.fmin_bfgs(f, 0))
    print(optimize.fmin_bfgs(f, 3))
    grid = (-10, 10, 0.1)
    xmin_global1 = optimize.brute(f, (grid, ))      # 暴力尝试寻找全局最小
    xmin_global2 = optimize.anneal(f, 0.0)     # 模拟退火
    print('global min', xmin_global1, xmin_global2)

    print('fminbound', optimize.fminbound(f, 0, 10))

    print('fsolve formula', optimize.fsolve(f, 2.5))

    # 回归的参数估计
    guess = [2, 2]
    xdata = linspace(-10, 10, num=20)
    ydata = f(xdata) + random.random(xdata.size)

    params, params_convariance = optimize.curve_fit(f2, xdata, ydata, guess)
    print('curve params', params)
    plt.plot(xdata, f2(xdata, params[0], params[1]))
    plt.show()


def hallo_scipy_stats():
    a = random.normal(size=1000)
    bins = arange(-4, 5)
    hist = histogram(a, bins=bins, normed=True)[0]
    bins = 0.5 * (bins[1:] + bins[:-1])
    print(bins)

    b = stats.norm.pdf(bins)
    x = arange(-4, 5)
    print(len(x), len(b))
    #plt.plot(x[:len(b)], b)
    plt.subplots(nrows=1, ncols=2)
    plt.plot(x[:len(b)], b)
    plt.plot(bins, hist)
    #plt.show()
    print(b)

    print('median', median(a))
    a = random.normal(0, 1, size=100)
    b = random.normal(1, 1, size=10)

    print(stats.ttest_ind(a, b))

if __name__ == '__main__':
    #hello_numpy_base()
    #hello_matrix()
    #hallo_scipy()
    hallo_scipy_stats()
