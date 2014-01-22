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
import pylab


#dataroot = '/export/data1/he/fedweb_userstudy/fedweb_ui/'
dataroot = '../../'
datadir = '%s/data/simulation-official-category/'%dataroot
paramfile = '%s/%s'%(datadir, 'param.txt')

basic_datadir = '%s/data/simulation_basic/'%dataroot
paramfile_basic = '%s/%s'%(basic_datadir, 'param.txt')

outputdir = 'data_plot/'

# Parameters we are going to look at
params = {
	'task_length': [1, 10, -1],
	'f_model': ['static', 'dynamic'], 
	'f_prior': ['None', 'NDCG'],
	'e_lambda': [1, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001]
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

# Get the comparison between basic and advance UI
# D: (param setting, diff)  
# where diff is a matrix: rows are simulation runs,
# columns are queries
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

	
def load_data(param_data, data_dir):
	D = []
	qids = []
	for p in param_data:
		pid = p[0]
		res = load_result('%s/%s.txt'%(data_dir, pid))
		qids = res[0:]
		data = np.array(res[1:])
		D.append((p[1], data))
	return dict(D), qids


# Aggregate all results, and see per query, the difference between two interfaces
def query_impact(D, B):
	Data = []
	keys = D.keys()
	for task in params['task_length']:
		key_b = ('task_length=%s'%task, )
		data_B = B[key_b]
		for n in params['f_prior']:
			for d in params['f_model']:
				for e in params['e_lambda']:
					K = list(itertools.ifilter(lambda x: 'task_length=%s'%task in x and 'f_prior=%s'%n in x, keys))
					data = []
					for k in K:
						diff = D[k]-data_B
						data.extend(list(diff))
					data = np.array(data).astype('float')
					mean_diff = np.mean(data, 0)
					sd_diff = np.std(data, 0)
					p = []
					# for each mean_diff, check if they are significant
					for i in range(mean_diff.shape[0]):
						print data[:, i]
						norm, norm_p = stats.normaltest(data[:, i])
						t, p = stats.ttest_1samp(data[:, i], 0)	
						print i, mean_diff[i], sd_diff[i], p, norm_p



# impact of lambda
# separate NDCG, None
def impact_lambda(D, B):
	Data = []
	keys = D.keys()
	for t in params['task_length']:
		key_b = ('task_length=%s'%t, )
		data_B = B[key_b]
		for n in params['f_prior']:
			for e in params['e_lambda']:
				K = list(itertools.ifilter(lambda x: 'task_length=%s'%t in x and 'e_lambda=%s'%e in x and 'f_prior=%s'%n in x, keys))
				data = 0 
				for k in K:
					data += D[k]		
				data = data/float(len(K))

				mean_data = np.mean(data, 0)
				baseline = data_B[0]
	
				mean_diff, T, p_value = paired_test(mean_data, baseline)
				print mean_diff, p_value

if __name__ == '__main__':
	param_a = load_params(paramfile, params)
	param_b = load_params(paramfile_basic, params_basic)	
	D, qids = load_data(param_a, datadir)
	B, qids = load_data(param_b, basic_datadir)
#	impact_lambda(D, B)
	print query_impact(D, B)
