# This script generates plots that showing the influence of 
# user parameters on their effort/gain.

import load_data as ld
import itertools
import numpy as np
import operator
import pylab
from scipy import stats
from matplotlib import rc

# Import the right config for the case: gain or effort
from  Configure import paramEffectGain as conf_g
from Configure import paramEffectEffort as conf_e
    

#Paths
g_res_dir = conf_g. simulation_dir
g_res_param_file = '%s/param.txt'%g_res_dir
e_res_dir = conf_e.simulation_dir
e_res_param_file = '%s/param.txt'%e_res_dir
outputdir = conf_g.output_dir

#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
#rc('text', usetex=True)
rc('font', **{'size': 20})

def data_gain(data, params):
    """
    # preprare data for gain based plots
    # gain experiment parameters:
    #['index', 'page_size', 'gain_type', 'ndcg_k',
    # 'e_model','task_length', 'f_model', 'f_prior',
    # 'e_lambda', 'moves', ]
    """
    # Main group: by moves
    # The index of the parameter for the main groups
    idx = 9
    main_group = {}
    params.sort(key=operator.itemgetter(idx))
    # loop over main groups, plot individual plots
    for k, g in itertools.groupby(params, lambda x: x[idx]):
        main_name = 'moves_%s'%k
        # now group by f_prior
        idx_f = 7
        # index of the lambda values
        idx_e = 8
        g = sorted(list(g), key=operator.itemgetter(idx_f))
        legend_group = {}    
        for key, group in itertools.groupby(g, lambda x: x[idx_f]):
            legend_name = 'NDCG' if key == 'NDCG' else 'Random'
            group = sorted(list(group), key=operator.itemgetter(idx_e), reverse=True)
            data_group = []
            e_group = []
            for g in group:
                group_data = data[g[0]]
                # Now aggregate data in this group
                # We take all data regardless queries
                all_data = []
                for d in group_data: 
                    all_data += group_data[d]
                
                # Try an extra normalisation step
                # Average effort/gain per doc/move
                all_data = [float(d)/float(k) for d in all_data]

                # Get median, lower, higher quantiles
                median = np.median(all_data)        
                lower = np.percentile(all_data, 25)
                higher = np.percentile(all_data, 75)
                data_group.append((median, lower, higher))        
                e_group.append(g[idx_e])
            legend_group[legend_name] = [e_group, data_group]
        main_group[main_name] = legend_group
    return main_group

def data_effort(data, params):
    """
    # preprare data for effort based plots
    # effort experiment parameters:
    #['index', 'page_size', 'gain_type', 'ndcg_k',
    # 'e_model','task_length', 'f_model', 'f_prior',
    # 'e_lambda',]
    """
    # Main group: by moves
    # The index of the parameter for the main groups
    idx = 5
    main_group = {}
    params.sort(key=operator.itemgetter(idx))
    # loop over main groups, plot individual plots
    for k, g in itertools.groupby(params, lambda x: x[idx]):
        main_name = 'task%s_e_fp'%k
        # now group by f_prior
        idx_f = 7
        # index of the lambda values
        idx_e = 8
        g = sorted(list(g), key=operator.itemgetter(idx_f), reverse=True)
        legend_group = {}    
        for key, group in itertools.groupby(g, lambda x: x[idx_f]):
            legend_name = 'NDCG' if key == 'NDCG' else 'Random'
            group = sorted(list(group), key=operator.itemgetter(idx_e), reverse=True)
            data_group = []
            e_group = []
            for g in group:
                group_data = data[g[0]]
                # Now aggregate data in this group
                # We take all data regardless queries
                all_data = []
                for d in group_data:
                    all_data += group_data[d]
                
                # Try an extra normalisation step
                # Average effort/gain per doc/move
                #all_data = [float(d)/float(k) for d in all_data]

                # Get median, lower, higher quantiles
                median = np.median(all_data)        
                lower = np.percentile(all_data, 25)
                higher = np.percentile(all_data, 75)
                data_group.append((median, lower, higher))        
                e_group.append(g[idx_e])
            legend_group[legend_name] = [e_group, data_group]
        main_group[main_name] = legend_group
    return main_group




def makeplot(D):
    # Set line properties
    colors = ['b', 'r']
    linestyles = ['-', '--']
    hatches = ['', '/']
    markers = ['x', '+']
    # Each plot corresponds to a move value
    for main_group in D:
        plot_name = main_group
        plot_data = D[main_group]
        legends = sorted(plot_data.keys(), reverse=True)

        fig = pylab.figure()
        #ax = pylab.subplot(1, 1, 1)
        # Two groups of uesr accuracy:  random or prior
        # Plot the median, lower/higher quantile along different lambda values
        i = 0
        ymax = 0
        for l in legends:
            Xlabel, Y = plot_data[l]
            X = [x for x in range(len(Xlabel))]
            median = np.array([y[0] for y in Y])
            lower = np.array([y[1] for y in Y])
            higher = np.array([y[2] for y in Y])

            # plot median
            pylab.plot(X, median, color=colors[i], marker = markers[i], linestyle=linestyles[i], linewidth=2, markersize=8)
            # plot area between lower and high
            pylab.fill_between(X, lower, higher, facecolor=colors[i], alpha=0.2, hatch=hatches[i])
            
            pylab.xticks(X, Xlabel)
            i += 1
            if max(higher) > ymax:
                ymax = max(higher)
        # Legend
        pylab.ylim(pylab.ylim()[0], ymax*1.2)
        pylab.legend(legends)
        pylab.xlabel('Effort')
        pylab.ylabel(r'$\lambda$')
        #pylab.title(plot_name)
        
        # save figure
        filename = '%s/%s.png'%(outputdir, plot_name)
        fig.tight_layout()
        pylab.savefig(filename, format='png')    


if __name__ == '__main__':
    # Load data    
    # parameter specifications
    g_params = ld.load_parameter_record(g_res_param_file)
    e_params = ld.load_parameter_record(e_res_param_file)
    
    # data corresponding to each parameter setting
    g_data = ld.load_data(g_res_dir, g_params)
    e_data = ld.load_data(e_res_dir, e_params)

    # Format data for plots
    g_D = data_gain(g_data, g_params)
    e_D = data_effort(e_data, e_params)

    # Make plots
    makeplot(g_D)
    makeplot(e_D)
    pylab.show()


    
