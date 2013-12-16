"""
User effort best cases in terms of moves
"""
import trec_util

# Number of relevant document to be found
count_rel = 1
runfile = '../data/testruns/nodup/run13.ql.nodup'
qrelsfile = '../data/FW13-QRELS-RM.txt'

 

if __name__ == '__main__':
	run = trec_util.load_TREC_run(runfile)		
	qrels = trec_util.load_qrels(qrelsfile)
	trec_util.judged_ranklist(run, qrels)
