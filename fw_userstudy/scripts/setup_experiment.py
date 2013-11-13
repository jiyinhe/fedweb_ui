"""
This script set up the experiment

"""

# Filling the type of UIs to be tested
UI = {
	1: 'basic UI, 10 blue links',
	2: 'basic UI + categorization of the sites from which the documents are fetched'
}

# Set the experiment
Experiment_description = [
	# Descriptions of experiments
	{
		'ID': 1,  
		'DESC': 'Understanding user behaviour, the joint effect of UIxRanking',
		'TYPE': 'Thinkaloud',
		'PREQ': True,
		'POST': False,
		'TUT': True,
	},
	{
		'ID': 2,  
		'DESC': 'Measuring user search effectiveness/efficiency, the joint effect of UIxRanking',
		'TYPE': 'Crowdsourced',
		'PREQ': True,
		'POST': False,
		'TUT': True,
	},

]

# Set the tasks
import sys
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

print 'Storing UIs'
qry = 'delete from fedtask_ui'
db.run_qry(qry, conn)
for u_id in UI:
	qry = 'insert into fedtask_ui (ui_id, ui_description) values(%s, "%s")'%(u_id, UI[u_id])
	db.run_qry(qry, conn)

# Store the experiments
print 'Storing experiments'
qry = 'delete from fedtask_experiment'
db.run_qry(qry, conn)
for e in Experiment_description:
	qry = 'insert into fedtask_experiment (experiment_id, exp_description, exp_type, prequestionnaire, postquestionnaire, tutorial) values (%s, "%s", "%s", %s, %s, %s) '%(e['ID'], e['DESC'], e['TYPE'], e['PREQ'], e['POST'], e['TUT'])
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
for t in topics:
	for r in runs:
		for u in UI:
			qry = 'insert into fedtask_task (task_id, run_id, topic_id, ui_id) values(%s, %s, %s, %s)'%(task_id, r[0], t[0], u)
			db.run_qry(qry, conn)
			task_id += 1
			














