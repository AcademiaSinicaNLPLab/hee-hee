# -*- coding: utf-8 -*-

import pymongo
# db = pymongo.Connection(config.mongo_addr)[config.db_name]

class TFIDFModel(object):
	"""
	"""
	def __init__(self, **kwargs):
		## check(and create if not existed) TFIDF cache path

		self.cache_root = 'TFIDFModel' if 'cache_root' not in kwargs else kwargs['cache_root']
		if not os.path.existed(self.cache_root): os.mkdir(self.cache_root)
		# T: the universe of terms
		# D: the universe of documents

	def build_f():
		"""
		For all kinds of TF
		Def:
			f(d,t): the number of occurrences of term t in document d
		"""
		fn = os.path.join(self.cache_root, 'f.pkl')
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
		fn = os.path.join(self.cache_root, 'n.pkl')
		if not os.path.exists(fn):
			# calculate n
			# ...

			pickle.dump(self.n, open(fn, 'wb'), pickle.HIGHEST_PROTOCOL)
		else:
			self.n = pickle.load(open(fn, 'rb'))

		# entropy of term t in D

	def build_F():
		"""
		For IDF-1 (directly used), IDF-2 (in n(t)), IDF-3 (in n(t))
		Def:
			F(t): the number of documents in D that contain term t
		"""
		fn = os.path.join(self.cache_root, 'F.pkl')
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
		fn = os.path.join(self.cache_root, 'd.pkl')
		if not os.path.exists(fn):
			# calculate F
			# ...
			pickle.dump(self.d, open(fn, 'wb'), pickle.HIGHEST_PROTOCOL)
		else:
			self.d = pickle.load(open(fn, 'rb'))


if __name__ == '__main__':
	tfidf = TFIDFModel()
