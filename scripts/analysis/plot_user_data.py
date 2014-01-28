"""
script to plot and analyse the results of the clickgame


"""
import numpy as np
from scipy import stats
import pylab
import matplotlib.pyplot as plt
import sys
import itertools
import operator
import UserData
from table_user_data import output_searchdepth, output_searchdepth_matrix

def load_baseline(t):
	return []

"""
"""

def plot_hovers():
	basic_hovers = sorted([(9, 6789), (5, 7042), (6, 7105), (8, 7320), (4, 7324), (3, 7327), (7,
		7393), (2, 7558), (1, 8369), (0, 9535)])
	facet_hovers = sorted([(9, 8584), (8, 8589), (7, 9269), (6, 9338), (5, 10007), (4, 10681),
		(3, 10980), (2, 12739), (1, 15587), (0, 16111)])

	basic = [x[1] for x in sorted(basic_hovers,key=lambda x:x[0])]
	mx = sum(basic)
	basic = np.array(basic)/float(mx)

	facet = [x[1] for x in sorted(facet_hovers,key=lambda x:x[0])]
	mx = sum(facet)
	facet = np.array(facet)/float(mx)

	positions = np.array(range(1,11))
	basic_pos = positions-0.3
	facet_pos = positions

	fig = pylab.figure()
	pylab.bar(basic_pos,basic, width=0.2, color='k')
	pylab.bar(facet_pos,facet, width=0.2, color='w',hatch='/')
	pylab.xticks(range(1,11), range(1,11), size='x-large')
	pylab.yticks(pylab.yticks()[0], pylab.yticks()[0]*100, size='x-large')
	pylab.xlabel('rank',size='x-large')
	pylab.ylabel('% of total hovers',size='x-large')
	subp = fig.add_subplot(111)
	subp.axes.autoscale_view(True)
	pylab.savefig('plots/hoverdistribution.pdf')


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
	fig = pylab.figure()
	x,y = get_cumulative_data(data1)
	bufy= [y[0]]*9
	bufx= range(9)
	pylab.plot(np.hstack((bufx,x)),np.hstack((bufy,y)),'k')
	write_data('data/basic_searchdepth_prob.data',[x,y])

	x,y = get_cumulative_data(data2)
	bufy= [y[0]]*9
	pylab.plot(np.hstack((bufx,x)),np.hstack((bufy,y)),'r',marker='+')
	write_data('data/facet_searchdepth_prob.data',[x,y])
	pylab.xlabel('rank',size='x-large')
	pylab.ylabel('probability to visit rank',size='x-large')
	pylab.xticks(size='x-large')
	pylab.yticks(size='x-large')
	sp = fig.add_subplot(111)
	sp.axes.autoscale_view(True)

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
	BNDCG1_medians = np.array([np.array(l.split()[1]).astype(np.float) for l in data])
	BNDCG10_medians = np.array([np.array(l.split()[2]).astype(np.float) for l in data])
	BNDCG20_medians = np.array([np.array(l.split()[3]).astype(np.float) for l in data])
	BNDCGall_medians = np.array([np.array(l.split()[4]).astype(np.float) for l in data])
	NDCG1_medians = np.array([np.array(l.split()[5]).astype(np.float) for l in data])
	NDCG10_medians = np.array([np.array(l.split()[6]).astype(np.float) for l in data])
	NDCG20_medians = np.array([np.array(l.split()[7]).astype(np.float) for l in data])
	NDCGall_medians = np.array([np.array(l.split()[8]).astype(np.float) for l in data])
	#facet_medians = output_searchdepth(1)
	#basic_medians = output_searchdepth(0)
	basic_medians = [np.median(f) for f in
np.array(open_searchdepth_matrix("basic_searchdepth_matrix.data"))]
	facet_medians = [np.median(f) for f in
np.array(open_searchdepth_matrix("facet_searchdepth_matrix.data"))]

	# load simulated data
	fh = open('data/simulate_user.txt','r')
	text = fh.read()
	fh.close()
	lines = text.split("\n")
	header = lines[0]
	data = lines[1:-1]
	facet_simdata_medians = np.median(np.array([
		np.array(l.split()).astype(np.int) for l in data]),axis =0)

	print "BNDCG1 vs user facet", "%.2f & %.4f"%stats.pearsonr(BNDCG1_medians,facet_medians)
	print "BNDCG10 vs user facet", "%.2f & %.4f"%stats.pearsonr(BNDCG10_medians,facet_medians)
	print "BNDCG20 vs user facet", "%.2f & %.4f"%stats.pearsonr(BNDCG20_medians,facet_medians)
	print "BNDCGall vs user facet", "%.2f & %.4f"%stats.pearsonr(BNDCGall_medians,facet_medians)
	print "NDCG1 vs user facet", "%.2f & %.4f"%stats.pearsonr(NDCG1_medians,facet_medians)
	print "NDCG10 vs user facet", "%.2f & %.4f"%stats.pearsonr(NDCG10_medians,facet_medians)
	print "NDCG20 vs user facet", "%.2f & %.4f"%stats.pearsonr(NDCG20_medians,facet_medians)
	print "NDCGall vs user facet", "%.2f & %.4f"%stats.pearsonr(NDCGall_medians,facet_medians)

	print "BNDCG1 vs user basic", "%.2f & %.4f"%stats.pearsonr(BNDCG1_medians,basic_medians)
	print "BNDCG10 vs user basic", "%.2f & %.4f"%stats.pearsonr(BNDCG10_medians,basic_medians)
	print "BNDCG20 vs user basic", "%.2f & %.4f"%stats.pearsonr(BNDCG20_medians,basic_medians)
	print "BNDCGall vs user basic", "%.2f & %.4f"%stats.pearsonr(BNDCGall_medians,basic_medians)
	print "NDCG1 vs user basic", "%.2f & %.4f"%stats.pearsonr(NDCG1_medians,basic_medians)
	print "NDCG10 vs user basic", "%.2f & %.4f"%stats.pearsonr(NDCG10_medians,basic_medians)
	print "NDCG20 vs user basic", "%.2f & %.4f"%stats.pearsonr(NDCG20_medians,basic_medians)
	print "NDCGall vs user basic", "%.2f & %.4f"%stats.pearsonr(NDCGall_medians,basic_medians)

	print "BNDCG1 vs sim facet", "%.2f & %.4f"%stats.pearsonr(BNDCG1_medians,facet_simdata_medians)
	print "BNDCG10 vs sim facet", "%.2f & %.4f"%stats.pearsonr(BNDCG10_medians,facet_simdata_medians)
	print "BNDCG20 vs sim facet", "%.2f & %.4f"%stats.pearsonr(BNDCG20_medians,facet_simdata_medians)
	print "BNDCGall vs sim facet", "%.2f & %.4f"%stats.pearsonr(BNDCGall_medians,facet_simdata_medians)
	print "NDCG1 vs sim facet", "%.2f & %.4f"%stats.pearsonr(NDCG1_medians,facet_simdata_medians)
	print "NDCG10 vs sim facet", "%.2f & %.4f"%stats.pearsonr(NDCG10_medians,facet_simdata_medians)
	print "NDCG20 vs sim facet", "%.2f & %.4f"%stats.pearsonr(NDCG20_medians,facet_simdata_medians)
	print "NDCGall vs sim facet", "%.2f & %.4f"%stats.pearsonr(NDCGall_medians,facet_simdata_medians)

	print "BnDCG@all vs sim facet", stats.pearsonr(BNDCGall_medians,facet_simdata_medians)
	print "user basic vs user facet", stats.pearsonr(basic_medians,facet_medians)
	print "user basic vs sim facet", stats.pearsonr(basic_medians,facet_simdata_medians)

	BNDCGall_ranking = [x[0] for x in sorted(zip(range(1,51),BNDCGall_medians),key=lambda x:x[1]) ]
	facet_ranking = [x[0] for x in sorted(zip(range(1,51),facet_medians),key=lambda x:x[1]) ]
	facet_simdata_ranking = [x[0] for x in sorted(zip(range(1,51),facet_simdata_medians),key=lambda x:x[1]) ]

	diff_ranking = [x[0] for x in
sorted(zip(range(1,51),np.subtract(np.array(facet_medians),
np.array( basic_medians))),key=lambda x:x[1])] 
	basic_ranking = [x[0] for x in sorted(zip(range(1,51),
basic_medians),key=lambda x:x[1]) ]

	fh = open('data/facet_catdist.data','r')
	text = fh.read()
	fh.close()
	lines = text.split("\n")
	catuse = []
	for l in lines:
		if not l: continue
		t,d = l.split("\t",1)
		d = eval(d)
		if d.values():
			catuse.append(sum(d.values()))
		else:
			catuse.append(0)
	catuse = np.array(catuse)/float(max(catuse))
	sel_medians = []
	for i in range(50):
		c = catuse[i]
		if c > .29:
			v = facet_simdata_medians[i]
		else:
			v = basic_medians[i]
		sel_medians.append(v)

	sel_ranking = [x[0] for x in sorted(zip(range(1,51),sel_medians),key=lambda x:x[1]) ]
	
		
	diff = np.subtract(np.array(basic_medians), np.array(facet_medians) )
	print stats.pearsonr(BNDCGall_medians,diff)
	print stats.pearsonr(facet_simdata_medians,diff)
	print "NDCG f",stats.kendalltau(BNDCGall_ranking,facet_ranking)
	print "sim f",stats.kendalltau(facet_simdata_ranking,facet_ranking)
	print "sel f",stats.kendalltau(sel_ranking,facet_ranking)
	print "NDCG b",stats.kendalltau(BNDCGall_ranking,basic_ranking)
	print "sim b",stats.kendalltau(facet_simdata_ranking,basic_ranking)

# NDCG vs facet users
#	pylab.figure()
#	fig = pylab.scatter(NDCG_medians,facet_medians,color='b')
#	fig.axes.autoscale_view(True)
#	print stats.pearsonr(NDCG_medians,facet_medians)
	#pylab.show()

# NDCG vs basic users
#	pylab.figure()
#	fig = pylab.scatter(NDCG_medians,basic_medians,color='b')
#	fig.axes.autoscale_view(True)
#	print stats.pearsonr(NDCG_medians,basic_medians)
	#pylab.show()

# facet users vs basic users
#	pylab.figure()
#	fig = pylab.scatter(facet_medians,basic_medians,color='b')
#	fig.axes.autoscale_view(True)
#	print stats.pearsonr(facet_medians,basic_medians)
	#pylab.show()

	#simdata_medians = [x if x < 51 else 50 for x in simdata_medians]
	
# facet sim vs facet users
	pylab.figure()
	fig = pylab.scatter(facet_simdata_medians,facet_medians,color='b')
	fig.axes.autoscale_view(True)
	print stats.pearsonr(facet_simdata_medians,facet_medians)
	print stats.spearmanr(facet_simdata_medians,facet_medians)
	pylab.xlabel('simulated effort',size='x-large')
	pylab.ylabel('user effort',size='x-large')
	pylab.xticks(size='x-large')
	pylab.yticks(size='x-large')
	pylab.savefig('plots/facet_simdata_medians-facet_medians.pdf')

# NDCG vs facet sim
#	pylab.figure()
#	fig = pylab.scatter(NDCG_medians,facet_simdata_medians,color='b')
#	fig.axes.autoscale_view(True)
#	print stats.pearsonr(NDCG_medians,facet_simdata_medians)
#	pylab.show()

def save_searchdepth_matrix():
	fname = "basic_searchdepth_matrix.data"
	fh = open(fname,'w')
	data =output_searchdepth_matrix(0)
	fh.write(str(data))
	fh.close()

	fname = "facet_searchdepth_matrix.data"
	fh = open(fname,'w')
	data =output_searchdepth_matrix(1)
	fh.write(str(data))
	fh.close()

def open_searchdepth_matrix(fname):
	fh = open(fname,'r')
	lst = eval(fh.read())
	fh.close()
	acc = []
	for l in lst:
		acc.append(np.array(l))
	return acc

def line_plots():
	#box_plot(BNDCGall_medians,facet_simdata_medians,"ndcg_simdata.pdf")
	
	fig, ax1 = pylab.subplots()
	indices = range(50)
	t = range(1,51)
	s1 = [np.median(f) for f in facet]
	order = [x[0] for x in sorted(zip(indices,s1),key=lambda k:k[1])]
	s1 = sorted(s1)

	ax1.plot(t, s1, 'b-')
	ax1.set_xlabel('topic')
#	# Make the y-axis label and tick labels match the line color.
	ax1.set_ylabel('facet  simulated effort', color='b')
#	for tl in ax1.get_yticklabels():
#		tl.set_color('b')


	ax2 = ax1.twinx()
	s2 = facet_simdata_medians
	s2 =  [np.median(f) for f in basic]
#	s2 = 1 - BNDCGall_medians
	s2 = [s2[i] for i in order]
	ax2.plot(t, s2, 'r-')
#	ax2.set_ylabel('BNDCGall', color='r')
##	for tl in ax2.get_yticklabels():
##		tl.set_color('r')

	pylab.savefig('facet_user_vs_basic_user.pdf')
	#pylab.savefig('facet_user_vs_basic_user.pdf')
	#pylab.savefig('facet_sim_vs_facet_user.pdf')
	#pylab.savefig('BNDCGall_vs_facet_user.pdf')
	#pylab.savefig('BNDCGall_vs_basic_user.pdf')


def select_neg(lst):
	return [e for e in lst if e < 0]

def select_neg_eq(lst):
	return [e for e in lst if e <= 0]

def select_pos(lst):
	return [e for e in lst if e > 0]

def agree(l1,l2):
	return len(set(l1).intersection(set(l2)))
		
def get_neg_eq_indices(lst):
	indices = []
	i = 0
	for e in lst:
		if e < 0:
			indices.append(i)
		i+=1
	return indices

def get_pos_indices(lst):
	indices = []
	i = 0
	for e in lst:
		if e > 0:
			indices.append(i)
		i+=1
	return indices


if __name__ == '__main__':
	#gen_effort_per_topic_box_plots()
	#plot_search_depth()	
	plot_correlation()
	plot_hovers()
	#save_searchdepth_matrix()
	basic = np.array(open_searchdepth_matrix("basic_searchdepth_matrix.data"))
	facet = np.array(open_searchdepth_matrix("facet_searchdepth_matrix.data"))

	box_plot(basic,facet, "searchdepth.pdf")
	basic_medians = [np.median(b) for b in basic]
	facet_medians = [np.median(b) for b in facet]

	fh = open('data/simulate_user.txt','r')
	text = fh.read()
	fh.close()
	lines = text.split("\n")
	header = lines[0]
	data = lines[1:-1]
	facet_simdata_medians = np.median(np.array([np.array(l.split()).astype(np.int) for l in data]),axis=0)
	

	fh = open('NDCG_originlist.txt','r')
	text = fh.read()
	fh.close()
	lines = text.split("\n")
	header = lines[0]
	data = lines[1:-1]
	data.sort()
	BNDCGall_medians = np.array([np.array(l.split()[4]).astype(np.float) for l in 
data])

	fh = open('data/facet_catdist.data','r')
	text = fh.read()
	fh.close()
	lines = text.split("\n")
	catuse = []
	for l in lines:
		if not l: continue
		t,d = l.split("\t",1)
		d = eval(d)
		#catuse.append(sum(d.values())/float(len(d)))
	#plot_correlation()
		
	pylab.figure()
	# real users
	diff = np.subtract(basic_medians,facet_medians)
	diff = [100 if e > 100 else e for e in diff]
	diff = [-100 if e < -100 else e for e in diff]
	neg=select_neg_eq(diff)
	pos =select_pos(diff)
	print "neg", len(neg), "pos", len(pos)

	# simulated
	diff2 = np.subtract(basic_medians,facet_simdata_medians)
	diff2 = [100 if e > 100 else e for e in diff2]
	diff2 = [-100 if e < -100 else e for e in diff2]

	print "predicted"
	neg2=select_neg_eq(diff2)
	pos2 =select_pos(diff2)
	print "neg", len(neg2), "pos", len(pos2)

	agree_neg= agree(get_neg_eq_indices(diff),get_neg_eq_indices(diff2))
	agree_pos= agree(get_pos_indices(diff),get_pos_indices(diff2))
	agree_all= [1 for (e1,e2) in zip(diff,diff2) if e1*e2 > 0 ]
	print "agree_neg", agree_neg, "agree_pos", agree_pos, "agree_all", len(agree_all)


	order = [x[0] for x in sorted(zip(range(50),diff),key=lambda x:
x[1])]

	positions = np.array(range(1,51))
	user_pos= positions - 0.4
	fig = pylab.figure()
	pylab.bar(user_pos,sorted(diff),width=0.3,color='k')
	pylab.bar(positions,[diff2[i] for i in
order],width=0.4,color='w',hatch='/')
	pylab.plot([BNDCGall_medians[i] for i in order])
	subp = fig.add_subplot(111)
	subp.axes.autoscale_view(True)
	pylab.xlabel('topic',size='x-large')
	pylab.ylabel('effort difference',size='x-large')
	#ax2 = subp.twinx()
	#pylab.plot([BNDCGall_medians[i] for i in order])
	pylab.xticks(size='x-large')
	pylab.yticks(size='x-large')
	pylab.savefig("basic_facet_diff.pdf")
#	pylab.show()

