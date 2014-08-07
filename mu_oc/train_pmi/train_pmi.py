# -*- coding: utf-8 -*-

import numpy as np
import pickle

from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.cross_validation import KFold
from sklearn.preprocessing import StandardScaler

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

    scaler = StandardScaler(with_mean=False)

    kf = KFold(length, n_folds=3, shuffle=True)
    i = 1 
    for train_index, test_index in kf:
        print '---cross validation round: ' + str(i) + ' ------'
        X_train, X_test, y_train, y_test = X[train_index], X[test_index], y[train_index], y[test_index]
        
        #scale data for SGD performance
        scaler.fit(X_train)
        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)
        
        clf = SGDClassifier(loss='hinge', penalty='elasticnet', shuffle=True)
        clf.fit(X_train, y_train)
        print '---finish training------'
        score = clf.score(X_test, y_test)
        print '---score: ' + str(score) + ' ---------'

        with open(str(i)+'.result', 'w') as f:
            for yy in y_test:
                f.write(str(yy) + ' ')
            f.write('\n')
            result = clf.predict(X_test)
            for r in result:
                f.write(str(r) + ' ')
            f.write('\n')

        i += 1
