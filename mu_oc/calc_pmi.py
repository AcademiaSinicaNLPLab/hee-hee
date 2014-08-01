from __future__ import division

import pymongo
import math

from collections import defaultdict

db = pymongo.Connection('doraemon.iis.sinica.edu.tw')['kimo']
co_f = db['tfidf.emotermcount']
co_mc = db['mutual_occurrence']
co_PMI = db['pmi']

def oc(term):
    return sum(map(lambda x: x['count'], co_f.find({'term':term},{'_id':0, 'count':1}).batch_size(40)))


if __name__ == '__main__':
    
    buf = []
    quick = defaultdict(int)
    for x in co_mc.find().batch_size(10000):
        #print x['count'], oc(x['first']), oc(x['second'])
        
        quick[x['first']] = oc(x['first']) if quick[x['first']] == 0 else quick[x['first']]
        quick[x['second']] = oc(x['second']) if quick[x['second']] == 0 else quick[x['second']]

        pmi = math.log(x['count'] / (quick[x['first']] * quick[x['second']]))
        mdoc = {
                'first': x['first'],
                'second': x['second'],
                'pmi': pmi
        }

        buf.append(mdoc)

        if len(buf) % 10000 == 0:
            co_PMI.insert(buf)
            buf = []
            quick.clear()

    if len(buf) != 0:
        co_PMI.insert(buf)

