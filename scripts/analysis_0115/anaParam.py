# This script generates plots that showing the influence of 
# user parameters on their effort/gain.

import load_data as ld
import itertools
import numpy as np
import operator
import pylab
from matplotlib import rc
from scipy import stats

# DIRs of simulation results

# For 
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


