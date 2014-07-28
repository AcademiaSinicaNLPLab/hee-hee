# -*- coding: utf-8 -*-

from __future__ import division

import pymongo
import logging
import os
import math

from collections import defaultdict, Counter


class TFIDFModel(object):
    """

    """
    def __init__(self, **kwargs):

        # T: the universe of terms
        # D: the universe of documents

        ## set logging default level: INFO
        loglevel = logging.DEBUG if 'verbose' in kwargs and kwargs['verbose'] == True else logging.INFO
        logging.basicConfig(format='[%(levelname)s] %(message)s', level=loglevel)


        ## check(and create if not existed) TFIDF cache path
        self._cache_root = 'TFIDFModel' if 'cache_root' not in kwargs else kwargs['cache_root']
        if not os.path.exists(self._cache_root): os.mkdir(self._cache_root)

        ## connect to mongo
        logging.debug('connect to mongodb')
        try:
            self._db = pymongo.Connection(kwargs['mongo_addr'])[kwargs['db_name']]
            self._co_termcount = self._db['tfidf.termcount']
            self._co_sents = self._db['sents']
        except KeyError:
            logging.error('mongo_addr and db_name are both necessary for create a mongo connection')
        
        self._deltaD = 0

    def build_db(self):
        """

        """
        #co_termcount= self._db['termcount']
        #co_sents = self._db['sents']
        for sents in self._co_sents.find():
            c = Counter(sents['sent'].split())
            for k, v in c.iteritems():
                mdoc = {
                        'usentID': sents['usentID'],
                        'term': k,
                        'count': v
                }
                self._co_termcount.insert(mdoc)



    def get_f(self, d, t):
        """
        For all kinds of TF
        Def:
            f(d,t): the number of occurrences of term t in document d
        """
        return self._co_termcount.find({'term': t, 'usentID':d}).count()


    def get_n(self, t):
        """
        For IDF-2, IDF-3
        Def:
            n(t): entropy of term t in D (the universe of documents)
                  --> sum(f(d,t) / F(t)*ln(f(d,t)/F(t))) for d in D
                  where F(t): the number of documents in D that contain term t
        """
        #co_sents = self._db['sents']
        n = 0
        for sent in self._co_sents.find():
           f_F = self.get_f(sent['usentID'], t) / self.get_F(t)
           if f_F != 0: n += f_F * math.log(f_F)
        return n 



    def get_F(self, t):
        """
        For IDF-1 (directly used), IDF-2 (in n(t)), IDF-3 (in n(t))
        Def:
            F(t): the number of documents in D that contain term t
        """
        return self._co_termcount.find({'term':t}).count()

    def get_d(self, d):
        """
        For TF-2, TF-3
        Def:
            |d|: cardinality (length) of d
            |delta d|: average document length in D
        """
        return self._co_sents.find({'usentID':d})[0]['sent_length']

    def get_deltaD(self):
        if self._deltaD == 0:
            sents = self._co_sents.find(None, {'_id': 0, 'sent_length':1})
            self._deltaD = sum(map(lambda x: x['sent_length'], sents))/sents.count()
            print self._deltaD    
        return self._deltaD


if __name__ == '__main__':


    tfidf = TFIDFModel(mongo_addr="doraemon.iis.sinica.edu.tw", db_name="kimo")
