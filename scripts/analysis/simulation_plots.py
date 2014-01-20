"""
analyse the simualtion results
and generate data for plots, per task type (1, 10, -1)

1. impact of lambda
2. impact of prior
3. impact of priorxlambda
4. impact of dynamic vs. static

"""
import simulation_analysis as sa
import numpy as np
import itertools
from scipy import stats

dataroot = '/export/data1/he/fedweb_userstudy/fedweb_ui/'
# dataroot = '../../'
datadir = '%s/data/simulation3'%dataroot
paramfile = '%s/%s'%(datadir, 'param.txt')

basic_datadir = '%s/data/simulation_basic/'%dataroot
paramfile_basic = '%s/%s'%(basic_datadir, 'param.txt')

# Parameters we are going to look at
params = {
	'task_length': [1, 10, -1],
	'f_model': ['static', 'dynamic'], 
	'f_prior': ['None', 'NDCG'],
	'e_lambda': [5, 1, 0.5, 0.25, 0.05, 0.01]
}

params_basic = {
	'task_length': [1, 10, -1],
}


param_index = [] 

def paired_test(x, y):
	mean_diff = np.mean(x-y)	
	T, p = stats.wilcoxon(x, y)
	return mean_diff, T, p

def ranksum_test(x, y):
	mean_diff = np.mean(x)-np.mean(y)
	Z, p = stats.ranksums(x, y)
	return mean_diff, Z, p


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



if __name__ == '__main__':
	params_a = load_params(paramfile, params)
	params_b = load_params(parafile_basic, params_basic)	
	print params_a
	print params_b













