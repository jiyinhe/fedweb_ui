"""
The purpose of this script is to produce a table with examples of relevant and
irrelevant documents to be shown to the user.

We pick our examples in 2 ways:
- an irrelevant document is picked based on the number of times it has been
  selected by a player (as recorded in the bookmarks table)
- a relevant document is picked based on its highest level of relevance first
  and then based on the number of times it has been selected. 

if a topic has no selected documents then we use the qrels to pick a document
 - we order the relevant documents based on relevance level 0-7 and pick the
   first element from the list as negative example and the last element as
   positive example.

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
QRELSFILE = "../../data/FW13-QRELS-RM.txt"


# main function
def produce_judgement_list():
    judgements = get_judgements()
    snippets = get_snippets()
#    qrels = get_qrels()        
    qrels = get_qrels_from_file(QRELSFILE)        
# combine snippets, relevance, and click frequency
    judgement_list = combine(judgements,snippets,qrels)
#    output(judgement_list)
#    output_csv(judgement_list)
    examples = click_based_examples(judgement_list)
    qrel_based_examples(examples, qrels)


def create_table(examples):
    rows = examples.items()
    rows.sort()
    qry = "insert into fedtask_examples (topic_id, doc_id, rel, cnt, use) VALUES (%d, %d, %d, %d, %d);"
    for (k,v) in rows:
        print k,v

# find examples based on the frequency that users clicked a particular document
# for a topic. Produces a dictionary with two keys for each topic, i.e., a
# postive example key (tID,1) and a negative example key (tID,-1) 
def click_based_examples(judgement_list):
    # group document tuples based on tID x[0] and relevance x[2]
    j_list = groupby(judgement_list, key=lambda x: (x[0],x[2]))
    table = {}
    for  k,g in j_list:
        (tID,jdg) = k
        if jdg == -1: # neg example sort on frequency
            max = sorted(list(g), key=lambda x: x[3],reverse=True)
        else: # pos example sort on relevance, then frequency
            max = sorted(list(g), key=lambda x: (x[4],x[3]),reverse=True)
        (tID,dID,jdg,cnt,rel,tle,url,sum) = max[0]
#        print "max:", [(tID,dID,jdg,cnt,rel) for (tID,dID,jdg,cnt,rel,tle,url,sum) in max[:3]]
#        db.run_qry(qry%(tID,dID,cnt,rel),conn)
#        print "max:", max[0]
        table[(tID,jdg)]=(tID,dID,rel)
    return table

#In case no relevant/irrelevant document has been selected for a topic,
# supplement examples based on the qrels.
def qrel_based_examples(examples,qrels):
    qrels = [(tID,rel,dID) for ((tID,dID),rel) in qrels]
    qrels.sort()        
# group qrels based on topicID x[0]
    qrels = groupby(qrels,key=lambda x: x[0])
    for k,g in qrels:
        group = list(g)
# sort a list of relevance judgements within a topic 
        group.sort()
# select the min and max
        min = group[0]
        max = group[-1]
# if the min irrelevant and the max relevant?
        if not min[1] == 0:
            print "error", min, "is not irrelevant"
        if not max[1] > 0:
            print "error", max, "is not irrelevant"
#   insert the min and max in the examples if they are not already examples available
        if not (k,-1) in examples:
            tID,rel,dID = min
            examples[(tID,-1)]=(tID,dID,rel)                
        if not (k,1) in examples:
            tID,rel,dID = max
            examples[(tID,1)]=(tID,dID,rel)                

def get_judgements():
	qry = "select * from fedtask_bookmark;"
	res = db.run_qry_with_results(qry,conn)       
	# r[2]: turn topicID from long into integer
	# r[3]: strip the _bookmark suffix form doc id
	# r[4]: turn long judgement one of {-1L,1L} into integer
	judgements = [(int(r[2]),r[3].strip("_bookmark"),int(r[4])) for r in res]
	# sort first on topic ID, then docID then relevance
	judgements = sorted(judgements, key=lambda x: (x[0],x[1],x[2]))
	# groupby topicID,docID,rel and count the group lengths
	judgements = [(k[0],k[1],k[2],len(list(g))) for k, g in groupby(judgements, key=lambda x: (x[0],x[1],x[2]))]
	# sort again now also with group length
	judgements = sorted(judgements, key=lambda x: (x[0],x[2],x[1]))
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

# get the qrels form file
# here we do have non relevant documents 
def get_qrels_from_file(file): 
    fh = open(file,'r')
    text = fh.read() 
    fh.close()
    lines = text.split("\n")
    qrels = []
    for l in lines:
        l = l.strip()
        if l:
            tID,void,dID,rel = l.split()
            qrels.append(((int(tID),dID),int(rel)))
    return qrels

# get the qrels form the database
# the non relevant documents are missing here
def get_qrels():
    qry = "select * from fedtask_qrels"
    res = db.run_qry_with_results(qry,conn)       
# r[1] topicID
# r[2] doc id
# r[3] relevance
# put as key-value pair for easy dict creation
    qrels = [((int(r[1]),r[2]),int(r[3])) for r in res]
    return qrels

# util functions to inspect the topics, and snippets, and output them
def combine(judgements,snippets,qrels):
    sd = dict(snippets)
    qd = dict(qrels)
    combined = []       
    for (tID,dID,jdg,cnt) in judgements:
        (tle,sum,url) = sd[dID]
        k = (tID,dID)            
        rel = 0
        if k in qd: 
            rel = qd[k]
        combined.append((tID, dID, jdg, cnt, rel, tle, url, sum))
    return combined

def output(judgement_list):
    for (tID,dID,jdg,cnt, rel, tle,url,sum) in judgement_list:
        print tID, dID, jdg, cnt, rel
#        print tle[:80]
#        print url
#        print sum[:350]
#        print

def output_csv(judgement_list):
    t = "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'"        
    for (tID,dID,jdg,cnt,rel,tle,url,sum) in judgement_list:
        print t%(str(tID), str(dID), str(jdg), str(cnt),str(rel),tle[:80].replace(","," ").replace('\n'," "),url.replace(","," ").replace('\n'," "),sum[:350].replace(","," ").replace('\n'," "))


produce_judgement_list()


