# -*- coding: utf-8 -*-

import pymongo
import pickle

from sklearn.feature_extraction import DictVectorizer

db = pymongo.Connection('doraemon.iis.sinica.edu.tw')
co_sents = db['sents']
co_pmi = db['pmi.trim']

'''generate feature vector for training'''

if __name__ == '__main__':
    
    for emoID in xrange(1, 3):
        print '----- process emoID: ' + str(emoID) + ' -------------'
        feature = []
        for data in co_sents.find({'emoID':str(emoID)}, {'sent':1}).batch_size(1000):
            sent = data['sent']
            words = sent.strip().split()
            mdoc = {}
        
            for i in enumerate(words):
                for j in xrange(i+1, len(words)):
                    cursor = co_pmi.find({'first': words[i], 'second': words[j]}).limit(1)
                    if cursor.count() != 0:
                        mdoc[words[i]+'_'+words[j]]:cursor['pmi']
            
            print k, v in mdoc.iteritems():
                print k, v, 
        
            feature.append(mdoc)
        
        pickle.dump(feature, open(emoID+'.pickle', 'w'), pickle.HIGHEST_PROTOCOL)
