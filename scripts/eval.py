"""
Generate ndcg scores for the original ranked list
"""
from trec_eval import trec_util, NDCG

runfile = '../data/testruns/nodup/run13.ql.nodup'
qrelsfile = '../data/FW13-QRELS-RM.txt'

def compute_ndcg(judged_list):
	# compute the ndcg scores	
	judge_b = [int(d>0) for d in judged_list]
	judge_g = [d for d in judged_list]
	n1 = NDCG.NDCG(judge_b)
	n2 = NDCG.NDCG(judge_g)
	ndcg_b = [[k, n1.ndcg(k)] for k in [1, 10, 20, len(judged_list)]]
	ndcg_b[-1][0] = -1
	ndcg_g = [[k, n2.ndcg(k)] for k in [1, 10, 20, len(judged_list)]]
	ndcg_g[-1][0] = -1
	return dict(ndcg_b), dict(ndcg_g)

run = trec_util.load_TREC_run(runfile)		
qrels = trec_util.load_qrels(qrelsfile)
judged_list = trec_util.judged_ranklist(run, qrels)
print 'QID\tNDCG@1_B\tNDCG@10_B\tNDCG@20_B\tNDCG_B\tNDCG@1_G\tNDCG@10_G\tNDCG@20_G\tNDCG_G'
for q in judged_list:
	judged = judged_list[q]
	# Binary and graded
	b, g = compute_ndcg(judged)
	print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s'%(q,b[1],b[10],b[20],b[-1],g[1],g[10],g[20],g[-1])  













