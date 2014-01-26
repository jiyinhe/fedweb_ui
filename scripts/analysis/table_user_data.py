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

	# a list of (task,user) tuples indicating the number of users that
	# completed a task
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
	# 		completed tasks				effort spend
	#	basic			facet		basic			facet
	# tot, md, IQR  tot, md, IQR  tot, md, IQR  tot, md, IQR
	print table_header_row(["","completed tasks","effort spent"],
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
#					basic			facet	
#				tot md IQR		tot md IQR	
# bookmark
# category
# paginate
# search depth 
# time spent
# nr of hovers
# effort
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
			search_depth.append(last_click)
	if not td: sys.exit()
	rows = [
	["posbookmark", 	sum(posbookmark),
						np.median(posbookmark),
						"(%.1f-%.1f)"%(np.percentile(posbookmark,25),np.percentile(posbookmark,75))],
	["negbookmark", 	sum(negbookmark),
						np.median(negbookmark),
						"(%.1f-%.1f)"%(np.percentile(negbookmark,25),np.percentile(negbookmark,75))],
	["category",		sum(category),
						np.median(category),
						"(%.1f-%.1f)"%(np.percentile(category,25),np.percentile(category,75))],
	["paginate", 		sum(paginate),
						np.median(paginate),
						"(%.1f-%.1f)"%(np.percentile(paginate,25),np.percentile(paginate,75))],
	["hovers", 			sum(hovers),
						np.median(hovers),
						"(%.1f-%.1f)"%(np.percentile(hovers,25),np.percentile(hovers,75))],
	["search depth", 	sum(search_depth),
						np.median(search_depth),
						"(%.1f-%.1f)"%(np.percentile(search_depth,25),np.percentile(search_depth,75))],
	["time spent", 	sum(time_spent),
					np.median(time_spent),
					"(%.1f-%.1f)"%(np.percentile(time_spent,25),np.percentile(time_spent,75))]]
	return rows


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
		#inputfile = "../../fw_userstudy/scripts/log_utils/alldata_24-01-2014_13:13.log"
		inputfile = "../../fw_userstudy/scripts/log_utils/alldata_26-01-2014_11:00.log"
		#inputfile = "clicks_24-01-2014_13:00.log"
		ld = LogData.LogData()
		ld.load_data(inputfile)
		data = ld.group_logevents_by_user_and_query()

		# filter the data
		# remove events (hovers) on non-task pages
		page = 'http://zookst9.science.uva.nl:8002/study/task/'
		data = ld.filter(data, {'location':page,
								'order':0})# order on date
		ld.cache2file("table2.tmp",data)
	else:
		fh = open('table2.tmp')
		data = eval(fh.read())
		fh.close()
	
	print 'basic'
	td = group_by_topic(data,0)
	basic_rows = log_summary_table(td)
	sddist = search_depth_distribution(td)
	write_data('basic_searchdepth.data',sddist)
	print 'facet'
	td = group_by_topic(data,1)
	facet_rows = log_summary_table(td)
	catdist = category_distribution(td)
	write_data('facet_catdist.data',catdist)
	sddist = search_depth_distribution(td)
	write_data('facet_searchdepth.data',sddist)

	print "\hline"
	print table_header_row(["","basic"], [(1,'c'),(3,'c')])
	print "\hline"
	print table_header_row(["","total","median","IQR"])
	print "\hline"

	for r in basic_rows:
		type = r[0]
		basic_row = r[1:]
		print table_row([type] + basic_row)

	print "\hline"
	print table_header_row(["","facet"], [(1,'c'),(3,'c')])
	print "\hline"
	print table_header_row(["","total","median","IQR"])
	print "\hline"

	for r in facet_rows:
		type = r[0]
		facet_row = r[1:]
		print table_row([type] + facet_row)

def write_data(fname, data):
	fh = open('data/'+fname,'w')
	for (k,v) in data:
		fh.write("%s	%s\n"%(k,v))
	fh.close()

def output_sessions():
	fh = open('table.tmp')
	data = eval(fh.read())
	fh.close()
	for (k,v) in data.items():
		print ", ".join([ el[2] for el in v if el[2] != 'mouse_click' and
el[2] != 'mouse_movements'])

def output_searchdepth(condition):
	fh = open('table.tmp')
	data = eval(fh.read())
	fh.close()
	td = group_by_topic(data,condition)

	topics = ['7040', '7042', '7046', '7047', '7084', '7056', '7129',
	'7067', '7068', '7069', '7075',
	'7076', '7080', '7209', '7132', '7087', '7089', '7090', '7407',
	'7348', '7094', '7096',
	'7097', '7099', '7465', '7103', '7109', '7115', '7504', '7505',
	'7506', '7124', '7127',
	'7001', '7258', '7003', '7004', '7007', '7009', '7145', '7018',
	'7404', '7406', '7485',
	'7025', '7030', '7415', '7033', '7034', '7039']
	topics.sort()

	medians = []
	for k in topics:
		if int(k) in td:
			lst = td[int(k)]
		else:
			lst = []
		search_depth = []
		for d in lst:
			if not d['done']: continue
			# determine last clicked document
			last_click = find_last_click_depth(d['search_depth'],d['last_click'])
			last_click +=sum(d['category'].values()) + d['paginate']
			print last_click
			search_depth.append(last_click)
		if search_depth:
			m = np.median(np.array(search_depth))
		else:
			m = 0
		medians.append((k,m))
	medians.sort()
	return [m[1] for m in medians]

# a row looks like this:
# id  | user_id | IP              | gender | year_of_birth |
# computer_exp | english_exp | search_exp | education | consent

def gen_demographics():
	qry = "select * from questionnaire_userprofile where user_id > 26\
 and user_id != 37 and user_id != 45;"
	us = UserData.UserData()
	rows = us.load_data(qry)
	gender = [r[3] for r in rows]
	year_of_birth = [r[4] for r in rows]
	computer_exp = [r[5] for r in rows]
	english_exp = [r[6] for r in rows]
	search_exp = [r[7] for r in rows]
	education = [r[8] for r in rows]
	
	print "gender", count_elements(gender).items()
	print "education", count_elements(education).items()
	print "age", desc_stats(year_of_birth)
	print "compexp", desc_stats(computer_exp)
	print "searchexp", desc_stats(search_exp)
	print "englishexp", desc_stats(english_exp)

def desc_stats(lst):
	arr = np.array(lst)
	return np.median(arr),"(%.1f-%.1f)"%(np.percentile(arr,25),np.percentile(arr,75))
	

def count_elements(lst):
	d = {}
	for k in lst:
		if k in d:
			d[k]+=1
		else:
			d[k]=1
	return d

	

if __name__ == '__main__':
	#gen_task_effort_table()
	#gen_logdata_table()
	#output_sessions()
	#output_searchdepth(1)
	gen_demographics()	
