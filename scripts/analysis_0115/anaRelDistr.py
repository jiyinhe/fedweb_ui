"""
We compute the probability of benefiting from switching sublists at a position
of a ranked list assuming that a user is going down one of the sublists while
making decisions with respect to rest of the unexplored lists. 

Switching is beneficial when the E(gain@K)/E(effort@K) < E(gain@S)/E(effort@S)
Assuming unit effort and gain.
effort@K = 1 (examine), effort@S = 2 (switch + examine)
gain@K = P(rel@K) * 1 
gain@S = P(rel@S) * 1 where P(rel|S) only depends on the rank of the doc in that sublist 

Probability of getting benefits from switching
P(b@K) = # cases with benefits/#possible moves(including switching/continue) 

We cannot enumerate all possible switchings. We do MC sampling.
Users start with the first doc in the original list. 
Then compute the expected benefit from switching. 
If E(b) < 0, don't switch. 
If E(b) > 0, switch randomly to one of the possible landing position.

We do maximum X steps. 
i.e., We sample the pathes of length X. 


Probability that examine next at position K
is the joint probability that one there is a document
at position K, and the probability that a document at position K is relevant.


Jan. 2015
"""
import sys
sys.path.append('../trec_eval')
import trec_util, NDCG
import operator
import itertools
import numpy as np
import pylab
import random

runfile = '../../data/testruns/nodup/run13.ql.nodup'
qrelsfile = '../../data/FW13-QRELS-RM.txt'
#categoryfile ='../data/resources-FW13-categorization.tsv'
categoryfile = '../../data/official-resources-FW13-categorization.tsv'


max_steps =100
num_samples = 1000
examine_effort = 1.
switch_effort = 2.

def load_categories(catefile):
	f = open(catefile)
	content = [d.split('\t') for d in f.readlines()]
	f.close()
	# category tuple: (site_id, category)	
	categories = [(d[0], d[3].split(',')) for d in content]
	return dict(categories)	

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

# sublists based on categories
# each doc item is (docid, rank, relevance)
# rank is the index in the list, i.e., starting from 0
def create_sublists(docs, judge):
	origin_list = [(d[0], d[1]-1, judge[d[1]-1]) for d in docs]
	# compute the ndcg scores
	judged_list = [d[2] for d in origin_list]	
	ndcg_b, ndcg_g = compute_ndcg(judged_list)
	B = [ndcg_b]
	G = [ndcg_g]

	# Assign categories to documents	
	doc_cate = []
	for d in origin_list:
		cates = categories[d[0].split('-')[1]]
		tmp = [(d, c) for c in cates]
		doc_cate.extend(tmp)
	#print doc_cate

	sublists = [origin_list]	
	# Group docs into sublists by category
	doc_cate.sort(key=operator.itemgetter(1))
	for k, g in itertools.groupby(doc_cate, lambda x: x[1]):
		sublist = [d[0] for d in g] 
		# sort by rank
		sublist.sort(key=operator.itemgetter(1))
		# Add to the sublists
		sublists.append(sublist)
		# Get NDCG for the sublist
		judged_list = [d[2] for d in sublist]	
		ndcg_b, ndcg_g = compute_ndcg(judged_list)
		B.append(ndcg_b)
		G.append(ndcg_g)	
	return sublists, B, G		


# Compute the probability of benefiting from examining at rank k
# L is all the sublists aggregated  over all queries
# P(rel|exam, k) = #rel@k/#count_doc@k
# P(k exists) = #k exists/# sublists
# As the sublists are of different lengths, we stop at K when 
# the number of sublists at length K is smaller than 50.
def compute_prob_rel_exam(L):
	# first get the length of sublists
	lengths = sorted([len(l) for l in L])
	max_length = max(lengths)
	# Get counts of sublists >= length K 
	counts_length = dict([(i, 0) for i in range(0, max_length+1)])
	exact_counts = dict([(k, len(list(g))) for k, g in itertools.groupby(lengths)])
	for length in range(1, max_length+1):
		# Add this count to the current length
		current_count = exact_counts.get(length, 0)
		counts_length[length] += current_count
		# Sublist of current length is at least as long as
		# its previous lists, so add this count to them
		for l in range(1, length):
			counts_length[l] += current_count 

	# Now compute probability
	P = {}
	for position in range(1, max_length+1):
#		if counts_length[position] < 50:
#			break
		count_docs = sum([1 if len(sublist)>position else 0 for sublist in L])
			
		rel_at_position = sum([int(sublist[position][2]>0) if len(sublist)>position else 0 for sublist in L])
		p_rel_k = float(rel_at_position)/float(counts_length[position])
		p_exist_k = float(counts_length[position])/len(lengths)
		p = p_rel_k * p_exist_k
		P[position] = p
	return P


# P contains the probability of seeing a relevant doc at rank K
# LQ contains sublists of each query.
# For each query we sample N samples of length X
def sample_paths(sublist, P):
	# Record in all the paths, how many times switching
	# wins over examine at step X
	# Note: P index starts from 1
	counts_win = dict([(i, 0) for i in range(max_steps)])
	for sample in range(num_samples):
		# Start by randomly pick one sublist	
		step = 0
		# Candidates record the (list_id, position)
		candidates = [[l, 0] for l in range(len(sublists))]
		select = random.randint(0, len(candidates)-1)
		candidates[select][1] += 1
		while step < max_steps:
			# Now start compute expected gain and effort
			# If there is no more docs, then nothing to examine
			if len(sublists[select])<candidates[select][1]:
				examine_gain = 0
				# remove this list from candidates
				candidates.pop(select)
			else:
				examine_gain = P[candidates[select][1]+1]*1
			examine_utility = examine_gain/examine_effort 	 
			# For rest of the candidates, compute expected gain
			for i in range(len(candidates)):
				if i == select:
					continue
				switch_gain = P[candidates[i][1]+1]*1
				switch_utility = switch_gain/switch_effort
				if switch_utility > examine_utility:
					counts_win[step] = counts_win.get(step, 0) + 1
				
			# Now sample next step
			select = random.randint(0, len(candidates)-1)
			candidates[select][1] += 1 	
			step += 1

	counts_win = [(c,counts_win[c]/float(num_samples)) for c in counts_win]
	counts_win = sorted(counts_win, key=operator.itemgetter(0))
	return dict(counts_win)

# Load categories		
categories = load_categories(categoryfile)

if __name__ == '__main__':
	run = trec_util.load_TREC_run(runfile)		
	qrels = trec_util.load_qrels(qrelsfile)
	judged_list = trec_util.judged_ranklist(run, qrels)

	# An aggregated list of sublists over all queries
	L = []
	# Sublists per query
	LQ = []
	for q in run:
		docs = q[1]
		if not q[0] in judged_list:
			continue
		judge = judged_list.get(q[0])
		sublists, B, G = create_sublists(docs, judge)
		L += sublists
		LQ.append(sublists)

	# Some stats for the length of sublists	
	#lengths = [len(l) for l in L]
	#lengths = list(itertools.ifilter(lambda x: x<100, lengths))
	#n, bins, patches = pylab.hist(lengths, 20)
	#print 'sublists lengths: median=%s, min=%s, max=%s'%(np.median(lengths), min(lengths), max(lengths))
	#compute_prob_rel_exam(L)

	P = compute_prob_rel_exam(L)
	QP = [[] for i in range(max_steps)]
	# lopp over queries
	for sublist in LQ:
		# get probability of benefiting from switching at each step
		p_win = sample_paths(sublist, P)

		# aggregate over queries
		for i in range(max_steps):
			QP[i].append(p_win[i])
	# Make a plot
	X = [i for i in range(len(QP))]
	Y = []
	Y1 = []
	Y2 = []
	#loop over steps to get data to plot
	for i in range(max_steps):
		Y.append(np.median(QP[i]))
		Y1.append(np.percentile(QP[i], 75))
		Y2.append(np.percentile(QP[i], 25))

	pylab.plot(X, Y)
	pylab.fill_between(X, Y2, Y1, alpha=0.2)
	
	pylab.show()


