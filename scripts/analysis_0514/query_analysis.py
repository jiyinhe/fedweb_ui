""" 
Analyse the per-query performance of simulated runs.  It asks two questions:
1. For which queries, faceted interface is better, if users can choose good
facets?  
2. For which queries, faceted interface is better, even if users cannot
choose?  
"""
import load_data as ld
import itertools
import numpy as np
import operator
import pylab
from matplotlib import rc
from scipy import stats

# DIRs of simulation results
facet_dir='../../data/simulation/'
basic_dir = '../../data/simulation_basic/'
outputdir = 'plots/'

#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
#rc('text', usetex=True)
rc('font', **{'size': 22})

# load data
def load_data(facet_dir, basic_dir):
    pa_facet = ld.load_parameter_record('%s/param.txt'%(facet_dir))
    data_facet = ld.load_data(facet_dir, pa_facet)
    pa_basic = ld.load_parameter_record('%s/param.txt'%(basic_dir))
    data_basic = ld.load_data(basic_dir, pa_basic)

    return pa_facet, data_facet, pa_basic, data_basic

# check per query performance
def perquery_compare(pa_facet, data_facet, pa_basic, data_basic, user_type): 	
    # Fixed parameters
    e_lambda = 0.01
    items = list(itertools.ifilter(lambda x: x[7] == user_type and x[8] == '%s'%e_lambda, pa_facet))
    for idx in items:
        index = idx[0]
	task = idx[5] 
        f_data = data_facet[index]
        # Find corresponding basic data
        basic_index = list(itertools.ifilter(lambda x: x[4] == task, pa_basic))[0][0]
        b_data = data_basic[basic_index] 

	# Compute the difference between the median and the basic effort
	diff_median = [(b_data[q]-np.median(f_data[q]), q) for q in f_data]
	diff_median.sort(key=operator.itemgetter(0))
        Y1 = [y[0] for y in diff_median]
	Y2 = [b_data[q[1]] for q in diff_median]	
	X = range(len(diff_median))

	pylab.figure()
	# make bar plot
	pylab.bar(X, Y1, alpha=0.6, color='b', label='Difference')		
	# plot basic effort on top
        pylab.plot(X, Y2, color='r', label='Basic')

        if abs(Y1[0]) < max(Y1[-1], max(Y2)):
	    pylab.legend(loc=2) 
        else:
            pylab.legend(loc=4)

	# Save plot
        outfile = '%s/%s_%s.png'%(outputdir, task, user_type)
        pylab.savefig(outfile)
	
	# Correlation analysis
        r, p = stats.pearsonr(Y1, Y2)
        print 'task type: %s, user type: %s, r:%s, p-value:%s'%(task, user_type, r, p)

    pylab.show()

if __name__ == '__main__':
    pa_facet, data_facet, pa_basic, data_basic = load_data(facet_dir, basic_dir)
    # Random user
    random_user = 'None'
    perquery_compare(pa_facet, data_facet, pa_basic, data_basic, random_user)

    # Good user
    ndcg_user = 'NDCG'
    perquery_compare(pa_facet, data_facet, pa_basic, data_basic, ndcg_user)





