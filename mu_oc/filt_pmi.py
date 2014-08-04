# -*- coding: utf-8 -*-

import pymongo

from calc_pmi import oc
from collections import defaultdict


db = pymongo.Connection('doraemon.iis.sinica.edu.tw')['kimo']
co_pmi = db['pmi']
co_fipmi = db['pmi.trim']
co_f = db['tfidf.emotermcount']

if __name__ == '__main__':
    
    quick = defaultdict(int)
    buf = []

    for pair in co_pmi.find().batch_size(1000):
        if quick[pair['first']] == 0:
            quick[pair['first']] = oc(pair['first'])
        if quick[pair['second']] == 0:
            quick[pair['second']] = oc(pair['second'])
        if pair['first'] > 1 and pair['second'] > 1:
            mdoc = {
                    'first': pair['first'],
                    'second': pair['second'],
                    'pmi': pair['pmi']
            }
            buf.append(mdoc)

        if len(buf) > 1000:
            co_fipmi.insert(buf)
            buf = []
            quick.clear()

    if len(buf) != 0:
        co_fipmi.insert(buf)
