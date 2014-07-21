# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
sys.path.append('../pymodules')
import pymongo
import json, os, codecs

from util import read_words, read_deps

# default output of Stanford Parser
# { 
#       'sents': 0,
#       'tree':  1,
#       'deps':  2
# } 

class DependencyExtracter:

    def __init__(self, mongo_addr, db_name, mapping_file=""):
        self.usentID = 0
        if len(mapping_file) != 0:
            self.maps = json.load(open(mapping_file, 'r'))
            self.mapping = True

        self.mc = pymongo.Connection(mongo_addr)
        self.db = self.mc[db_name] 

        self.co_sents = None
        self.co_deps = None
        self.co_trees = None

    def process_parsed_files(self, corpus_root, category, sections):
        """
        process parsed files from "corpus_root" directory
        specify sections with bit-mask representation
        """

        #self.category = category

        sn = bin(sections).count('1')

        if sections & 1:
            self.co_sents = self.db['sents']
        
        if sections & 2:
            self.co_trees = self.db['trees']

        if sections & 4:
            self.co_deps = self.db['deps']


        for filename in os.listdir(corpus_root):   
            if filename[0] == 'R': continue
            print "processing document %s" % filename 
            mapID = filename.strip('.')[0]
            ## load parsed text
            fpath = os.path.join(corpus_root, filename) 
            doc = codecs.open(fpath, 'r', 'utf-8').read().split('\n\n')

            for i in xrange(len(doc)/sn):
                block = doc[i*sn:(i+1)*sn]
                idx = 0
                word_pos_list = []
                
                if block[idx] == '\n':
                    print 'yes'

                if sections & 1:
                    word_pos_list = self.insert_sents(block[idx], mapID)
                    idx += 1

                if sections & 2:
                    self.insert_trees(block[idx], mapID)
                    idx += 1

                if sections & 4:
#                    print len(block[idx])
                    if len(block[idx]) != 0:
                        self.insert_deps(block[idx], mapID, word_pos_list)

                self.usentID += 1




    def insert_sents(self, block, mapID):
        word_pos_list = read_words(block)

        msent = {
            'emotion': self.maps[mapID],
            'emoID': mapID,
            'sent_length': len(word_pos_list),
            'sent': ' '.join(map(lambda x:x[0], word_pos_list)),
            'usentID': self.usentID,
            'sent_pos': block
        }

#        if self.mapping:
 #           msent['emotion'] = self.maps[emoID]

        #print msent    
        self.co_sents.insert(msent)

        return word_pos_list

    def insert_trees(self, block, mapID):
        mtree = {
            'emotion': self.maps[mapID],
            'emoID': mapID,
            'tree': block,
            'usentID': self.usentID
        }

        #print mtree
        self.co_trees.insert(mtree)


    def insert_deps(self, block, mapID, word_pos_list):
        deps = read_deps(block)

        for rel, left, right in deps:
            mdep = { 
                'emotion': self.maps[mapID],
                'emoID': mapID,
                'sent_length': len(word_pos_list),
                'usentID': self.usentID,
                'rel': rel 
            }   

            mdep['x'] = left[0]
            mdep['y'] = right[0]
            mdep['xIdx'] = left[1]
            mdep['yIdx'] = right[1]
            x_list_idx = left[1]-1
            y_list_idx = right[1]-1
            mdep['xPos'] = word_pos_list[x_list_idx][1]
            mdep['yPos'] = word_pos_list[y_list_idx][1]
            ### insert to db.deps
            self.co_deps.insert(mdep)
        
            #print mdep


if __name__ == '__main__':
    d = DependencyExtracter('doraemon.iis.sinica.edu.tw', 'kimo', '../emoID')
    d.process_parsed_files('/corpus/kimo/parsed.new', 'emotion', int('111', 2))

