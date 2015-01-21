#comparing systems: anaPerQuery.py
# use user parameters instead  

#per-query: score@basic vs. score@facet - score@basic
#3Relation between difficulty of a query with a basic interface and its benefit from using a faceted interface.
import sys
sys.path.append('../trec_eval')
import trec_util, NDCG

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
from Configure import generalDir, util
from math import log
	
rc('font', **{'size': 20})

#Paths
g_res_dir = conf_g.simulation_dir
g_res_param_file = '%s/param.txt'%g_res_dir
g_res_basic_dir = conf_g.simulation_basic_dir
g_res_basic_param_file = '%s/param.txt'%g_res_basic_dir

e_res_dir = conf_e.simulation_dir
e_res_param_file = '%s/param.txt'%e_res_dir
e_res_basic_dir = conf_e.simulation_basic_dir
e_res_basic_param_file = '%s/param.txt'%e_res_basic_dir

outputdir = conf_g.output_dir
runfile = generalDir.runfile
qrelsfile = generalDir.qrelsfile
categoryfile = generalDir.categoryfile

u = util()

# Fix the e_lambda parameter
e_lambda = '0.01'
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
    # lambda is set to 0.1, first get data for fixed param
    # comment this out for user parameters
    #params = list(itertools.ifilter(lambda x: x[e_idx] == e_lambda, params))
    # group data by plots
    params = sorted(params, key=operator.itemgetter(main_idx[0], main_idx[1]))

    plot_data = {}
    for k, g in itertools.groupby(params, key=operator.itemgetter(main_idx[0], main_idx[1])):
        plot_name = '%s_%s_User'%(main_name, k[0])
        # Now there is only one set of parameters per group
        # Get the per query median of that group
        g = list(g)
        g_data = data[g[0][0]]
        median = dict([(d, np.median(g_data[d])) for d in g_data])
        # Store the data
        plot_data[plot_name] = median
        print k, plot_name
    return plot_data

	
def prepare_data_basic(data, params, main_idx, main_name):
    plot_data = {}
    for p in params:
        # The same data apply to 2 plots
#        plot_name1 = '%s_%s_Prior'%(main_name, p[main_idx])
#        plot_name2 = '%s_%s_Random'%(main_name, p[main_idx])
        plot_name = '%s_%s_User'%(main_name, p[main_idx])
        # Get the median
        g_data = data[p[0]]
        median = dict([(d, np.median(g_data[d])) for d in g_data])
        # store the data in plot_data
        plot_data[plot_name] = median
        print plot_name
    return plot_data


# compute the average pairwise overlap between
# lists
def sublist_overlap(sublists, topX):
    overlap = [] 
    for i in range(0, len(sublists)-1):
        list1 = set([d[0] for d in sublists[i][0:topX]])
        for j in range(i+1, len(sublists)):
            list2 = set([d[0] for d in sublists[j][0:topX]])
            overlap.append(len(list1.intersection(list2)))
    return sum(overlap)/float(len(overlap))

# KL divergence of distribution of relevant docs
# among sublists from a uniform distribution
# We remove the first list from ths sublists, 
# as it is the original list. 
def sublist_entropy(sublists):
    p_random = 1./len(sublists[1:])
    rel_counts = [sum([int(s[2]>0) for s in sub]) for sub in sublists[1:]] 
    tot_rel = sum(rel_counts)
    H_P = 0
    H_PQ = 0
    for count in rel_counts:
        p_rel = float(count)/tot_rel
        if p_rel > 0:
            H_P += - (p_rel * log(p_rel))
            H_PQ += -(p_rel * log(p_random))
    return H_PQ - H_P 


# Prepare data to describe the properties of the sublists
# hypothesis:
# - sublist needs to contain diverse relevant info, and 
# to be able to seperate relevant versus non-relevant info
# to be useful.   
def prepare_data_sublists():
    run = trec_util.load_TREC_run(runfile)		
    qrels = trec_util.load_qrels(qrelsfile)
    judged_list = trec_util.judged_ranklist(run, qrels)
    categories = u.load_categories(generalDir.categoryfile)

    facets_data = {}
    for q in run:
        docs = q[1]
        if not q[0] in judged_list:
            continue
        judge = judged_list.get(q[0])
        sublists, B, G = u.create_sublists(docs, judge, categories)
        # Overlap didn't show any correlation with benefit
        # overlap = {10: sublist_overlap(sublists, 10),
        #        20: sublist_overlap(sublists, 20),
        #        -1: sublist_overlap(sublists, -1)}
        
        entropy = sublist_entropy(sublists)
        facets_data[q[0]] = entropy  
    return facets_data 

def correlate(plotdata_facet, plotdata_basic, data_sublists):
    # Make plot that compares data from facet vs. basic UI
    for plotname in plotdata_facet:
        # skip the random users
        if 'Random' in plotname:
            continue
        data = plotdata_facet[plotname]
        print plotdata_basic.keys()
        data_b = plotdata_basic[plotname]

        # Get difference between median of facet and basic UI
        diff_median = [(data_b[q]-data[q], data_b[q], data[q], data_sublists[q]) for q in data]
        diff_median.sort(key=operator.itemgetter(0))
        # make bar plot
        X = [i for i in range(len(diff_median))]
        # diff
        Y1 = [d[0] for d in diff_median] 
        # basic
        Y2 = [d[1] for d in diff_median]
        # facet
        Y3 = [d[2] for d in diff_median]
        # sublist properties
        # overlap in top 10
        #Y4 = [d[3][10] for d in diff_median]
        # overlap in top 20
        #Y5 = [d[3][20] for d in diff_median]
        # overlap in all
        #Y6 = [d[3][-1] for d in diff_median]

        # entropy
        Y7 = [d[3] for d in diff_median
]
        # Correlation analysis
        print "=================================================="
        print 'We only focus on Prior case, Random cases were commented out.'
        r, p = stats.pearsonr(Y1, Y2)
        print 'diff vs. basic -', 
        print '%s, r:%s, p-value:%s'%(plotname, r, p)
        r, p = stats.pearsonr(Y2, Y3)
        print 'basic vs. RLR -', 
        print '%s, r:%s, p-value:%s'%(plotname, r, p)

        print 'diff vs. overlap 10, 20, All', 
        print 'No correlation was found' 
        print 'Code was commented out. '
        #r, p = stats.pearsonr(Y1, Y4)
        #print 'diff vs. overlap10 -', 
        #print '%s, r:%s, p-value:%s'%(plotname, r, p)
        #r, p = stats.pearsonr(Y1, Y5)
        #print 'diff vs. overlap20 -', 
        #print '%s, r:%s, p-value:%s'%(plotname, r, p)
        #r, p = stats.pearsonr(Y1, Y6)
        #print 'diff vs. overlap All -', 
        #print '%s, r:%s, p-value:%s'%(plotname, r, p)
 
        r, p = stats.pearsonr(Y1, Y7)
        print "diff vs. sublist entropy",
        print '%s, r:%s, p-value:%s'%(plotname, r, p)
 

        # make a plot for the relation between diff, basic, and sublist entropy
        # X - basic(Y2), Y - entropy(Y7), diff>0: red; diff<0: blue; diff == 0: circle
        pylab.figure()
        dots = []
        for i in range(len(Y1)):
            # improve over basic
            if (Y1[i] > 0 and 'task' in plotname) or (Y1[i]<0 and 'moves' in plotname):
                marker = 'ro'
                label = 'Improved'
            # worse than basic
            elif (Y1[i] < 0 and 'task' in plotname) or (Y1[i]>0 and 'moves' in plotname):
                marker = 'b^'
                label = 'Worse'
            else:
                marker = 'k+'
                label = 'No difference'
            pylab.plot([Y2[i]], [Y7[i]], marker, markersize=10, label=label)

        pylab.savefig('plots/diff_basic_entropy/%s.png'%plotname)
        

 
        # Get the improvement
        #print 'diff>0:', sum([int(diff[0]>0) for diff in diff_median])
        #print 'diff=0:', sum([int(diff[0]==0) for diff in diff_median])
        #print 'diff<0:', sum([int(diff[0]<0) for diff in diff_median])
        



if __name__ == '__main__':
    # Load data	
    # parameter specifications
    g_params = ld.load_parameter_record(g_res_param_file)
    e_params = ld.load_parameter_record(e_res_param_file)
    g_params_basic = ld.load_parameter_record(g_res_basic_param_file)
    e_params_basic = ld.load_parameter_record(e_res_basic_param_file)	

    # data corresponding to each parameter setting
    g_data = ld.load_data(g_res_dir, g_params)
    e_data = ld.load_data(e_res_dir, e_params)
    g_data_basic = ld.load_data(g_res_basic_dir, g_params_basic)
    e_data_basic = ld.load_data(e_res_basic_dir, e_params_basic)
	
    # Format data for plots
    # main indx for gain is move(9), for effort is task_length(5)
    #g_D = prepare_data(g_data, g_params, (9, 7), 'moves')
    # for user parameter
    g_D = prepare_data(g_data, g_params, (8, 7), 'moves')
 
    e_D = prepare_data(e_data, e_params, (5, 7), 'tasklength')
    # for user parameter
    g_D_basic = prepare_data_basic(g_data_basic, g_params_basic, -1, 'moves')
    e_D_basic = prepare_data_basic(e_data_basic, e_params_basic, 4, 'tasklength')



    # compute properties of per query sublist
    data_sublists = prepare_data_sublists()


    # compute correlations
    correlate(g_D, g_D_basic, data_sublists)
    correlate(e_D, e_D_basic, data_sublists)
    pylab.show()

