# -*- coding: utf-8 -*-

import pymongo
import logging
import os


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
		except KeyError:
			logging.error('mongo_addr and db_name are both necessary for create a mongo connection')

	def build_f():
		"""
		For all kinds of TF
		Def:
			f(d,t): the number of occurrences of term t in document d
		"""
		fn = os.path.join(self._cache_root, 'f.pkl')
		if not os.path.exists(fn):
			# calculate F
			# ...
			pickle.dump(self.f, open(fn, 'wb'), pickle.HIGHEST_PROTOCOL)
		else:
			self.f = pickle.load(open(fn, 'rb'))

	def build_n():
		"""
		For IDF-2, IDF-3
		Def:
			n(t): entropy of term t in D (the universe of documents)
				  --> sum(f(d,t) / F(t)*ln(f(d,t)/F(t))) for d in D
				  where F(t): the number of documents in D that contain term t
		"""
		fn = os.path.join(self._cache_root, 'n.pkl')
		if not os.path.exists(fn):
			# calculate n
			# ...

			pickle.dump(self.n, open(fn, 'wb'), pickle.HIGHEST_PROTOCOL)
		else:
			self.n = pickle.load(open(fn, 'rb'))

	def build_F():
		"""
		For IDF-1 (directly used), IDF-2 (in n(t)), IDF-3 (in n(t))
		Def:
			F(t): the number of documents in D that contain term t
		"""
		fn = os.path.join(self._cache_root, 'F.pkl')
		if not os.path.exists(fn):
			# calculate F
			# ...
			pickle.dump(self.F, open(fn, 'wb'), pickle.HIGHEST_PROTOCOL)
		else:
			self.F = pickle.load(open(fn, 'rb'))


	def build_d():
		"""
		For TF-2, TF-3
		Def:
			|d|: cardinality (length) of d
			|delta d|: average document length in D
		"""
		fn = os.path.join(self._cache_root, 'd.pkl')
		if not os.path.exists(fn):
			# calculate F
			# ...
			pickle.dump(self.d, open(fn, 'wb'), pickle.HIGHEST_PROTOCOL)
		else:
			self.d = pickle.load(open(fn, 'rb'))


if __name__ == '__main__':


	tfidf = TFIDFModel(mongo_addr="doraemon.iis.sinica.edu.tw", db_name="kimo")
