"""
Make plots for the result of fitting logistic regression
models with the smooth data to illustrate 
the effect of interaction terms
Three types of interactions:
- q_difficulty x f_entropy
- q_difficulty x u_level
- f_entropy x u_level
"""

import pylab
from matplotlib import rc
import matplotlib
import itertools
import numpy as np
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

#fontProperties = {'size': 16, 'family':'sans-serif','sans-serif':['Helvetica']}    
rc('font', **{'size': 16})
#rc('text', usetex=True)

# Plots to make:
# data/lr_10_4factors.txt data/lr_1_qxfe.txt      data/lr_all_fexfr.txt
# data/lr_10_qxfr.txt     data/lr_1_qxu.txt       data/lr_all_qxfr.txt
configure = {
    '1': ['qxu', 'qxfe'],
    '10': ['qxfr', '4factors'],
    'all': ['qxfr', 'fexfr']
}

datafile = lambda x, y: 'data/lr_%s_%s.txt'%(x, y)
outputdir = 'plots/lr/'
outputfile = lambda x, y: '%s/task%s_%s'%(outputdir, x, y)

tasks = ['1', '10', 'all']
u_levels = [(1, 0), (2, 0.1), (3, 0.5), (4, 1)] 

lines = ['-', '--', '-.', ':']
colors = ['b', 'r', 'g', 'black']
legends = [r'level1', r'level2', r'level3', r'level4']

#
# The columns of the data are:
#"q_difficulty" "u_level" "f_entropy" "f_relevance"  "fit" "se.fit" 
#"residual.scale" "UL" "LL" "predictedProb"
#
def load_data(datafile):
    f = open(datafile)
    lines = f.readlines()
    f.close()
    header = lines[0].strip().replace('"', '').split(' ')
    data = []
    for l in lines[1:]:
        d = l.strip().replace('"', '').split(' ')
        data.append([float(dd) for dd in d[1:]])
    return data

def plot_qxfe_gradient(data, task):
    # each user level is a plot
    i = 0
    for u_level in u_levels:
        # Get data for each level
        f, ax = pylab.subplots(1, 1)
        filtered = list(itertools.ifilter(lambda x: x[1] == u_level[1], data))
        # x-axis is query difficulty
        x = [d[0] for d in filtered]
        # y-axis is facet entropy
        y = [d[2] for d in filtered]
        # contour is the probability  
        p = [d[-1] for d in filtered]

        x = np.reshape(x, (100, 100))
        y = np.reshape(y, (100, 100))    
        z = np.reshape(p, (100, 100))

        dx, dy = 0.05, 0.05

        # x and y are bounds, so z should be the value *inside* those bounds. Therefore, remove the last value from the z array.
        z = z[:-1, :-1]
        levels = MaxNLocator(nbins=20).bin_boundaries(z.min(), z.max())

        # pick the desired colormap, sensible levels, and define a normalization instance which takes data values and translates those into levels.
        cmap = pylab.get_cmap('Greys')
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

        # contours are *point* based plots, so convert our bound into point centers
        pylab.contourf(x[:-1, :-1] + dx / 2.,
             y[:-1, :-1] + dy / 2., z, levels=levels,
             cmap=cmap)

        pylab.xlabel('Query difficulty')
        pylab.ylabel('Sublists entropy')
        pylab.colorbar()

        outfile = outputfile(task, 'qdifficulty_x_fentropy')
        pylab.savefig('%s.png'%outfile)


def plot_qxu(data, task):
    # each user level is a line
    i = 0
    pylab.figure()
    for u_level in u_levels:
        # Get data for each level
        filtered = list(itertools.ifilter(lambda x: x[1] == u_level[1], data))
        q_difficulty = [d[0] for d in filtered]
        y = [d[-1] for d in filtered]
        LL = [d[-2] for d in filtered]
        UL = [d[-3] for d in filtered]
        pylab.plot(q_difficulty, y, color = colors[i], linestyle=lines[i], linewidth=2, label=legends[i])
        pylab.fill_between(q_difficulty, y, LL, UL, color = colors[i], alpha = 0.1)
        i += 1
#    pylab.legend(legends)
    pylab.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=4, mode="expand", borderaxespad=0.) 
 
    pylab.xlabel('Query difficulty')
    pylab.xlim((min(q_difficulty), max(q_difficulty)))
    pylab.ylabel('Probability that RLR helps')
    outfile = outputfile(task, 'qdifficulty_x_ulevel')
    pylab.savefig('%s.png'%(outfile))

def plot_qxfe(D, task):
    # bin the query difficulty into 3 levels
    q = [d[0] for d in D]
    p25 = np.percentile(q, 25)
    p75 = np.percentile(q, 75)
    data_low = list(itertools.ifilter(lambda x: x[0]<=p25, D))
    data_mid = list(itertools.ifilter(lambda x: x[0]>p25 and x[0]<p75, D))
    data_high = list(itertools.ifilter(lambda x: x[0]>=p75, D))

    data_q = [('qlow', data_low), 
            ('qmid', data_mid), 
            ('qhigh', data_high)]
    
    for dq in data_q:
        name, data = dq
        fig = pylab.figure()
        i = 0
        for u_level in u_levels:
            # Get data for each level
            filtered = list(itertools.ifilter(lambda x: x[1] == u_level[1], data))
            print len(filtered)
            # x is entropy
            X = [d[2] for d in filtered]
            y = [d[-1] for d in filtered]
            LL = [d[-2] for d in filtered]
            UL = [d[-3] for d in filtered]
            for f in filtered:
                print f
            pylab.plot(X, y, color = colors[i], linestyle=lines[i], linewidth=2, label=legends[i])
            pylab.fill_between(X, y, LL, UL, color = colors[i], alpha = 0.1)
            i += 1
        pylab.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               ncol=4, mode="expand", borderaxespad=0.) 
 
        pylab.xlabel('Sublist entropy')
        pylab.xlim((min(X), max(X)))
        pylab.ylabel('Probability that RLR helps')
        outfile = outputfile(task, '%s_x_fentropy'%name)
        pylab.savefig('%s.png'%(outfile))

  


def plot_fentropy_ulevel(task):
    data = load_data(datafile_fxu(task))
    # Each user level is a line
    i = 0
    pylab.figure()
    for u_level in u_levels:
        # Get data for each level
        filtered = list(itertools.ifilter(lambda x: x[2] == u_level[1], data))
        f_entropy = [d[1] for d in filtered]
        y = [d[8] for d in filtered]
        pylab.plot(f_entropy, y, color=colors[i], linestyle=lines[i], linewidth=2, label=legends[i])
        i += 1
    pylab.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=4, mode="expand", borderaxespad=0.) 
    pylab.xlabel(r'Sublists DFU')
    pylab.xlim((min(f_entropy), max(f_entropy)))
    pylab.ylabel(r'$P(\Delta_\textit{effort} > 0)$')
    pylab.savefig('%s/fxu_%s.png'%(outputdir, task))




if __name__ == '__main__':
    for task in tasks:
        data = configure[task]
        for d in data:
            fdata = datafile(task, d)
            if d == 'qxu':
                plot_qxu(load_data(fdata), task)
            elif d == 'qxfe':
                plot_qxfe(load_data(fdata), task)
    pylab.show()
