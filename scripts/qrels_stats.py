"""
Get following stats:
 - # doc ret per query
 - # doc rel per query
 - # site ret per query
 - # site category covered per query
 - # rel cate per query
"""
import itertools
catefile = '../data/resources-FW13-categorization.tsv'
dupfile = '../data/duplicates.txt'
qrelsfile = '../data/FW13-QRELS-RM.txt'
topicfile = '../data/FW13-topics.txt'

def load_engine_category(inputfile):
	sites = []
	f = open(inputfile)
	for c in f:
		strs = c.strip().split('\t')
		site_id = strs[0]
		cate = strs[3]
		sites.append((site_id, cate))
	f.close()
	return dict(sites)


def load_duplicate(inputfile): 
	dupId = 0
	dup = {}
	f = open(inputfile)
	for c in f:
		dupId += 1
		strs = c.strip().split('\t')
		for s in strs[1:]:
			dup[s] = dupId 
	f.close()
	return dup

def load_qrels(inputfile):
	f = open(inputfile)
	qrels = []
	for c in f:
		strs = c.strip().split(' ')
		site = strs[2].split('-')[1]
		qrels.append((strs[0], strs[2], strs[3], site))
	f.close()
	return qrels

def load_topics(inputfile):
	f = open(inputfile)
	topics = {}
	for c in f:
		strs = c.strip().split(':')
		topics[strs[0]] = strs[1]
	f.close()
	return topics

# topics: {topicid: topic}
# sites: {siteid: category} 
# dups: {docid: dupId} 
# qrels: [(qid, docid, rel, site)]
def get_stats(qrels, dups, sites, topics):
	qids = sorted(list(set([q[0] for q in qrels])))
	print 'qid', 'doc_ret', 'rel_ret', '#site', '#category', '#rel_category', 'topic'
	for q in qids:
		docs = list(itertools.ifilter(lambda x: x[0] == q, qrels))
		# reduce duplicate docs
		docs = [(dups.get(d[1], d[1]), int(d[2]), d[3]) for d in docs]
		rel_docs = list(itertools.ifilter(lambda x: x[1]>0, docs))
		# Get counts
		# count_docs = len(docs)
		count_docs_nodup = len(set([d[0] for d in docs]))
		count_sites = len(set(d[2] for d in docs))
		count_rel_docs = len(set([d[0] for d in rel_docs]))	
		count_cate = len(set([sites[d[2]] for d in docs]))
		count_rel_cate = len(set([sites[d[2]] for d in rel_docs]))
		print q, '\t', count_docs_nodup, '\t', count_rel_docs,'\t', count_sites, '\t', 
		print count_cate, '\t', count_rel_cate, '\t', topics[q] 
	

	
sites = load_engine_category(catefile)
dups = load_duplicate(dupfile)
qrels = load_qrels(qrelsfile)
topics = load_topics(topicfile)
get_stats(qrels, dups, sites, topics)


