import random
import pymongo
import pickle

db = pymongo.Connection('localhost')['kimo']
co_sents = db['sents']
co_features = db['feature.pmi']

if __name__ == '__main__':

    indices = [x for x in xrange(0, 5624732)]
    print 'haha'
    happy = co_sents.find({'emoID':'1'}, {'emoID':1, 'usentID':1, '_id':0})
    happy_len = happy.count()

    del indices[4936337:5208195] 

    random.shuffle(indices)
    indices = indices[:happy_len]
    
    print happy_len, len(indices)

    picked_feature = []
    picked_value = []

    for x, i in enumerate(indices):
        print '\r' + str(x),
        feature = co_features.find_one({'usentID':i})
        picked_feature.append(feature['feature'])
        picked_value.append(int(feature['emoID']))

    for i, x in enumerate(picked_value):
        if i > 10:
            break
        print x
    
    pickle.dump(picked_feature, open('unhappy_feature.pickle', 'wb'), pickle.HIGHEST_PROTOCOL)
    pickle.dump(picked_value, open('unhappy_value.pickle', 'wb'), pickle.HIGHEST_PROTOCOL)

