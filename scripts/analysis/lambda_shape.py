"""
Plot the probability that a depth is reached in a list for a given lambda
"""

import pylab
import numpy as np

steps = np.array(range(200))
styles = ['-b', '.-r', '--g', 'x-m']
legends = ['$\lambda=1$', '$\lambda=0.1$', '$\lambda=0.01$', '$\lambda=0.001$']

X = steps+1
pylab.figure()

i = 0
for l in [1, 0.1, 0.01, 0.001]:
	p_continue = np.exp(-X*l)
	s = 1
	p_reach = [s]
	for x in p_continue[1:]:
		s = s*x
		p_reach.append(x)
	pylab.plot(X, p_reach, styles[i], linewidth=2.) 
	i += 1

pylab.legend(legends, bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0.)
pylab.xlabel('Rank')
pylab.ylabel('Probability of reaching rank $r$')
 
pylab.rc('text', fontsize=18)
pylab.show()


