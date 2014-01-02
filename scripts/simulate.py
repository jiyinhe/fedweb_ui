"""
User effort best cases in terms of moves
"""
from trec_eval import trec_util
import itertools
from browse import BrowseBasic, BrowseCategory
import operator
# Number of relevant document to be found
count_rel = 1
runfile = '../data/testruns/nodup/run13.ql.nodup'
qrelsfile = '../data/FW13-QRELS-RM.txt'
categoryfile ='../data/resources-FW13-categorization.tsv'

# find 10 relevant documents
gain = 10

def load_categories(catefile):
	f = open(catefile)
	content = [d.split('\t') for d in f.readlines()]
	f.close()
	categories = [(d[0], d[3]) for d in content]
	return dict(categories)	
		

if __name__ == '__main__':
	run = trec_util.load_TREC_run(runfile)		
	qrels = trec_util.load_qrels(qrelsfile)
	judged_list = trec_util.judged_ranklist(run, qrels)
	
	


	

	
