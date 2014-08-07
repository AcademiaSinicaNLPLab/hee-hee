import random
import pymongo
import pickle

db = pymongo.Connection('localhost')['kimo']
co_sents = db['sents']


if __name__ == '__main__':

    emos = map(lambda x: co_sents.find({'emoID': str(x)}).count(), [x for x in xrange(1, 41)])
    happy = emos[0]
    total = sum(emos) - happy
    picked_feature = []
    picked_value = []

    for x in xrange(2, 41):
        
        with open(str(x)+'.pickle', 'r') as f:
            feature = pickle.load(f)

        print '---finish loading feature from emo: ' + str(x) + '-----'

        num = happy * emos[x-1] / total
        random.shuffle(feature)
        picked_feature.extend(feature[:num])
        picked_value.extend([x] * num)

        del feature [:]


    pickle.dumps(open('unhappy_feature.pickle', 'w'), picked_feature)
    pickle.dumps(open('unhappy_value.pickle', 'w'), picked_value)

