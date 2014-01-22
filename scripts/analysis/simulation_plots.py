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

import SimuData as simd
import itertools

dataroot = '/export/data2/fedweb_userstudy/'
#dirlist = ['simulation-official-category', 'simulation-official-category-1', 'simulation-official-category-2', 'simulation-official-category-3']
dirlist = ['simulation-official-category-1']
#params = ['e_lambda', 'f_prior', 'f_model', 'task_length']

outpudir = 'data/'
params = {
	'e_lambda': [0.1],
	'f_prior': ['None', 'NDCG'],
	'f_model': ['static', 'dynamic'],
	'task_length': [10]
}

s = simd.SimuData(dataroot, dirlist, params.keys())

"""
Plot per_query performance
f_prior: NDCG vs. None
fixed dynamic vs. stactic
fixed task_length
fixed e_lambda 
"""
def plot_per 





if __name__ == '__main__':
