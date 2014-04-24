import trec_util
import sys
import math

class NDCG:

	# Input the ranked list with relevance judgement
	# e.g.,  [1, 0, 0, 1] means the 1st and 4th document in the ranked list
	# are relevant, given binary judgement.
	# K: ndcg@K
	def __init__(self, judged_rank):
		self.judged_rank = judged_rank

	def DCG(self, X, K):
		if K == -1:
			length = len(X)
		else:
			length = min(K, len(X))
		
		# index starts from 1
		score = [(2**X[i-1]-1)/math.log((i+1)) for i in range(1, length+1)] 

		#print len(score)
		#Javelin
		#score = [ X[i]/math.log(i+1, 2) for i in range(1, length)]
		#score.append(X[0])
		return sum(score), score	

	def ndcg(self, K):
		X = self.judged_rank
		# Sort the whole judgement list
		# Note: we should sort all judged documents, instead of the retrieved judgemed docs
		# However, in this project as all documents were judged, it wouldn't make a difference
		# It needs to be changed for other usage.
		iX = sorted(self.judged_rank, reverse=True) 
		iDCG, score1 = self.DCG(iX, K)
		DCG, score2 = self.DCG(X, K)
		#print score2
		#print DCG, iDCG
		#print iDCG, DCG
		if iDCG == 0:
			return 0
		return DCG/iDCG


if __name__ == '__main__':
#	X = [3, 2, 3, 0, 1, 2]
#	n = NDCG(X)
#	print n.DCG(X, 6), n.DCG(sorted(X, reverse=True), 6), n.ndcg(6)
	
	if len(sys.argv)<4:
		print 'usage python NDCG.py qrels run @K (K=-1 for computing NDCG)'
		sys.exit()

	qrelfile = sys.argv[1]
	runfile = sys.argv[2]
	K = int(sys.argv[3])

	qrels = trec_util.load_qrels(qrelfile)
	run = trec_util.load_TREC_run(runfile)
	judged_results = trec_util.judged_ranklist(run, qrels)
	x = 0
	sum_x = 0
	for q in sorted(judged_results.keys()):
		if q in qrels:
			j = judged_results[q]
			# make it binary
			j = [int(x>0) for x in j]
			ndcg = NDCG(j)
			#print q, 
			#print [(i, judged_results[q][i]) for i in range(len(judged_results[q][0:K]))]
			#print 'DCG:', ndcg.DCG(judged_results[q], K)
			#print 'iDCG:', ndcg.DCG(sorted(judged_results[q], reverse=True), K)
			print q, '%.4f'%ndcg.ndcg(K)	
			#print
			sum_x += ndcg.ndcg(K)
			x += 1
	print 'mean', sum_x/float(x)
