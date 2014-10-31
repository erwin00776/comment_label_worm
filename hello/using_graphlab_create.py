__author__ = 'erwin'

import graphlab
#sf = graphlab.SFrame(data='http://graphlab.com/files/datasets/freebase_performances.csv')


def pagerank():
    sf = graphlab.load_sframe('/users/erwin/work/ml_datasets/freebase_performances.csv')
    print sf
    g = graphlab.SGraph()
    g = g.add_edges(sf, 'actor_name', 'film_name')
    pr = graphlab.pagerank.create(g)
    print(pr.get('pagerank').topk(column_name='pagerank'))


def classification():
    data = graphlab.SFrame("http://s3.amazonaws.com/GraphLab-Datasets/regression/houses.csv")
    data['expensive'] = data['price'] > 3000
    model = graphlab.svm.create(data, target='expensive', features=['bath', 'bedroom', 'size'])
    coefficients = model['coefficients']
    predications = model.predict(data)
    print(predications)
    #predications = model.predict(data, output_type="margin")


def nearest_neighbors():
    sf = graphlab.SFrame('http://s3.amazonaws.com/GraphLab-Datasets/regression/houses.csv')
    for c in sf.column_names():
        sf[c] = (sf[c] - sf[c].mean())/sf[c].std()

    sf.add_row_number(column_name='house_id')
    sf['house_id'] = sf['house_id'].astype(str)
    model = graphlab.nearest_neighbors.create(dataset=sf, label='house_id', features=['bedroom', 'bath', 'size'])
    print(model.summary())


def tree_emsembles():
    sf = graphlab.SFrame.read_csv("http://s3.amazonaws.com/GraphLab-Datasets/boosted_trees/boston-housing.csv")
    (training_data, test_data) = sf.random_split(fraction=0.8)
    objective = 'regression' # or 'classification'
    m = graphlab.boosted_trees.create(training_data, target_column='MEDV', objective=objective)
    test_result = m.evaluate(test_data)
    rmse = test_result['rmse']
    print(rmse)
    print(test_result)


def vowpal_wabbit():
    from graphlab import vowpal_wabbit as vw
    #m = vw.create(sf, "rating")


def recommender():
    data = graphlab.SFrame('s3://GraphLab-Datasets/audioscrobbler')
    m = graphlab.recommender.create(data)
    recs = m.summary()
    print(recs)


if __name__=="__main__":
    #classification()
    #tree_emsembles()
    #nearest_neighbors()
    recommender()

