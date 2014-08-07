# -*- coding: utf-8 -*-

import pymongo
import pickle, sys
import json, codecs

db = pymongo.Connection('doraemon.iis.sinica.edu.tw')['kimo']
co_sents = db['sents']
co_pmi = db['pmi.trim']

'''generate feature vector for training'''

if __name__ == '__main__':
    
    for emoID in xrange(8, 41):
        print '----- process emoID: ' + str(emoID) + ' -------------'
        feature = []
        for i, data in enumerate(co_sents.find({'emoID':str(emoID)}, {'sent':1}, timeout=False).batch_size(100)):
           
            print '\r' + str(i),
            sys.stdout.flush()

            sent = data['sent']
            words = sent.strip().split()
            mdoc = {}
        
            for i, w in enumerate(words):
                for j in xrange(i+1, len(words)):
                    cursor = co_pmi.find_one({'first': words[i], 'second': words[j]}, {'_id':0, 'first':1, 'second':1, 'pmi':1})
                    if cursor:
                        mdoc[words[i]+'_'+words[j]] = cursor['pmi']
            
#            for k, v in mdoc.iteritems():
#                print k + '\t\t\t' + str(v)

            feature.append(mdoc)
        
        try:
            pickle.dump(feature, open(str(emoID)+'.pickle', 'w'), pickle.HIGHEST_PROTOCOL)
        except MemoryError:
            print '----- emoID: ' + str(emoID) + ' failed :( ----------------'
            json.dump(feature, codecs.open(str(emoID)+'.json', 'w', 'utf-8'))
            
        del feature[:]

        print ' '
