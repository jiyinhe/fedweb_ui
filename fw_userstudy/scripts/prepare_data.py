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
import simplejson
import xml.etree.ElementTree as et 
import re

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

# Clear all tables
def clear_tables():
	print 'Clear Topic table'
	qry = 'delete from fedtask_topic'
	db.run_qry(qry, conn)
	print 'Clear Site table'
	qry = 'delete from fedtask_site'
	db.run_qry(qry, conn)
	print 'Clear Qrels table'
	qry = 'delete from fedtask_qrels'
	db.run_qry(qry, conn)
	print 'Clear Run table'
	qry = 'delete from fedtask_run'
	db.run_qry(qry, conn)
	print 'Clear Document table'
	qry = 'delete from fedtask_document'
	db.run_qry(qry, conn)


# Topic table
def fill_topic_table(topicfile):
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
	print 'Fill the Site table'
	for c in f:
		strs = c.strip().split('\t')
		qry = 'insert into fedtask_site (site_id, site_name, site_url, category) values("%s", "%s", "%s", "%s") on duplicate key update site_name=site_name, site_url=site_url, category = category'%(strs[0], strs[1], strs[2], strs[3])
		db.run_qry(qry, conn)
	f.close()		 

# Qrels table
def fill_qrels_table(qrels):
	f = open(qrels)
	print 'Fill the Qrels table'
	for c in f:
		strs = c.strip().split(' ')
		# Only store relevant docs
		if not int(strs[-1]) == 0:
			#qrels.append((strs[0], strs[2], strs[3]))
			qry = 'insert into fedtask_qrels (topic_id, doc_id, relevance) values (%s, "%s", %s)'%(strs[0], strs[2], strs[3])
			db.run_qry(qry, conn)
	f.close()		

# Run table
def fill_run_table(rundir):
	files = os.listdir(rundir)
	for runfile in files:
		f = open('%s/%s'%(rundir, runfile))
		# Insert to run table
		qry = 'select max(run_id) from fedtask_run'
		res = db.run_qry_with_results(qry, conn)
		if res[0][0] == None:
			run_id = 1
		else:
			run_id = res[0][0] + 1

		run_desc = runfile
		qry = 'insert into fedtask_run (run_id, description) values (%s, "%s")'%(run_id, run_desc)
		db.run_qry(qry, conn)

		print 'Precessing run %s: %s'%(run_id, run_desc)
		current_q = ''
		docs = []
		for c in f:
			strs = c.strip().split(' ')
			qid = strs[0]
			docid = strs[2]	
			if not current_q == qid:
				if not current_q == '':
					ranklist = simplejson.dumps(docs)
					qry = "insert into fedtask_ranklist (run_id, topic_id, ranklist) values(%s, %s, '%s')"%(run_id, qid, ranklist)
					db.run_qry(qry, conn)
					docs = []
				current_q = qid
			docs.append(docid)
		ranklist = simplejson.dumps(docs)
		qry = "insert into fedtask_ranklist (run_id, topic_id, ranklist) values(%s, %s, '%s')"%(run_id, qid, ranklist)
		db.run_qry(qry, conn)
		f.close()	
	
# Document table
reg_snippet = '<snippet>'
def fill_doc_table(snippets_loc, docs_loc):
	print 'Process snippets and documents'
	# Get all sites
	qry = 'select distinct site_id from fedtask_site'
	sites = db.run_qry_with_results(qry, conn)
	# Get all topics
	qry = 'select distinct topic_id from fedtask_topic'
	topics = db.run_qry_with_results(qry, conn)
	# Get snippets of (site, topics)
	for s in sites:
		site_id = s[0]
		for t in topics:
			snippet_file = '%s/%s/%s.xml'%(snippets_loc, s[0], t[0])
			tree = et.parse(snippet_file)
			root = tree.getroot()
			# Snippet element
			snippets = root.find('search_results')[2]
			# Get info of each doc: doc_id, title, summary, url
			for sn in snippets:
				docid = sn.get('id')
				url = sn.find('link')
				title = sn.find('title')
				summary = sn.find('description')
				# Page link
				s_url = url.text
				sn_url = ''
				if not s_url == None:
					sn_url = s_url.replace('"', '\\"')
				# HTML_location
				doc_loc = url.get('cache')
				if doc_loc == None:
					doc_loc = ''
				# title
				sn_title = ''
				if not title == None:
					s_title = title.text
					if not s_title == None:
						sn_title = s_title.replace('"', '\\"').encode('utf-8')
				# summary
				sn_summary = ''
				if not summary == None: 
					s_summary = summary.text					
					if not s_summary == None:
						s_summary = s_summary.replace('\\', '') 
						sn_summary = s_summary.replace('"', '\\"').encode('utf-8')

				qry = 'insert into fedtask_document (doc_id, site_id, title, url, html_location, summary) values ("%s", "%s", "%s", "%s", "%s", "%s")'%(docid, site_id, sn_title, sn_url, doc_loc, sn_summary)	
				db.run_qry(qry, conn)
				

# Fill tables
clear_tables()
topics = fill_topic_table(topicfile)
fill_site_table(sitefile)
fill_qrels_table(qrels)
fill_run_table(rundir)
fill_doc_table(snippets, docs)




