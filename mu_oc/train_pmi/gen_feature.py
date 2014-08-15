# -*- coding: utf-8 -*-

import pymongo
import pickle, sys
import json, codecs

db = pymongo.Connection('localhost')['kimo']
co_sents = db['sents']
co_pmi = db['pmi.trim']
co_feature = db['feature.pmi']

'''generate feature vector for training and insert into database'''

if __name__ == '__main__':
    
    buf = []

    for emoID in xrange(1, 41):
        print '----- process emoID: ' + str(emoID) + ' -------------'
        for i, data in enumerate(co_sents.find({'emoID':str(emoID)}, {'sent':1, 'emoID':1, 'usentID':1}, timeout=False).batch_size(1000)):
           
            print '\r' + str(i),
            sys.stdout.flush()

            sent = data['sent']
            words = sent.strip().split()
            mdoc = {
                    'usentID': data['usentID'],
                    'emoID': data['emoID']
            }
            
            pmi_pair = {}
            
            for i, w in enumerate(words):
                for j in xrange(i+1, len(words)):
                    cursor = co_pmi.find_one({'first': words[i], 'second': words[j]}, {'_id':0, 'first':1, 'second':1, 'pmi':1})
                    if cursor:
                        pmi_pair[words[i]+'_'+words[j]] = cursor['pmi']
            
#            for k, v in pmi_pair.iteritems():
#                print k + '\t\t\t' + str(v)

            mdoc['feature'] = pmi_pair
            buf.append(mdoc)

            if len(buf) >= 100:
                co_feature.insert(buf)
                del buf[:]
        
        print ' '

    if len(buf) != 0:
        co_feature.insert(buf)
