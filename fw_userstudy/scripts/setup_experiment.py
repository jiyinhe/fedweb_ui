"""
This script sets up an experiment with a between subject design

there are 4 experiments
0: basic UI, run13.bst.nodup
1: basic UI, run13.ql.nodup
2: category UI, run13.bst.nodup
3: category UI, run13.ql.nodup

"""

# Filling the type of UIs to be tested
UI = {
 1: 'basic UI, 10 blue links',
 2: 'basic UI + categorization of the sites from which the documents are fetched'
}

RUNS = {
#	1: 'run13.bst.nodup',
#	2: 'run13.ql.nodop'
	3: 'run13.ql.nodup',
}

# Set the experiment
Experiment_description = [
	# Descriptions of experiments
	{
		'ID': 0,  
		'DESC': 'Understanding user behaviour, the joint effect of UIxRanking\
				all topics with the same UI basic and run ql',
		'TASKS': [],
		'TYPE': 'Game',
		'PREQ': True,
		'POST': False,
		'TUT': True,
	},
	{
		'ID': 1,  
		'DESC': 'Understanding user behaviour, the joint effect of UIxRanking\
				all topics with the same UI category and run ql',
		'TASKS': [],
		'TYPE': 'Game',
		'PREQ': True,
		'POST': False,
		'TUT': True,
	},
]

# Set the tasks
import sys,simplejson
import os
sys.path.append(os.path.abspath('../fw_userstudy/').rsplit('/', 1)[0])
from fw_userstudy import settings
import db_util as db

DB = settings.DATABASES['default']
user = DB['USER']
passwd = DB['PASSWORD']
database = DB['NAME']
host = DB['HOST']
conn = db.db_connect(host, user, passwd, database)
maxclicks = settings.MaxClicks

qry='set foreign_key_checks=0'
db.run_qry(qry, conn)

print 'clearing UI table'
qry = 'delete from fedtask_ui'
db.run_qry(qry, conn)

print 'Storing UIs'
qry = 'delete from fedtask_ui'
db.run_qry(qry, conn)
for u_id in UI:
	qry = 'insert into fedtask_ui (ui_id, ui_description) values(%s, "%s")'%(u_id, UI[u_id])
	db.run_qry(qry, conn)

print 'clearing RUNS table'
qry = 'delete from fedtask_run'
db.run_qry(qry, conn)

print 'Storing RUNS'
qry = 'delete from fedtask_run'
db.run_qry(qry, conn)
for run_id in RUNS:
	qry = 'insert into fedtask_run (run_id, description)\
			values(%s,"%s")'%(run_id, RUNS[run_id])
	db.run_qry(qry, conn)


print 'clearing tasks table'
qry = 'delete from fedtask_task'
db.run_qry(qry, conn)
# Make tasks	
print "Fill task table"
qry = 'delete from fedtask_task'
db.run_qry(qry, conn)
qry = 'select run_id from fedtask_run'
runs = db.run_qry_with_results(qry, conn)
qry = 'select topic_id from fedtask_topic'
topics = db.run_qry_with_results(qry, conn)

# A task consists of: topic, run, ui
task_id = 1
expmnt_indx = 0
for r in RUNS:
	for u in UI: # add the tasks to an experiment here
		expmnt = Experiment_description[expmnt_indx]
		for t in topics:
			expmnt["TASKS"].append(task_id)
			qry = 'insert into fedtask_task (task_id, run_id,\
 topic_id, ui_id, maxclicks) values(%s, %s, %s, %s, %s)\
'%(task_id, r, t[0], u, maxclicks)
			db.run_qry(qry, conn)
			task_id += 1
		expmnt_indx+=1

print 'clearing experiment table'
qry = 'delete from fedtask_experiment'
db.run_qry(qry, conn)
# Store the experiments
print 'Storing experiments'
qry = 'delete from fedtask_experiment'
db.run_qry(qry, conn)
for e in Experiment_description:
	qry = 'insert into fedtask_experiment (experiment_id,\
			exp_description, exp_tasks, exp_type, pre_qst,\
			post_qst, tutorial)\
			values (%s, "%s", "%s", "%s", %s, %s, %s) '%(e['ID'], 
				e['DESC'], simplejson.dumps(e['TASKS']), e['TYPE'], e['PREQ'], 
				e['POST'], e['TUT'])
	db.run_qry(qry, conn)

qry='set foreign_key_checks=1'












