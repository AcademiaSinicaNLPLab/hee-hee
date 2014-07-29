# -*- coding: utf-8 -*-

from __future__ import division

import pymongo
import logging
import os, pickle
import math
import sys
sys.path.append("pymodules")
from mathutil import entropy


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
            self._co_termcount = self._db['tfidf.emotermcount']
            #self._co_termcount = self._db['tfidf.termcount']
            self._co_sents = self._db['sents']
        except KeyError:
            logging.error('mongo_addr and db_name are both necessary for create a mongo connection')
        
        self._deltaD = 0
        self.d = None
        self._maxN = -999999999

    def build_db(self):
        """

        """
        #co_termcount= self._db['termcount']
        #co_sents = self._db['sents']
        for i in xrange(1, 41):
            c = Counter()
            for sents in self._co_sents.find({'emoID': str(i)}):
                for w in sents['sent'].split():
                    c[w] += 1
           
            for k, v in c.iteritems():
                mdoc = {
                        'emoID': sents['emoID'],
                        'emotion': sents['emotion'],
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
        f = self._co_termcount.find({'term': t, 'emoID': str(d)})
        if f.count() == 0:
            return 0
        return f[0]['count']


    def get_n(self, t):
        """
        For IDF-2, IDF-3
        Def:
            n(t): entropy of term t in D (the universe of documents)
                  --> sum(f(d,t) / F(t)*ln(f(d,t)/F(t))) for d in D
                  where F(t): the number of documents in D that contain term t
        """
       
        if 'tfidf.n' not in self._db.collection_names():
            self.calc_n()
        else:
            return self._db['tfidf.n'].find({'term': t})[0]['n']

    def get_maxN(self):
        if self._maxN == -999999999:
            self._maxN = self._db['tfidf.n'].find().sort('n', pymongo.DESCENDING).limit(1)[0]['n'] 
        
        return self._maxN

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
        if self.d is not None:
            return self.d[d]

        fn = os.path.join(self._cache_root, 'd.pkl')
        if not os.path.exists(fn):
            self.d = defaultdict(int)
            for i in xrange(1, 41):
                count = 0
                for sent in self._co_sents.find({'emoID': str(i)}):
                    count += sent['sent_length']
                self.d[i] = count
            pickle.dump(self.d, open(fn, 'wb'), pickle.HIGHEST_PROTOCOL)
        else:
            self.d = pickle.load(open(fn, 'rb'))        
        return self.d[d]


    def get_deltaD(self):
        if self._deltaD == 0:
            total = 0
            for i in xrange(1, 41):
                total += self.get_d(i)
            self._deltaD = total / 40
        return self._deltaD

    def calc_n(self):
        """
            calculate the entropy n of each distinct term in D
        """
        if 'tfidf.n' in self._db.collection_names():
            print "n has been calculated"
            return 
        
        co_n = self._db['tfidf.n']
        termlist = self._co_termcount.distinct('term')
        for term in termlist:
            #print term + "/r",
             
            n = 0
            F = self.get_F(t)
            for i in xrange(1, 41):
                #print self.get_f(str(i), t), F
                f_F = self.get_f(str(i), t) / F
                if f_F != 0: n += f_F * math.log(f_F)
            
            n = -n
            mdoc = {
                    'term': term,
                    'n': n
            }
            co_n.insert(mdoc)
   
    def calc_entropy(self):
        co_entropy = self._db['tfidf.entropy']
        co_n = self._db['tfidf.n']
        for term in co_n.find():
            
            result = self._co_termcount.find({'term': term['term']}).batch_size(40)
            l = [0] * 40
            for r in result:
                l[int(r['emoID'])-1] = r['count']
            #print l 
            mdoc = {
                    'term': term['term'],
                    #'entropy': entropy([self.get_f(x, term['term']) for x in xrange(1, 41)])
                    'entropy': entropy(l)
            }
            #for k, v in mdoc.iteritems():
             #   print k, v,
            co_entropy.insert(mdoc)


    def calc_tf(self, tftype):
        """
            calculate the tf value of each term
        """

        co_tf = self._db['tfidf.tf']
        for i in xrange(1, 41):
            print '----process emoID: ' + str(i) + ' -----------------'
            for term in self._co_termcount.find({'emoID':str(i)}):
                mdoc = {
                        'term': term['term'],
                        'docID': i,
                        'tftype': tftype
                }

                f = self.get_f(i, term['term'])
                if tftype == 1:
                    tf = 1 + math.log(f, 2)
                elif tftype == 2:
                    tf = f /(f + self.get_d(i)/self.get_deltaD())
                
                mdoc['tf'] = tf
                co_tf.insert(mdoc)
       

    def calc_idf(self, idftype):
        """
            calculate the idf value of each term
        """

        co_idf = self._db['tfidf.idf']
        co_n = self._db['tfidf.n']
        max_n = self.get_maxN()
        for term in co_n.find():
            mdoc = {
                    'term': term['term'],
                    'idftype': idftype
            }
            if idftype == 1:
                idf = math.log(self._deltaD / self.get_F(term['term']))
            elif idftype == 2:
                idf = max_n - term['n']
            mdoc['idf'] = -idf
            co_idf.insert(mdoc)



if __name__ == '__main__':


    tfidf = TFIDFModel(mongo_addr="doraemon.iis.sinica.edu.tw", db_name="kimo")
