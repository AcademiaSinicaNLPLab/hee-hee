# -*- coding: utf-8 -*-

import pymongo, logging, json
from collections import Counter

class FeatureExtractor(object):
	"""
	Extract Feature from mongodb based on sentence/document
	"""
	def __init__(self, **kwargs):

		try:
			self._db = pymongo.Connection(kwargs['mongo_addr'])[kwargs['db_name']]
		except KeyError, e:
			logging.error('mongo_addr and db_name are both necessary for create a mongo connection')
			raise e

		## set logging level
		## default level: INFO
		loglevel = logging.DEBUG if 'verbose' in kwargs and kwargs['verbose'] == True else logging.INFO
		logging.basicConfig(format='[%(levelname)s] %(message)s', level=loglevel)


	def _SaveSettings(self, settings):
		"""
		private method: save settings to mongodb
		"""
		# > db.features.settings.findOne()
		# {
		# 	"_id" : ObjectId("53730f67d4388c27cc4c06f1"),
		# 	"min_count" : 3,
		# 	"feature_name" : "pattern"
		# }
		setting_id = str(self._db['features.settings'].insert(settings))
		return setting_id

	def PatternEmotion(self, **kwargs):
		"""
		create pattern-emotion feature
		> feature dimention: number of emotions
		> source: db.sents, db.pats
		> destination: db.feature.pattern_emotion
		"""
		## save settings
		settings = {
			'feature_name': 'pattern_emotion',
		}
		settings.update(kwargs)

		logging.info('save current setting: %s', json.dumps(settings))
		setting_id = self._SaveSettings(settings)

		## sentence-based
		logging.info('start extracting features')

		# detect and set min_count
		# min_count matters only if min_count > 1
		min_count = 0 if 'min_count' not in kwargs else kwargs['min_count']

		for sent_mdoc in self._db['sents'].find():
			features = Counter()
			for pat_mdoc in self._db['pats'].find({'usentID': sent_mdoc['usentID']}):

				## fetch lexicon to get dist
				lexicon_mdoc = self._db['lexicon.nested'].find_one({'pattern': pat_mdoc['pattern'] })
				## no data fethced
				if not lexicon_mdoc:
					continue
				## total count is less than min_count threshold
				elif lexicon_mdoc['total_count'] < min_count:
					continue
				else:
					## aggregate counts
					## detect and set weight
					weight = pat_mdoc['weight'] if 'weighted' in kwargs and kwargs['weighted'] == True else 1.0
					for emotion, count in lexicon_mdoc['count'].items():
						features[emotion] += count*weight

			mdoc = {
				'setting': setting_id,				# <str>
				'usentID': sent_mdoc['usentID'],	# <int>
				'emotion': sent_mdoc['emotion'],	# <str>
				'feature': dict(features),			# <dict>
			}
			
			logging.debug('insert pats in usentID: %d' % (sent_mdoc['usentID']) )

			self._db['features.pattern_emotion'].insert(mdoc)

		logging.info('create index on "setting"')
		self._db['features.pattern_emotion'].create_index('setting')
			

if __name__ == '__main__':
	
	# from FeatureExtractor import FeatureExtractor

	Ext = FeatureExtractor(mongo_addr="doraemon.iis.sinica.edu.tw", db_name="kimo", verbose=False)
	
	Ext.PatternEmotion(weighted=True, min_count=4)

