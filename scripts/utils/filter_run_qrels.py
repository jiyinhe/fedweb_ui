"""
Only get judged results
"""
import sys
import os
sys.path.append(os.path.abspath('../trec_eval/'))
import trec_util
import itertools

def filter_run(run, qrels):
	docs = itertools.ifilter(lambda x: x[0] in qrels, run)	
	for r in run:
		if r[0] not in qrels:
			print r[0]

if len(sys.argv)<3:
	print 'usage: python filter_run_qrels.py runfile qrelsfile'
	sys.exit()



runfile = sys.argv[1]
qrelsfile = sys.argv[2]

outputfile = 'jd_%s'%sys.argv[0].split('/')[-1]

run = trec_util.load_TREC_run(runfile)
qrels = trec_util.load_qrels_all(qrelsfile)
for q in run:
	qid = q[0]
	docs = q[1]
	judge = qrels.get(qid,[])
	if not judge == []:
		filter_run(docs, judge)	

