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
from table_user_data import output_searchdepth

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
	pylab.savefig("plots/bar_"+fname)

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

	pylab.xticks(range(1,len(order)+1), order, size='small')

	pylab.setp(plt.get_xticklabels(),rotation='vertical', fontsize=10)

	# show/save
#	pylab.show()
	pylab.savefig("plots/box_"+fname+".pdf")

def gen_effort_per_topic_box_plots():
	us = UserData.UserData()	
	# number of success
	q1 = ("basic","select task_id, clickcount, giveup from fedtask_userscore\
 where (numrel = 10 || clickcount = 50 || giveup = 1)  and\
 task_id < 51 and user_id >26 and user_id != 37 and user_id != 45\
 order by task_id;")
	# number of fail
	q2 = ("facet", "select task_id, clickcount, giveup from fedtask_userscore\
  where (numrel = 10 || clickcount = 50 || giveup = 1) and\
 task_id > 50 and user_id >26 and user_id != 37 and user_id != 45\
 order by task_id;")

#	for q in [("basic.pdf",q1),("facet.pdf",q2)]:
#		us.load_data(q[1])
#		x = us.get_matrix_data()
#		box_plot(x,q[0])

	d={}
	for i in range(0,50):
		d[i] = [[],[]]
	index = 0
	for q in [q1,q2]:			
		data = us.load_data(q[1])
		x = [e[0] for e in data]
		# set giveup to 50 
		y = [e[1] if e[2] == 0 else 50 for e in data]
#		[x,y] = us.get_x_y_data()
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

def load_data(fname):
	fh = open(fname)
	text = fh.read()
	fh.close()
	lines = text.split("\n")
	data = []
	for line in lines:
		if line:
			row = [] 
			for e in line.split():
				row.append(int(e))
			data.append(row)
	return np.array(data)

def get_cumulative_data(data):
	# number of people that have seen a snippet at a certain rank is
	# the sum of all people that saw that rank and furter, so reverse
	# the data:
	rev_data = data[::-1]
	rev_cumdata = np.cumsum(rev_data[:,1])
	# now reverse the cumulative data and x axis back
	cumdata = rev_cumdata[::-1]
	# normalize cumdata to probability
	totcumdata = float(max(cumdata))
	print sum(cumdata/totcumdata)
	return data[:,0],cumdata/totcumdata

def write_data(fname,data):
	[x,y] = data
	fh = open(fname,'w')
	for i in range(len(x)):
		fh.write("%d	%f\n"%(x[i],y[i]))
	fh.close()

def plot_search_depth():
	data1 = load_data('data/basic_searchdepth.data')
	data2 = load_data('data/facet_searchdepth.data')

	x,y = get_cumulative_data(data1)
	pylab.plot(x,y,'b')
	write_data('data/basic_searchdepth_prob.data',[x,y])

	x,y = get_cumulative_data(data2)
	pylab.plot(x,y,'r')
	write_data('data/facet_searchdepth_prob.data',[x,y])

	pylab.savefig('plots/searchdepth.pdf')

def plot_correlation():
#	us = UserData.UserData()	
#	q = ("facet", "select task_id, clickcount, giveup from fedtask_userscore\
#  where (numrel = 10 || clickcount = 50 || giveup = 1) and\
# task_id > 50 and user_id >26 and user_id != 37 and user_id != 45\
# order by task_id;")
#
##	for q in [("basic.pdf",q1),("facet.pdf",q2)]:
##		us.load_data(q[1])
##		x = us.get_matrix_data()
##		box_plot(x,q[0])
#
#	# initialize the dict so we have empty lists for tasks that have
#	# not been done
#	d={}
#	for i in range(50):
#		d[i]=[]
#
#	data = us.load_data(q[1])
#	# get the task_ids
#	x = [e[0] for e in data]
#	# get the clickcounts and if user has given up, set clickcount to 50 
#	y = [e[1] if e[2] == 0 else 50 for e in data]
#	# load data, we have a long list with zero, 1, or  possibly multiple
#	# clickcounts for each task, so we aggregate them here
#	for i in range(len(x)):
#		k = x[i]%50
#		v = int(y[i])
#		d[k].append(v)
#
#	acc = []
#	pairs = d.items()
#	# sort on task_id, so lowest task_id is first
#	pairs.sort()
#	# create arrays from each list
#	for (k,v) in pairs: 
#		acc.append(np.array(v))
#	acc = np.array(acc)
#	medians = [np.median(x) if x.any() else 0 for x in acc]

	# load NDCG data
	fh = open('NDCG_originlist.txt','r')
	text = fh.read()
	fh.close()
	lines = text.split("\n")
	header = lines[0]
	data = lines[1:-1]
	data.sort()
	NDCG_medians = np.array([np.array(l.split()[-1]).astype(np.float) for l in data])
	facet_medians = output_searchdepth(1)
	basic_medians = output_searchdepth(0)

	pylab.figure()
	fig = pylab.scatter(NDCG_medians,facet_medians,color='b')
	fig.axes.autoscale_view(True)
	print stats.pearsonr(NDCG_medians,facet_medians)
	#pylab.show()

	pylab.figure()
	fig = pylab.scatter(NDCG_medians,basic_medians,color='b')
	fig.axes.autoscale_view(True)
	print stats.pearsonr(NDCG_medians,basic_medians)
	#pylab.show()

	pylab.figure()
	fig = pylab.scatter(facet_medians,basic_medians,color='b')
	fig.axes.autoscale_view(True)
	print stats.pearsonr(facet_medians,basic_medians)
	#pylab.show()

	# load simulated data
	fh = open('data/simulate_user.txt','r')
	text = fh.read()
	fh.close()
	lines = text.split("\n")
	header = lines[0]
	data = lines[1:-1]
	facet_simdata_medians = np.median(np.array([np.array(l.split()).astype(np.int) for l in
data]),axis =0)
	#simdata_medians = [x if x < 51 else 50 for x in simdata_medians]
	
	pylab.figure()
	fig = pylab.scatter(facet_simdata_medians,facet_medians,color='b')
	fig.axes.autoscale_view(True)
	print stats.pearsonr(facet_simdata_medians,facet_medians)
	pylab.xlabel('simulated effort')
	pylab.ylabel('user effort')
	pylab.savefig('plots/facet_simdata_medians-facet_medians.pdf')

	pylab.figure()
	fig = pylab.scatter(NDCG_medians,facet_simdata_medians,color='b')
	fig.axes.autoscale_view(True)
	print stats.pearsonr(NDCG_medians,facet_simdata_medians)
	pylab.show()


if __name__ == '__main__':
	#gen_effort_per_topic_box_plots()
	plot_search_depth()	
	plot_correlation()
		

