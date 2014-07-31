import pymongo
import os, codecs

if __name__ == '__main__':

    co = pymongo.Connection('doraemon.iis.sinica.edu.tw')['kimo']['mutual_occurrence']


    with codecs.open('../../mc_new.txt', 'r', 'utf-8') as f:
        buf = []
        for i, line in enumerate(f):
            l = line.split('\t')
            mdoc = {
                    'first': l[0],
                    'second': l[1],
                    'count': l[2]
            }
            buf.append(mdoc)
            if (i+1) % 1000 == 0:
                co.insert(buf)
                buf = []
        if len(buf) != 0:
            co.insert(buf)
