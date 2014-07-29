# -*- coding: utf-8 -*-

svm_root = '/tools/libsvm/python'

import sys
import os
import pymongo
import logging
sys.path.append(svm_root)
import svmutil


class svmwrap(object):
    """
    1. feature vectors and problems
        1.1 format (y,x):   self.format_yx()
                            -> fetch mongodb based on the specified setting_id
                               and format features into (y, x) tuple

        1.2.1 save (y,x):   self.save_yx()
                            -> dump the (y, x) tuple to a file

        1.2.2 load (y,x):   self.load_yx() 
                            -> load the (y, x) tuple from a file

        1.3.1 fuse (y,x)s:  self.fuse()
                            -> fuse multiple sets of (y, x) tuple

        1.3.2 normalize:    self.features_normalize()
                            -> normalize fused features

        1.4 form problem:   self.format_problem(y, x)
                            -> a wrap of svmutil.svm_problem(y, x)
        
    2. svm training
        2.1 set parameter:  svmutil.set_parameter()
        2.2 training:       svmutil.train()
        2.3 save model:     svmutil.svm_save_model()

    3. svm prediction
    4. svm evaluation
    """
    def __init__(self, **kwargs):

        ## set logging default level: INFO
        loglevel = logging.DEBUG if 'verbose' in kwargs and kwargs['verbose'] == True else logging.INFO
        logging.basicConfig(format='[%(levelname)s] %(message)s', level=loglevel)

        ## connect to mongo
        try:
            self._db = pymongo.Connection(kwargs['mongo_addr'])[kwargs['db_name']]
            logging.debug('mongodb %s.%s connected' % (kwargs['mongo_addr'], kwargs['db_name']))
        except KeyError:
            logging.error('mongo_addr and db_name are both necessary for create a mongo connection')

        ## set cache root
        self._cache_root = 'svmwrap' if 'cache_root' not in kwargs else kwargs['cache_root']
        if not os.path.exists(self._cache_root): os.mkdir(self._cache_root)

        self.labels = set()

    def genFeatureIndex(self):
        """
        create a dictionary containing the mapping from <feature name> to <feature ID>
        e.g.,   happy --> 1, sad --> 2, ..., angry --> 40
        """
        self.feature_idx = { x['emotion']:int(x['emoID']) for x in self._db['emotions'].find({'label':'kimo'})}
        logging.debug('feature_idx generated, total %d keys' % (len(self.feature_idx)))

    def format_yx(self, setting_id, **kwargs):
        from bson.objectid import ObjectId
        """
        Function
            read from mongodb > features.[feature_name]
            collect instance features --> x and gold answers --> y
        kwargs:
            ignore_empty_feature (FALSE/true)
        """
        self.setting_id = setting_id
        
        ## fetch feature_name and assembly collection_name
        ## feature_name: "pattern_emotion" --> collection_name: "features.pattern_emotion"
        try:
            feature_name = self._db['features.settings'].find_one({"_id": ObjectId(setting_id) })['feature_name']
            collection_name = 'features.'+feature_name
            logging.debug('Source collection will be %s with setting: %s' % (collection_name, setting_id))
        except TypeError, e:
            logging.error('The setting %s is not existed')
            raise e
        
        
        ## form x,y
        logging.debug('Formatting y, x pairs from %s with setting: %s' % (feature_name, setting_id))
        y, x = [], [] # y, x = [1,-1], [{1:1, 3:1}, {1:-1,3:-1}]
        threshold = 1000
        ignore_empty_feature = False if 'ignore_empty_feature' not in kwargs else kwargs['ignore_empty_feature']
        for i, mdoc in enumerate(self._db[collection_name].find({'setting': setting_id})):

            if i == threshold: break

            ## form vector x: features
            features = {self.feature_idx[fn]:fv for fn,fv in mdoc['feature'].iteritems() }
            if ignore_empty_feature and not features:
                continue
            else:
                x.append( features ) # fetch feature{name, value} --> feature{id, value}

                ## form vector y: gold answers
                label_id = self.feature_idx[mdoc['emotion']]
                y.append( label_id )

                ## record distinct feature id
                self.labels.add( label_id )

        logging.debug('Totally %d instance scanned, %d added (%.2f%%)' % (i, len(y)-1, round(len(y)/float(i)*100) ))

        return (y, x)


    def to_binary(self, y, x):
        fw = { open() for i in xrange()}

    ## not finished
    def save_yx(self, y, x, **kwargs):
        """
        Function:
            save y, x pairs to a plain-text file in the svm-readable format
        kwargs:
            yx_file_name (FALSE/<str>): specify a path to the destination file
            overwrite (FALSE/true): set True to overwrite the destination file
        """

        ## auto-generate problem path
        yx_file_name = False if 'yx_file_name' not in kwargs else kwargs['yx_file_name']
        
        if not yx_file_name:
            yx_file_name = '.'.join([self.setting_id, 'yx']) ## 53d0a63cd4388c1b77a25f19.yx
            yx_file_path = os.path.join(self._cache_root, yx_file_name)
        elif type(yx_file_name) is str and '/' not in yx_file_name: # containing a self-defined directory
            yx_file_path = os.path.join(self._cache_root, yx_file_name)
        elif type(yx_file_name) is str:
            yx_file_path = yx_file_name
        else:
            raise TypeError('Unknown type of yx_file_name, which is in str format')

        ## check if the destination file already existed
        overwrite = False if 'overwrite' not in kwargs else kwargs['overwrite']
        if os.path.exists(yx_file_path) and not overwrite:
            logging.warn('yx pairs %s exists, use overwrite=True to ignore the previous version' % (yx_file_path) )
            return False
        else:
            ## make sure destination folder existed
            dirname = os.path.dirname(yx_file_path)
            if dirname and not os.path.exists(dirname): os.makedirs(dirname)

            with open(yx_file_path, 'w') as fw:
                for label, insts in zip(y,x):

                    label_str = str(label)

                    ## Dense data
                    ## insts is a tuple/list: e.g., [[1, 2, -2], [2, -2, 2]]
                    if type(insts) in (list, tuple):
                        # ...
                        pass

                    ## Sparse data
                    ## insts is a dictionary: e.g., {0:1, 1:2, 2:-2} or {0:2, 1:-2, 2:2}
                    elif type(insts) is dict:
                        # insts_str_lst: ['0:1', '1:2', '2:-2']
                        insts_str_lst = map(lambda x: str(x[0])+':'+str(x[1]), sorted(insts.items(), key=lambda x:int(x[0])))
                        # line: '1 0:1 1:2 2:-2\n'
                        line = ' '.join([label_str] + insts_str_lst) + '\n'
                    fw.write(line)

            logging.info('yx pairs saved in %s' % (yx_file_path))
        return yx_file_name

    def load_yx(self, yx_file_name, **kwargs):
        
        # <cache>/[filename].yx
        if self._cache_root+'/' in yx_file_name:
            yx_file_path = yx_file_name
        elif self._cache_root+'/' not in yx_file_name:
            # /temp/test/[filename].yx
            if '/' in yx_file_name:
                yx_file_path = yx_file_name
            # [filename].yx --> <cache>/[filename].yx
            else:
                yx_file_path = os.path.join(self._cache_root, yx_file_name)

        if not os.path.exists(yx_file_path):
            raise OSError("Target file %s doesn't exist" % (yx_file_path))
        else:
            y ,x = [], []
            with open(yx_file_path) as fr:
                for line in fr:
                    if len(line.strip()) == 0: continue # ignore empty line

                    line = line.strip().split()

                    ## revert y
                    label = int(line[0])
                    y.append(label)

                    ## revert x
                    insts_str_lst = line[1:]
                    insts = {int(insts_str.split(':')[0]):float(insts_str.split(':')[1]) for insts_str in insts_str_lst}
                    x.append(insts)

            return (y, x)



    def format_problem(self, y, x):
        self.problem = svmutil.svm_problem(y, x)
        return self.problem

    ## 2. svm training
    def set_parameter(self, options=None):
        self.param = svmutil.svm_parameter(options)
        return self.param

    ## train(prob, param)
    ## train(prob, [param])
    ## train([prob, param])
    def train(self, prob=None, param=None):
        _problem = prob if prob else self.problem
        _param = param if param else self.param
        svmutil.svm_train(_problem, _param)
        


if __name__ == '__main__':
    
    # in IPython
    #   In [1]: %load_ext autoreload
    #   In [2]: %autoreload 2
    #   In [3]: from svmwrap import svmwrap

    svm = svmwrap(mongo_addr="doraemon.iis.sinica.edu.tw", db_name="kimo",verbose=True)

    svm.genFeatureIndex() ## get feature_idx

    # feature_name="features.pattern_emotion", 
    (y, x) = svm.format_yx(setting_id="53d0a63cd4388c1b77a25f19", ignore_empty_feature=True)

    svm.to_binary(y, x)

    yx_file = svm.save_yx(y, x, overwrite=True) # yx_file_name=False, overwrite=True

    (y, x) = svm.load_yx(yx_file_name=yx_file)
    
    svm.format_problem(y, x)

    svm.set_parameter('-b 1 -v 10 -q')

    model = svm.train()



