"""
 Anaylizing simulation results:

 Under each condition, which queries will benefit from faceted interface

"""
import numpy as np
import itertools
import pylab as pl

datadir = '../../data/simulation3'
paramfile = '%s/%s'%(datadir, 'param.txt')

basic_datadir = '../../data/simulation_basic/'
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

# Get the comparison between basic and advance UI
def get_diff_data(param_a, param_b):
	qids = []
	baseline = []
	for pb in param_b:
		pid = pb[0]
		resfile = '%s/%s.txt'%(basic_datadir, pid)
		data = load_result(resfile)
		qids = data[0]
		data = np.array(data[1:])
		baseline.append((pb[1][0], data))
	baseline = dict(baseline)
	#print 'Computing diff'
	
	D = []
	for pa in param_a:
		pid = pa[0]
		resfile = '%s/%s.txt'%(datadir, pid)
		data = np.array(load_result(resfile)[1:])
		""" get corresponding baseline based on  task_length """
		task_length = pa[1][-1]
		b = baseline[(task_length)]			
		diff = data - b
		D.append((pa[1], diff))
	return D, baseline, qids

def query_performance_per_param(qids, D, B):
	header = [d.split('=')[0] for d in D[0][0]]
	header.extend(['%s'%q for q in qids])
	print '\t'.join(header)

	for p in B:
		values = ['', '', '', p.split('=')[1]]	
		values.extend(['%s'%s for s in B[p][0]])	
		print '\t'.join(values)
	
	for p in D:
		# The parameter values
		line = [x.split('=')[1] for x in p[0]]
		# Diff median
		diff = np.median(p[1], axis=0)
		line.extend(['%s'%d for d in diff])	
		print '\t'.join(line)
	

if __name__ == '__main__':
	param_a = load_params(paramfile, params)
	param_b = load_params(paramfile_basic, params_basic)
	D, B, qids = get_diff_data(param_a, param_b)
	
	""" do analysis"""
	""" Difference per param """	
	query_performance_per_param(qids, D, B)

