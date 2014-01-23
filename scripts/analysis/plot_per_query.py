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
from scipy import stats
import pylab
import sys
import SimuData as simd
import itertools
import operator
#dataroot = '/export/data2/fedweb_userstudy/'
dataroot = '../../data'
dirlist = ['simulation-official-category', 'simulation-official-category-1', 'simulation-official-category-2', 'simulation-official-category-3']
#dirlist = ['simulation-official-category-1']
#params = ['e_lambda', 'f_prior', 'f_model', 'task_length']

baseline_dir = ['simulation_basic']

outpudir = 'data/'
params = {
	'e_lambda': [1, 0.1, 0.01, 0.001, 0.5, 0.05, 0.005],
	'f_prior': ['None', 'NDCG'],
	'f_model': ['static', 'dynamic'],
	'task_length': [0, 10, -1]
}


s = simd.SimuData(dataroot, dirlist, params.keys())


def load_baseline(t):
	s = simd.SimuData(dataroot, baseline_dir, {'task_length': [0, 10, -1]})	
	data, qids = s.get_data(['task_length=%s'%t])
	return np.array(data)

"""
plots per_query performance
f_prior: NDCG vs. None
fixed dynamic vs. stactic
fixed task_length
fixed e_lambda 
"""
def prior_per_query(e, fm, fp, t):
	pa = ['e_lambda=%s'%e, 'f_prior=%s'%fp, 'f_model=%s'%fm, 'task_length=%s'%t]			
	data, qids = s.get_data(pa)
	data = np.array(data, dtype=float)
	baseline = load_baseline(t)
	
	# get difference
	diff = baseline - data
	median = np.median(data, axis=0)
	upper_qt = np.percentile(data, 75, axis=0)
	lower_qt = np.percentile(data, 25, axis=0)
		
	# A bar chart
	pylab.figure()
	ids = [(i, baseline.T[i]) for i in range(len(baseline.T))]
	ids.sort(key=operator.itemgetter(1))
	idx = [i[0] for i in ids]

	X = range(1, len(median)+1)
	width = 0.3
	#pylab.bar(X, median, width, color='b', yerr=[median-lower_qt, upper_qt-median])
	diff = diff[:, idx]

	pylab.boxplot(diff)
	pylab.axhline(0, color='black')

	bl = baseline.T[idx]
	pylab.plot(X, bl, 'r')

	median = median[:, idx]
	pylab.plot(X, median, 'g')
	pylab.title(fm)
#	bp = pylab.boxplot(data)
#	pylab.setp(bp['boxes'], color='green')
#	pylab.setp(bp['whiskers'], color="green")


if __name__ == '__main__':
	if len(sys.argv)<4:
		print 'usage_python simulation_plot.py parameters'
		print 'parameters:'
		print 'e_lambda f_model(static/dynamic) f_prior(None/NDCG) task_length(1, 10, -1)'
		sys.exit()

	e = sys.argv[1]
	fm = sys.argv[2]
	fp = sys.argv[3]
#	t = sys.argv[4]	
	for t in [1, 10, -1]:
		for fm in ['dynamic', 'static']:
			prior_per_query(e, fm, fp, t)
	pylab.show()



