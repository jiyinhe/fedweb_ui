"""
Load simulation data
"""
class SimuData:
	# An array of dirs
	def __init__(dirlist)




def load_params(paramfile, params):
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

def load_result(res_file):
	f = open(res_file)
	mat = [[int(y) for y in x.strip().split(' ')] for x in f.readlines()]
	f.close()
	return mat

