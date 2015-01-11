#comparing systems: anaPerQuery.py

#per-query: score@basic vs. score@facet - score@basic
#3Relation between difficulty of a query with a basic interface and its benefit from using a faceted interface.
import load_data as ld
import itertools
import numpy as np
import operator
import pylab
from matplotlib import rc
from scipy import stats
# Import the right config for the case: gain or effort
from  Configure import perQueryGain as conf_g
from Configure import perQueryEffort as conf_e
	
rc('font', **{'size': 20})

#Paths
g_res_dir = conf_g.simulation_dir
g_res_param_file = '%s/param.txt'%g_res_dir
g_res_basic = conf_g.simulation_basic_dir

e_res_dir = conf_e.simulation_dir
e_res_param_file = '%s/param.txt'%e_res_dir
e_res_basic = conf_e.simulation_basic_dir

outputdir = conf_g.output_dir

# Fix the e_lambda parameter
e_lambda = 0.1
e_idx = 8

def prepare_data(data, params, main_idx, main_name):
	"""
	# preprare data for gain based plots
	# gain experiment parameters:
	#['index', 'page_size', 'gain_type', 'ndcg_k',
	# 'e_model','task_length', 'f_model', 'f_prior',
	# 'e_lambda', 'moves', ]
	# effort parameters are the same without "move"
	"""
	# group data by plots
	
	# lambda is set to 0.01

	params = sorted(params, key=operator.itemgetter(main_idx))
	for k, g in itertools.groupby(params, lambda x: x[main_idx]):
		plot_name = '%s_%s'%(main_name, k)
	

	
def prepare_basic_data(data, params, main_idx, main_name):
	



if __name__ == '__main__':
	# Load data	
	# parameter specifications
	g_params = ld.load_parameter_record(g_res_param_file)
	e_params = ld.load_parameter_record(e_res_param_file)
	
	# data corresponding to each parameter setting
	g_data = ld.load_data(g_res_dir, g_params)
	e_data = ld.load_data(e_res_dir, e_params)

	# Format data for plots
	# main indx for gain is move(9), for effort is task_length(5)
	g_D = prepare_data(g_data, g_params, (9, 7), 'moves')
	e_D = prepare_data(e_data, e_params, (5, 7), 'tasklength')

	# Make plots
	makeplot(g_D)
	makeplot(e_D)
	pylab.show()


