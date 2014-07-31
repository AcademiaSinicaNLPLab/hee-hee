import pymongo
import math


db = pymongo.Connection('doraemon.iis.sinica.edu.tw')
co_f = db['tfidf.emotermcount']
co_mc = db['mutual_occurrence']
co_PMI = db['PMI']

def oc(term):
    return sum(map(lambda x: x['count'], co_f.find({'term':term},{'_id':0, 'count':1}.batch_size(40))))


if __name__ == '__main__':
    
    buf = []
    for x in co_mc.find().batch_size(1000): 
        pmi = math.log(x['count'] / (oc(x['first']) * oc(x['second'])))
        mdoc = {
                'first': x['first'],
                'second': x['second'],
                'pmi': pmi
        }

        buf.append(mdoc)

        if len(buf) % 10000:
            co_PMI.insert(buf)
            buf = []

    if len(buf) != 0
        co_PMI.insert(buf)

