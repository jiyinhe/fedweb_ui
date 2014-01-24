"""
script to plot and analyse the results of the clickgame


"""
import numpy as np
from scipy import stats
import pylab
import sys
import itertools
import operator
import UserData

def load_baseline(t):
	return []

"""
"""
def bar_plot(left,height, width=0.8, bottom=0):
	# left:  x coord of left side of bar
	# height: y coord of top of bar
	# width: width of bar
	# bottom: y coord of bottom of bar
	pylab.figure()
	pylab.bar(left,height,width,bottom)
	pylab.savefig("plots/scatter_"+fname)

def scatter_plot(x,y,fname,markersize=20,color='b',marker='o'):
	# x,y: arrays of x and y coords to be plotted against each other
	# markersize: size of markers
	# color: e.g., 'r','g','y'...
	# marker: type, e.g., "." point, "," pixel, "o" circle, 
	#	"v" triangle_down, "^" triangle_up, "<" triangle_left, 
	#	"s" square, "p" pentagon, "*" star, "h" hexagon1, "H" hexagon2,
	#	"+" plus, "x" x, "D" diamond
	pylab.figure()
	fig = pylab.scatter(x,y,markersize,color,marker)
	fig.axes.autoscale_view(True)
	pylab.savefig("plots/scatter_"+fname)

def box_plot(x1,x2,fname):
	fig = pylab.figure()
	plt = fig.add_subplot(111)

	m1 = [np.median(x) if x.any() else 0 for x in x1]
	m2 = [np.median(x) if x.any() else 0 for x in x2]
	
	# create ordering by median effort of baseline
	order = zip(m1,range(0,50))
	order.sort()
	order = [i[1] for i in order]

	# reorder
	m1 = [m1[i] for i in order]
	m2 = [m2[i] for i in order]
	x = range(1,51)	
	# plot
	pylab.plot(x,m1,'blue')
	pylab.plot(x,m2,'red')

	# reorder
	x1 = [x1[i] for i in order]
	# plot
	bp = pylab.boxplot(x1)
	pylab.setp(bp['medians'], color='blue')

	# reorder
	x2 = [x2[i] for i in order]
	# plot
	bp = pylab.boxplot(x2)
	pylab.setp(bp['boxes'], color='red')
	pylab.setp(bp['whiskers'], color='red')
	pylab.setp(bp['medians'], color='red')

	pylab.xticks(range(len(order)), order, size='small')

	pylab.setp(plt.get_xticklabels(),rotation='vertical', fontsize=10)

	# show/save
#	pylab.show()
	pylab.savefig("plots/box_"+fname+".pdf")

if __name__ == '__main__':
	us = UserData.UserData()	
	# number of success
	q1 = ("basic","select task_id, clickcount from fedtask_userscore\
 where numrel = 10 and task_id < 51;")
	# number of fail
	q2 = ("facet", "select task_id, clickcount from fedtask_userscore\
  where numrel = 10 and task_id > 50;")

#	for q in [("basic.pdf",q1),("facet.pdf",q2)]:
#		us.load_data(q[1])
#		x = us.get_matrix_data()
#		box_plot(x,q[0])

	d={}
	for i in range(0,50):
		d[i] = [[],[]]
	index = 0
	for q in [q1,q2]:			
		us.load_data(q[1])
		[x,y] = us.get_x_y_data()
		for i in range(0,len(x)):
			k = x[i]%50
			v = int(y[i])
			d[k][index].append(v)
		index+=1
	acc1 = []
	acc2 = []
	for [v1,v2] in d.values():
		acc1.append(np.array(v1))
		acc2.append(np.array(v2))
	box_plot(np.array(acc1),np.array(acc2),"combined")
		

