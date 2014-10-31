__author__ = 'erwin'
#coding=utf-8

import sklearn
from sklearn import datasets
from sklearn.externals.six import StringIO
from sklearn import tree
from sklearn.naive_bayes import GaussianNB
import pydot

def test_bayes():
    '''
    贝叶斯
    '''
    iris = datasets.load_iris()
    gnb = GaussianNB()
    y_pred = gnb.fit(iris.data, iris.target).predict(iris.data)
    #print('debeg_on', iris.data, iris.target, y_pred)
    print("total sample: %d, miss:%d" %
            (iris.data.shape[0],
             (iris.target != y_pred).sum()))


def test_decision_tree():
    X = [[0, 0], [1,1]]
    Y = [0, 1]
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X, Y)
    #print(clf)
    iris = datasets.load_iris()
    clf = clf.fit(iris.data, iris.target)

    dot_data = StringIO()
    tree.export_graphviz(clf, out_file=dot_data)
    graph = pydot.graph_from_dot_data(dot_data.getvalue())
    graph.write_pdf("/users/erwin/tmp/decision_tree_iris.pdf")


def test_feature_selection():
    '''
    RFE,
    '''
    from sklearn.feature_selection import VarianceThreshold
    X = [[0, 0, 1], [0, 1, 0], [1, 0, 0], [0, 1, 1], [0, 1, 0], [0, 1, 1]]
    sel = VarianceThreshold(threshold=0.8*(1-0.8))  # Var[x] = p*(1-p)
    print(sel.fit_transform(X))

    from sklearn.feature_selection import SelectKBest
    from sklearn.feature_selection import chi2
    iris = datasets.load_iris()
    X, y = iris.data, iris.target
    print("before feature selection", X.shape)
    X_new = SelectKBest(chi2, k=2).fit_transform(X, y)
    print("after feature selection", X_new.shape)


def test_nearest_neighbours():
    from sklearn.neighbors import NearestNeighbors
    import numpy as np
    X = np.array([[-1, 1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
    neighbours = NearestNeighbors(n_neighbors=2, algorithm="ball_tree").fit(X)
    distances, indices = neighbours.kneighbors(X)
    print(distances, indices)


def test_pca():
    import pylab
    import matplotlib.pyplot as plt
    from sklearn import datasets
    from sklearn.decomposition import PCA
    from sklearn.lda import LDA

    iris = datasets.load_iris()
    X = iris.data
    y = iris.target
    target_names = iris.target_names

    pca = PCA(n_components=2)
    X_r = pca.fit(X).transform(X)

    lda = LDA(n_components=2)
    X_r2 = lda.fit(X, y).transform(X)

    print('explained variance ratio (first two components): %s'
        % str(pca.explained_variance_ratio_))

    plt.figure()
    for c, i, target_name in zip("rgb", [0, 1, 2], target_names):
        plt.scatter(X_r[y == i, 0], X_r[y == i, 1], c=c, label=target_name)
    plt.legend()
    plt.title('PCA of IRIS dataset')

    plt.figure()
    for c, i, target_name in zip("rgb", [0, 1, 2], target_names):
        plt.scatter(X_r2[y == i, 0], X_r2[y == i, 1], c=c, label=target_name)
    plt.legend()
    plt.title('LDA of IRIS dataset')

    # 实际显示窗口
    pylab.show()


def test_kernel_pca():
    import pylab
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA, KernelPCA
    from sklearn.datasets import make_circles

    np.random.seed(0)
    #X, y = make_circles(n_samples=400, factor=0.3, noise=0.05)
    X, y = make_circles(n_samples=400, factor=0.3, noise=0.1)

    kpca = KernelPCA(kernel="rbf", fit_inverse_transform=True, gamma=10)
    #kpca = KernelPCA(kernel="poly", fit_inverse_transform=True, gamma=10)
    X_kpca = kpca.fit_transform(X)
    X_back = kpca.inverse_transform(X_kpca)
    pca = PCA()
    X_pca = pca.fit_transform(X)

    plt.figure()
    plt.subplot(2, 2, 1, aspect='equal')
    plt.title("Original space")
    reds = y==0
    blues = y==1

    plt.plot(X[reds, 0], X[reds, 1], "ro")
    plt.plot(X[blues, 0], X[blues, 1], "bo")
    plt.xlabel("$x_1$")
    plt.ylabel("$x_2$")

    X1, X2 = np.meshgrid(np.linspace(-1.5, 1.5, 50), np.linspace(-1.5, 1.5, 50))
    X_grid = np.array([np.ravel(X1), np.ravel(X2)]).T
    Z_grid = kpca.transform(X_grid)[:, 0].reshape(X1.shape)
    plt.contour(X1, X2, Z_grid, colors='grey', linewidths=1, origin='lower')

    plt.subplot(2, 2, 2, aspect='equal')
    plt.plot(X_pca[reds, 0], X_pca[reds, 1], "ro")
    plt.plot(X_pca[blues, 0], X_pca[blues, 1], "bo")
    plt.title("Project by PCA")
    plt.xlabel("1st principal component")
    plt.ylabel("2nd component")

    plt.subplot(2, 2, 3, aspect='equal')
    plt.plot(X_kpca[reds, 0], X_kpca[reds, 1], "ro")
    plt.plot(X_kpca[blues, 0], X_kpca[blues, 1], "bo")
    plt.title("Projection by KernelPCA")
    plt.xlabel("1st principal component in space induced by $\phi$")
    plt.ylabel("2nd component")

    plt.subplot(2, 2, 4, aspect='equal')
    plt.plot(X_back[reds, 0], X_back[reds, 1], "ro")
    plt.plot(X_back[blues, 0], X_back[blues, 1], "bo")
    plt.title("Original space after inverse transform")
    plt.xlabel("$x_1$")
    plt.ylabel("$x_2$")

    plt.subplots_adjust(0.02, 0.10, 0.98, 0.94, 0.04, 0.35)

    plt.show()
    pylab.show()


if __name__ == '__main__':
    #test_bayes()
    #test_decision_tree()
    #test_feature_selection()
    #test_nearest_neighbours()
    #test_pca()
    test_kernel_pca()