# -*- coding: utf-8 -*-

import pymongo, logging
from collections import Counter

class FeatureExtractor(object):
	"""
	Extract Feature from mongodb based on sentence/document
	"""
	def __init__(self, mongo_addr="doraemon.iis.sinica.edu.tw", db_name="kimo", verbose=True):
		self._db = pymongo.Connection(mongo_addr)[db_name]

		# set logging level
		loglevel = logging.DEBUG if verbose else logging.INFO
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

	def PatternEmotion(self, options={}):
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
		settings.update(options)
		setting_id = self._SaveSettings(settings)

		## sentence-based
		logging.info('start extracting features')

		for sent_mdoc in self._db['sents'].find():
			features = Counter()
			for pat_mdoc in self._db['pats'].find({'usentID': sent_mdoc['usentID']}):

				if 'weighted' in options and options['weighted'] == True:
					features[ pat_mdoc['emotion'] ] += pat_mdoc['weight'] # if weighted
				else:
					features[ pat_mdoc['emotion'] ] += 1

			mdoc = {
				'setting': setting_id,				# <str>
				'usentID': sent_mdoc['usentID'],	# <int>
				'emotion': sent_mdoc['emotion'],	# <str>
				'feature': dict(features), 			# <dict>
			}

			logging.debug('insert pats in usentID: %d' % (sent_mdoc['usentID']) )

			self._db['features.pattern_emotion'].insert(mdoc)

		logging.info('create index on "setting"')
		self._db['features.pattern_emotion'].create_index('setting')
			

if __name__ == '__main__':
	
	Ext = FeatureExtractor(mongo_addr="doraemon.iis.sinica.edu.tw", db_name="kimo", verbose=False)
	
	options = {
		'weighted': True
	}

	Ext.PatternEmotion(options)

