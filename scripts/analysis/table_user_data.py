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
	
	

	# number of in progress

if __name__ == '__main__':
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
	
