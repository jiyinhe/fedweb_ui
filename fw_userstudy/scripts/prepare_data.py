"""
This script prepare the data needed in the 
experiment. We use the TREC FedWeb13 data.
Includes:
 - Topic
 - Document
 - Site
 - Run (duplicate removed)
 - Qrels
"""
import sys
import os
import db_util as db
# To import the database setting
sys.path.append(os.path.abspath('../fw_userstudy/').rsplit('/', 1)[0])
from fw_userstudy import settings
import itertools

DB = settings.DATABASES['default']
user = DB['USER']
passwd = DB['PASSWORD']
database = DB['NAME']
host = DB['HOST']
conn = db.db_connect(host, user, passwd, database)

# A topic file in the format of: topicid:topic_text
topicfile = '../../data/FW13-topics.txt'
# Remember to remove the duplicates in the runfiles
rundir = '../../data/testruns/nodup'
# Site categorization
sitefile = '../../data/resources-FW13-categorization.tsv'
# Qrels
qrels = '../../data/FW13-QRELS-RM.txt'
# Snippets: FW13-topics-search/eXXX/topicid.xml
# HTML documents: FW13-topics-docs/eXXX/topicid_rank.html
snippets = '%s/FW13-topics-search/'%settings.DATA_ROOT
docs = '%s/FW13-topics-docs'%settings.DATA_ROOT

# Topic table
def fill_topic_table(topicfile, conn):
	f = open(topicfile)
	print 'Fill the Topic table'
	topics = []
	for c in f:
		strs = c.strip().split(':')
		qry = 'insert into fedtask_topic (topic_id, topic_text) values(%s, "%s") on duplicate key update topic_text=topic_text;'%(strs[0], strs[1].replace('"', '\\"'))
		db.run_qry(qry, conn)
		topics.append(strs)
	f.close()
	return topics

# Site table
def fill_site_table(sitefile):
	f = open(sitefile)
	print 'Fill the site table'
	for c in f:
		strs = c.strip().split('\t')
		qry = 'insert into fedtask_site (site_id, site_name, site_url, category) values("%s", "%s", "%s", "%s")'%(strs[0], strs[1], strs[2], strs[3])
		db.run_qry(qry, conn)
	f.close()		 
# Qrels table
def load_qrels(qrels):
	f = open(qrels)
	qrels = []
	for c in f:
		strs = c.strip().split(' ')
		if not int(strs[-1]) == 0:
			qrels.append((strs[0], strs[2], strs[3]))
	return qrels
	f.close()		

# Run table
def load_runs(rundir):
	files = os.listdir(rundir)
	runs = []
	for runfile in files:
		f = open('%s/%s'%(rundir, runfile))
		run = []
		for c in f:
			strs = c.strip().split(' ')
			run.append((strs[0], strs[2]))	
		f.close()	
		runs.append(run)
	return runs

# Document table


topics = fill_topic_table(topicfile, conn)
fill_site_table(sitefile)
qrels = load_qrels(qrels)
runs = load_runs(rundir)




