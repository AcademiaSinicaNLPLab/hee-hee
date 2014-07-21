# -*- coding: utf-8 -*-

import pymongo
import json

if __name__ == '__main__':
    db = pymongo.Connection('doraemon.iis.sinica.edu.tw')['kimo']
    co = db['emotions']
    
    mapping = json.load(open('emoID', 'r'))

    for k, v in mapping.items():
        mdoc = {
            'emotion': v,
            'emoID': k,
            'label': 'kimo'
        }
        co.insert(mdoc)
