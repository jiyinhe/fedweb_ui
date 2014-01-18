"""
reading TREC runs and qrels
"""

import itertools
import operator

def load_TREC_run(runfile):
	f = open(runfile)
	#run = [[[cc[0], cc[2], cc[3], cc[4]] for cc in c.split(' ')] for c in f.readlines()]
	run = []
	for c in f:
		strs = c.strip().split(' ')
		if len(strs) == 6:
			run.append([strs[0], strs[2], int(strs[3]), float(strs[4])])
		else:
			print 'ERROR in run file: ', strs
	f.close()
	per_qry = []
	# Sort by query	
	run.sort(key=operator.itemgetter(0))
	for k, g in itertools.groupby(run, lambda x: x[0]):
		docs = [d[1:] for d in g]
		# sort by rank
		ranklist = sorted(docs, key=lambda x: x[1])
		# group by query, sorted by doc score, then by docno 
		#ranklist = sorted(docs, key=lambda x: (-x[2], x[0]))
		#print [r[1] for r in ranklist], len(ranklist)
		per_qry.append((k, ranklist))
	return per_qry

def load_qrels(qrelfile):
	f = open(qrelfile)
	q = []
	for c in f:
		strs = c.strip().split(' ')
		if len(strs) == 4:
			if int(strs[3])>0:
				q.append((strs[0], strs[2], int(strs[3])))
		else:
			print 'ERROR in qrels file'
			print strs
	f.close()
	per_qry = []
	# Sort by query
	q.sort(key=operator.itemgetter(0))
	for k, g in itertools.groupby(q, lambda x: x[0]):
		docs = [(d[1], d[2]) for d in g]
		per_qry.append((k, dict(docs)))
	return dict(per_qry) 


def load_qrels_all(qrelfile):
	f = open(qrelfile)
	q = []
	for c in f:
		strs = c.strip().split(' ')
		if len(strs) == 4:
			q.append((strs[0], strs[2], int(strs[3])))
		else:
			print 'ERROR in qrels file'
			print strs
	f.close()
	per_qry = []
	# Sort by query
	q.sort(key=operator.itemgetter(0))
	for k, g in itertools.groupby(q, lambda x: x[0]):
		docs = [(d[1], d[2]) for d in g]
		per_qry.append((k, dict(docs)))
	return dict(per_qry) 


def judged_ranklist(run, qrels):
	res = []
	for q in run:
		qid = q[0]
		docs = [d[0] for d in q[1]]
		judge = qrels.get(qid)
		if judge == None:
			continue
		judged_list = [judge.get(d, 0) for d in docs]
		#if qid == '7003':
		#	Q = q[1][0:20]
	        #	print Q
		#	print [(i+1, judge.get(Q[i][0], 0)) for i in range(len(Q))]

		res.append((qid, judged_list))
	return dict(res)	
