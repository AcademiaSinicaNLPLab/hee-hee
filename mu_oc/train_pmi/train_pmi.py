# -*- coding: utf-8 -*-

import numpy as np
import pickle

from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.cross_validation import KFold


if __name__ == '__main__':

    feature = []
    target = []
    for x in xrange(1, 3):
        pmi_list = pickle.load(open(str(x)+'.pickle', 'r'))
        feature.extend(pmi_list)
        target.extend([x] * len(pmi_list))
    
    print '---finish loading feature list---'

    vec = DictVectorizer()
    X = vec.fit_transform(feature)
    y = np.array(target)
    length = len(feature)

    print '---finish vectorizing feature---'    
    del feature
    del target

    kf = KFold(length, n_folds=3, shuffle=True)
    i = 1 
    for train_index, test_index in kf:
        print '---cross validation round: ' + str(i) + ' ------'
        X_train, X_test, y_train, y_test = X[train_index], X[test_index], y[train_index], y[test_index]
        clf = SGDClassifier(loss='hinge', penalty='l2')
        clf.fit(X_train, y_train)
        print '---finish training------'
        score = clf.score(X_test, y_test)
        print '---score: ' + str(score) + ' ---------'
        i += 1


