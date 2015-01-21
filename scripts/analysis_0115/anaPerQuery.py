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
g_res_basic_dir = conf_g.simulation_basic_dir
g_res_basic_param_file = '%s/param.txt'%g_res_basic_dir

e_res_dir = conf_e.simulation_dir
e_res_param_file = '%s/param.txt'%e_res_dir
e_res_basic_dir = conf_e.simulation_basic_dir
e_res_basic_param_file = '%s/param.txt'%e_res_basic_dir

outputdir = conf_g.output_dir

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
    params = list(itertools.ifilter(lambda x: x[e_idx] == e_lambda, params))
    # group data by plots
    params = sorted(params, key=operator.itemgetter(main_idx[0], main_idx[1]))

    plot_data = {}
    for k, g in itertools.groupby(params, key=operator.itemgetter(main_idx[0], main_idx[1])):
        if k[1] == 'NDCG':
            plot_name = '%s_%s_Prior'%(main_name, k[0])
        elif k[1] == 'None':
            plot_name = '%s_%s_Random'%(main_name, k[0])
        # Now there is only one set of parameters per group
        # Get the per query median of that group
        g = list(g)
        g_data = data[g[0][0]]
        median = dict([(d, np.median(g_data[d])) for d in g_data])
        # Store the data
        plot_data[plot_name] = median
    return plot_data

    
def prepare_data_basic(data, params, main_idx, main_name):
    plot_data = {}
    for p in params:
        # The same data apply to 2 plots
        plot_name1 = '%s_%s_Prior'%(main_name, p[main_idx])
        plot_name2 = '%s_%s_Random'%(main_name, p[main_idx])        
        # Get the median
        g_data = data[p[0]]
        median = dict([(d, np.median(g_data[d])) for d in g_data])
        # store the data in plot_data
        plot_data[plot_name1] = median
        plot_data[plot_name2] = median 
    return plot_data




def makeplot(plotdata_facet, plotdata_basic):
    # Make plot that compares data from facet vs. basic UI
    for plotname in plotdata_facet:
        data = plotdata_facet[plotname]
        data_b = plotdata_basic[plotname]

        # Get difference between median of facet and basic UI
        diff_median = [(data_b[q]-data[q], data_b[q], data[q]) for q in data]
        diff_median.sort(key=operator.itemgetter(0))
        pylab.figure()
        # make bar plot
        X = [i for i in range(len(diff_median))]
        # diff
        Y1 = [d[0] for d in diff_median] 
        # basic
        Y2 = [d[1] for d in diff_median]
        # category
        Y3 = [d[2] for d in diff_median]
    
        pylab.bar(X, Y1, alpha=0.6, color='b', label='Difference')        
        pylab.plot(X, Y2, color='r', label='Basic')
        pylab.plot(X, Y3, color='g', label="RLR")
        
        if abs(Y1[0]) < max(Y1[-1], max(Y2)):
            pylab.legend(loc=2) 
        else:
            pylab.legend(loc=4)


        # Save plot
        outfile = '%s/%s.png'%(outputdir, plotname)
        pylab.savefig(outfile)
    
        # Correlation analysis
        r, p = stats.pearsonr(Y1, Y2)
        print '%s, basic vs. diff r:%s, p-value:%s'%(plotname, r, p)
        r, p = stats.pearsonr(Y1, Y3)
        print '%s, RLR vs. diff r:%s, p-value:%s'%(plotname, r, p)



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
    g_D = prepare_data(g_data, g_params, (9, 7), 'moves')
    e_D = prepare_data(e_data, e_params, (5, 7), 'tasklength')
    g_D_basic = prepare_data_basic(g_data_basic, g_params_basic, 5, 'moves')
    e_D_basic = prepare_data_basic(e_data_basic, e_params_basic, 4, 'tasklength')

    # Make plots
    makeplot(g_D, g_D_basic)
    makeplot(e_D, e_D_basic)
    pylab.show()

