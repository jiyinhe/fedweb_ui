"""
script to tabulate and analyse the results of the clickgame


"""
import sys,os
sys.path.append(os.path.abspath('../../fw_userstudy/scripts/log_utils/'))

import numpy as np
from scipy import stats
import pylab
import itertools
import operator
import UserData,LogData
import dateutil
import datetime

def load_baseline(t):
	return []

"""
"""

def table_row(row):
	row = [str(i) for i in row]
	return " & ".join(row) + "\\\\"

# create a header row, use multicolumn when width is bigger than
# provided header
def table_header_row(header,width=[]):
	if width:
		i = 0
		row = []
		for (w,f) in width:
			row.append("\multicolumn{%d}{%s}{%s}"%(w,f,header[i]))
			i+=1
		return table_row(row)
		
	else:
		return table_row(header)
	
def gen_task_effort_table():
	us = UserData.UserData()	

	# number of success with basic 
	q1=("success basic"," and numrel = 10 and task_id < 51")
	# number of success with facet
	q2=("success facet"," and numrel = 10 and task_id > 50")
	# number of fail with basic
	q3=("fail basic"," and numrel < 10 and clickcount = 50 and task_id < 51")
	# number of fail with facet
	q4=("fail facet"," and numrel < 10 and clickcount = 50 and task_id > 50")
	# number of give up with basic
	q5=("giveup basic"," and giveup=1 and task_id < 51")
	# number of give up with facet
	q6=("giveup facet"," and giveup=1 and task_id > 50")
	qrs=[("success",(q1,q2)),("fail",(q3,q4)),("giveup",(q5,q6))]

	# a list of (task,user) tuples indicating the tasks completed by a
	# particular user
	task_userqry = """select task_id,count(*)
			from 	fedtask_userscore as us,
					auth_user as au 
			where us.user_id=au.id %s group by task_id;"""
	# a list of task_id, clickcount tuples indicating the effort to
	# complete a particular task
	task_clickcountqry = """select task_id, clickcount
			from 	fedtask_userscore as us,
					auth_user as au 
			where us.user_id=au.id %s;"""
	taskqrs=[task_userqry,task_clickcountqry]
	
	# loop over queries and create table rows
	# this is a bit complicated, becuase of the wanted table structure
	# 		tasks completed				effort spend
	#	basic			facet		basic			facet
	# tot, md, IQR  tot, md, IQR  tot, md, IQR  tot, md, IQR
	print table_header_row(["","tasks completed","effort spent"],
							[(1,'c'),(6,'c'),(6,'c')])
	print "\hline"
	print table_header_row(["","basic","facet","basic","facet"],
							[(1,'c'),(3,'c'),(3,'c'),(3,'c'),(3,'c')])
	print "\hline"
	print table_header_row(["","total","median","IQR","total","median","IQR","total","median","IQR","total","median","IQR"])
	print "\hline"
							
	for (type,b_f_pair) in qrs: # get a basic, facet query
		row = [type]
		for tqry in taskqrs: # for both tasks	
			for q in b_f_pair: # get stats for each
				us.load_data(tqry%q[1])
				(x,y) = us.get_x_y_data()
				row.extend([int(sum(y)), np.median(y), 
					"(%.1f-%.1f)"%(np.percentile(y,25),np.percentile(y,75))])
		print table_row(row)

# summarize a list of log events in a single data object
# each data object represents a user on a single task
def summarize_events(events):
	data = {'posbookmark':0,
			'negbookmark':0,
			'category':{},
			'paginate':0,
			'hovers':0,
			'search_depth':[],
			'last_click':[],
			'time_spent':[],
			'done': False}

	for e in events:
		time = e[0]
		data['time_spent'].append(time)	
		
		e_type = e[2]
		if e_type == 'bookmark':
			feedback = int(e[4][2]) 
			done = e[4][3]
			data['done']=done
			if done: # we store the last list user was working in
				data['search_depth'].append(e[3])
			if feedback == 1:
				data['posbookmark']+=1
			else:
				data['negbookmark']+=1
		elif e_type == 'category_filter':
			cat = e[4] 
			if cat in data['category']:
				data['category'][cat]+=1
			else:
				data['category'][cat]=1
			data['search_depth'].append(e[3])
		elif e_type == 'paginate':
			data['paginate']+=1
			data['search_depth'].append(e[3])
		elif e_type == 'mouse_movements':
			data['hovers']+=e[4]
		elif e_type == 'mouse_click':
			data['last_click'].extend(e[4])
		else:	
			pass
	return data

# descriptive statistics data: for completed tasks
# 				 		per user,					 per query
#				basic			facet			basic			facet
#			tot md IQR		tot md IQR		tot md IQR		tot md IQR
# bookmark
# category
# paginate
# search depth 
# time spent
# nr of hovers
def log_summary_table(td):
	posbookmark = []
	negbookmark = []
	category = []
	paginate = []
	search_depth = []
	hovers = []
	time_spent = []

	for (k,lst) in td.items():
		for d in lst:
			if not d['done']: continue
			posbookmark.append(d['posbookmark'])
			negbookmark.append(d['negbookmark'])
			paginate.append(d['paginate'])
			hovers.append(d['hovers'])
			# time spent
			diff = 0
			if len(d['time_spent']) > 0:
				first = dateutil.parser.parse(d['time_spent'][0])
				last =	dateutil.parser.parse(d['time_spent'][-1])
				diff = last - first
				diff = diff.total_seconds()
			time_spent.append(diff)
			category.append(sum(d['category'].values()))
			#print d['category']
			# determine last clicked document
			last_click = find_last_click_depth(d['search_depth'],d['last_click'])
			if last_click < 10:
				print d['search_depth']
				print d['last_click']
			search_depth.append(last_click)
	if not td: sys.exit()
	print "posbookmark"
	print sum(posbookmark),np.median(posbookmark),np.percentile(posbookmark,25),np.percentile(posbookmark,75)
	print "negbookmark"
	print sum(negbookmark),np.median(negbookmark),np.percentile(negbookmark,25),np.percentile(negbookmark,75)
	print "category"
	print sum(category),np.median(category),np.percentile(category,25),np.percentile(category,75)
	print "paginate"
	print sum(paginate),np.median(paginate),np.percentile(paginate,25),np.percentile(paginate,75)
	print "hovers"
	print sum(hovers),np.median(hovers),np.percentile(hovers,25),np.percentile(hovers,75)
	print "search depth"
	print sum(search_depth),np.median(search_depth),np.percentile(search_depth,25),np.percentile(search_depth,75)
	print "time spent"
	print sum(time_spent),np.median(time_spent),np.percentile(time_spent,25),np.percentile(time_spent,75)


def find_last_click_depth(data,last_click_list):
			search_path = []
			# first find all the lists a user went through except for
			# the last
			for l in data[:-1]:
				search_path.extend(l)
			# for the last list we need to find the highest ranked
			# document clicked.
			indices = []
			lastlist = data[-1]
			# for each click in last_click list
			for click in last_click_list:
				if type(click) == int: continue
				if not click.startswith("rank_"): continue
				i = int(click.replace("rank_",""))
				if i in lastlist:
					indices.append(lastlist.index(i))
			# depth of the searchpath is the sum of the lists visited
			# + the rank of the lowest ranked document in the last
			# list
			search_depth = len(search_path) + max(indices)
			return search_depth


def group_by_topic(data,condition):
	"""
	(u'dodijk', 7115)
	[[u'2014-01-23T16:29:15.594+01:00',
	u'http://zookst9.science.uva.nl:8002/study/task/', u'bookmark_try',
	[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]], [u'2014-01-23T16:29:15.622+01:00',
	u'http://zookst9.science.uva.nl:8002/study/task/', u'bookmark', [0, 1,
	2, 3, 4, 5, 6, 7, 8, 9], (1, 1, 1, 1)],
	"""
	# per query (topic_id)
	td = {}
	for ((username,topic_id),events) in data.items():
		# ignore the following users:
		# username < 27, 37 45
		if username < 27 or username == 37 or username == 45:
			continue
		# skip non existing username ('')
		if not username: continue
		# skip users not matching the condition
		if int(username)%2 != condition: continue

		data = summarize_events(events)
		if topic_id in td:
			td[topic_id].append(data)
		else:
			td[topic_id] = [data]

	return td

# print for each topic the distribution of category clicks as a
# dictionary
def category_distribution(td):
	topcatd = {}
	for (t_id,lst) in td.items():
		catd = {}
		for d in lst:
			if not d['done']: continue
			for (cat,v) in d['category'].items():
				if cat in catd:
					catd[cat]+=v
				else:
					catd[cat]=v
		topcatd[t_id]=catd
	topcatdist = topcatd.items()
	topcatdist.sort()
	return topcatdist

def search_depth_distribution(td):
	searchd = {}
	for (t_id,lst) in td.items():
		for d in lst:
			if not d['done']: continue
			last_click = find_last_click_depth(d['search_depth'],d['last_click'])
			if last_click in searchd:
				searchd[last_click]+=1
			else:
				searchd[last_click]=1
	searchddist = searchd.items()
	searchddist.sort()
	return searchddist
	

def gen_logdata_table():
	# first get the data
	if 0:
		inputfile = "../../fw_userstudy/scripts/log_utils/alldata_24-01-2014_13:13.log"
		#inputfile = "clicks_24-01-2014_13:00.log"
		ld = LogData.LogData()
		ld.load_data(inputfile)
		data = ld.group_logevents_by_user_and_query()

		# filter the data
		# remove events (hovers) on non-task pages
		page = 'http://zookst9.science.uva.nl:8002/study/task/'
		data = ld.filter(data, {'location':page,
								'order':0})# order on date
		ld.cache2file("table.tmp",data)
	else:
		fh = open('table.tmp')
		data = eval(fh.read())
		fh.close()
	
	print 'basic'
	td = group_by_topic(data,0)
	log_summary_table(td)
	sddist = search_depth_distribution(td)
	write_data('basic_searchdepth.data',sddist)
	print 'facet'
	td = group_by_topic(data,1)
	log_summary_table(td)
	catdist = category_distribution(td)
	write_data('facet_catdist.data',catdist)
	sddist = search_depth_distribution(td)
	write_data('facet_searchdepth.data',sddist)

def write_data(fname, data):
	fh = open('data/'+fname,'w')
	for (k,v) in data:
		fh.write("%s	%s\n"%(k,v))
	fh.close()


if __name__ == '__main__':
	#gen_task_effort_table()
	gen_logdata_table()
