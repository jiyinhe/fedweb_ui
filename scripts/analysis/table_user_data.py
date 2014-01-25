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
		print username
		# skip non existing username ('')
		if not username: continue
		# skip users not matching the condition
		if int(username)%2 != condition: continue
		data = {'posbookmark':0,
				'negbookmark':0,
				'category':0,
				'paginate':0,
				'hovers':0,
				'search_depth':[0,1,2,3,4,5,6,7,8,9],
				'last_click':[],
				'time_spent':[]}
		td[topic_id]=data
		for e in events:
			time = e[0]
			td[topic_id]['time_spent'].append(time)	
			
			e_type = e[2]
			if e_type == 'bookmark':
				feedback = e[4] 
				if feedback == 1:
					td[topic_id]['posbookmark']+=1
				else:
					td[topic_id]['negbookmark']+=1
			elif e_type == 'category':
				td[topic_id]['category']+=1
			elif e_type == 'paginate':
				td[topic_id]['paginate']+=1
			elif e_type == 'mouse_movements':
				td[topic_id]['hovers']+=e[4]
			elif e_type == 'mouse_click':
				td[topic_id]['last_click'].extend(e[4])
			else:	
				pass
	# descriptive statistics data: for all tasks
	# 				 		per user,					 per query
	#				basic			facet			basic			facet
	#			tot md IQR		tot md IQR		tot md IQR		tot md IQR
	# bookmark
	# category
	# paginate
	# search depth 
	# time spent
	# nr of hovers
	
	posbookmark = []
	negbookmark = []
	category = []
	paginate = []
	search_depth = []
	hovers = []
	time_spent = []

	for (k,d) in td.items():
		print k,d
		posbookmark.append(d['posbookmark'])
		negbookmark.append(d['negbookmark'])
		category.append(d['category'])
		paginate.append(d['paginate'])
		hovers.append(d['hovers'])
		# time spent
		first = dateutil.parser.parse(d['time_spent'][0])
		last =	dateutil.parser.parse(d['time_spent'][-1])
		time_spent.append(last-first)
		# determine last clicked document
		stoplist = set([])
		search_path = []
		for snip in d['search_depth']:
			if snip in stoplist: continue
			stoplist.add(snip)
			search_path.append(snip)
		search_depth.append(len(search_path))

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
		

def gen_logdata_table():
	# first get the data
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
	
	print 'basic'
	group_by_topic(data,0)
	print 'facet'
	group_by_topic(data,1)


if __name__ == '__main__':
	#gen_task_effort_table()
	gen_logdata_table()
