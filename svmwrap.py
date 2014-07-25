# -*- coding: utf-8 -*-

svm_root='/tools/libsvm/python'

import sys, pymongo, logging
sys.path.append(svm_root)
import svmutil

class svmwrap(object):
	"""
	1. feature vectors and problems
		1.1 format x, y: 	self.format_xy()
		1.2 save x,y: 		self.svm_save_problem()
		1.3 form problem: 	svmutil.svm_problem()
		1.4 normalization: 	self.svm_feature_normalize()
	2. svm training
		2.1 set parameter: 	svmutil.svm_parameter()
		2.2 training: 		svmutil.svm_train()
		2.3 save model: 	svmutil.svm_save_model()
	3. svm prediction
	4. svm evaluation
	"""
	def __init__(self, mongo_addr="doraemon.iis.sinica.edu.tw", db_name="kimo", verbose=True):
		self._db = pymongo.Connection(mongo_addr)[db_name]
		# set logging level
		loglevel = logging.DEBUG if verbose else logging.INFO
		logging.basicConfig(format='[%(levelname)s] %(message)s', level=loglevel)

	def genFeatureIndex(self):
		self.feature_idx = { x['emotion']:int(x['emoID']) for x in self._db['emotions'].find({'label':'kimo'})}

	def format_xy(self, setting_id):
		from bson.objectid import ObjectId
		"""
		read from mongodb > features.[feature_name]
		collect instance features --> x and gold answers --> y
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
		logging.debug('Formatting x, y from %s with setting: %s' % (feature_name, setting_id))
		y, x = [], [] # y, x = [1,-1], [{1:1, 3:1}, {1:-1,3:-1}]
		for i, mdoc in enumerate(self._db[collection_name].find({'setting': setting_id})):
			x.append( {self.feature_idx[fn]:fv for fn,fv in mdoc['feature'].items()} ) # fetch feature{name, value} --> feature{id, value}
			y.append(mdoc['emotion'])
			logging.debug('Add %d instance.' % (i))

		return (x, y)

	def svm_save_problem(x,y, problem_file_name=False):
		"""
		save x, y to a plain-text file in svm-format
		"""
		## auto-generate problem
		if not problem_file_name:
			problem_file_name = '.'.join([self.setting_id, 'problem']) ## 53d0a63cd4388c1b77a25f19.problem

		## check if the destination file already existed
		if os.path.exists(problem_file_name):
			logging.warn('')
			return False

		## make sure destination folder existed
		dirname = os.path.dirname(problem_file_name)
		if dirname and not os.path.exists(dirname): os.makedirs(dirname)

		with open(problem_file_name, 'w') as fw:
			for label, insts in zip(y,x):
				## Dense data
				## insts is a tuple/list: e.g., [[1, 2, -2], [2, -2, 2]]
				if type(insts) in (list, tuple):
					# ...
					pass

				## Sparse data
				## insts is a dictionary: e.g., [{0:1, 1:2, 2:-2}, {0:2, 1:-2, 2:2}]
				elif type(insts) is dict:
					insts_str = map(lambda x: str(x[0])+':'+str(x[1]), sorted([( self.feature_idx[f], fv) for f,fv in insts.items() ], key=lambda x:int(x[0])))
					label_str = str(label)
					line = ' '.join([label_str, insts_str]) + '\n'
				fw.write(line)
		return True

if __name__ == '__main__':
	
	from svmwrap import svmwrap

	sw = svmwrap(verbose=True)

	sw.genFeatureIndex() ## get feature_idx

	# feature_name="features.pattern_emotion", 
	(x, y) = sw.format_xy(setting_id="53d0a63cd4388c1b77a25f19")

	sw.svm_save_problem(x, y)

			

