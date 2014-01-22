"""
Load simulation data
"""
import operator
import itertools

class SimuData:
	# An array of dirs
	def __init__(self, data_root, dirlist, params):
		self.data_root = data_root
		self.directories = dirlist
		self.params = params

		# load parameterfiles
		self.run_locations = []
		for d in dirlist:
			paramf = '%s/%s/param.txt'%(data_root, d)
			p = self.load_params(paramf, self.params)						
			loc = [('%s/%s/%s.txt'%(data_root, d, pp[0]), pp[1]) for pp in p]
			self.run_locations.extend(loc)
			self.run_locations.sort(key=operator.itemgetter(1))

	def load_params(self, paramfile, params):
		param_index = []
		f = open(paramfile)
		header = f.readline().strip().split(' ')
		for c in f.readlines():
			strs = c.strip().split(' ')
			pid = strs[0]
			# IDs of the parameter values
			values = tuple('%s=%s'%(p,strs[header.index(p)]) for p in params)	
			param_index.append((pid, values))
		f.close()
		return param_index

	def load_result(self, res_file):
		f = open(res_file)
		mat = [[int(y) for y in x.strip().split(' ')] for x in f.readlines()]
		f.close()
		return mat

	"""
	pamramvalues: [e_labmda=0.1, f_prior=None ...]
	"""
	def get_data(self, paramvalues):
		locs = self.run_locations
		for p in paramvalues:
			locs = itertools.ifilter(lambda x: p in x[1], locs)
		data = []
		qids = []
		for l in locs:
			res = self.load_result(l[0])
			qids = res[0]
			data.extend(res[1:])
		return data, qids		


if __name__ == '__main__':
	dataroot = '/export/data2/fedweb_userstudy/'
	dirlist = ['simulation-official-category', 'simulation-official-category-1', 'simulation-official-category-2', 'simulation-official-category-3']
	params = ['e_lambda', 'f_prior', 'f_model', 'task_length']
	s = SimuData(dataroot, dirlist, params)

	p = ['e_lambda=0.1']
	data, qids = s.get_data(p)
	print len(data)

