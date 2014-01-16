"""
This script gets the judged documentIDs from the bookmark table
formats the docIDs into snippets
outputs ordered lists of:
topic docID relevance count snippet
"""
import sys
import os
import db_util as db
# To import the database setting
sys.path.append(os.path.abspath('../fw_userstudy/').rsplit('/', 1)[0])
from fw_userstudy import settings
from itertools import groupby

DB = settings.DATABASES['default']
user = DB['USER']
passwd = DB['PASSWORD']
database = DB['NAME']
host = DB['HOST']
conn = db.db_connect(host, user, passwd, database)

def produce_judgement_list():
	judgements = get_judgements()
	snippets = get_snippets()
	judgement_list = combine(judgements,snippets)
	output(judgement_list)


def get_judgements():
	qry = "select * from fedtask_bookmark;"
	res = db.run_qry_with_results(qry,conn)       
	# r[2]: turn topicID from long into integer
	# r[3]: strip the _bookmark suffix form doc id
	# r[4]: turn long judgement one of {-1L,1L} into integer
	judgements = [(int(r[2]),r[3].strip("_bookmark"),int(r[4])) for r in res]
	judgements = sorted(judgements, key=lambda x: x)
	for k, g in groupby(judgements, key=lambda x: x):
		print k , len(list(g)), list(g) 
	return judgements

def get_snippets():
	qry = "select * from fedtask_document;"
	res = db.run_qry_with_results(qry,conn)       
	# r[0]: docid
	# r[2]: get the title (first 80 characters) 
	# r[3]: get the summary (first 350 characters)
	# r[4]: get the url
	# put it as a key-tuple pair so it is easy to turn into dict
	snippets = [(r[0],(r[2],r[3],r[4])) for r in res]
	return snippets

def combine(judgements,snippets):
	sd = dict(snippets)
	for (tID,dID,jdg) in judgements:
		(tle,sum,url) = sd[dID]
		print tID, dID, tle, url, sum

	return []

def output(judgement_list):
	pass

produce_judgement_list()


