"""
User effort best cases in terms of moves
"""
import trec_util
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
		
def simulate_category_ui(judged_list, run, categories):
	unique_cate = list(set([categories[c] for c in categories]))
	run = dict(run)
	for q in judged_list:
		sites = [d[0].split('-')[1] for d in run[q]]
		cate = [(i, categories[sites[i]]) for i in range(len(sites))] 
		cate.sort(key=operator.itemgetter(1))
		sublists = []
		judge = judged_list[q]
		# make it binary
		judge = [int(j>0) for j in judge]	
		if sum(judge) == 0:
			continue
		if sum(judge)>300:
			continue
		for c in unique_cate:
			sublist = list(itertools.ifilter(lambda x: x[1]==c, cate))
			#print sublist
			# Get judge for sublist
			jsub = [judge[s[0]] for s in sublist]	
			sublists.append(jsub)
			
		print q, sum(judge)
		bc = BrowseCategory(sublists)
		bc.min_effort(gain)

def simulate_basic_ui(judged_list):
	res = []
	for q in judged_list:
		qlist = judged_list[q] 
		# Use binary judge
		qlist = [int(x>0) for x in qlist]	
		# An unjudged query
		if sum(qlist) == 0:
			continue
		bb = BrowseBasic(qlist)
		cost = bb.min_effort(gain)
		res.append((q, cost))
	return dict(res)


if __name__ == '__main__':
	run = trec_util.load_TREC_run(runfile)		
	qrels = trec_util.load_qrels(qrelsfile)
	judged_list = trec_util.judged_ranklist(run, qrels)
	#basic = simulate_basic_ui(judged_list)

	# run simulation for the advanced interface
	categories = load_categories(categoryfile)
	cate = simulate_category_ui(judged_list, run, categories)
	
	


	

	
