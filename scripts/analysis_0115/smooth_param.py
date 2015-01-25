"""
Determine how much smooth would be approperiate based
on the ndcg scores of sublists and number of sublists

NDCG score setting: binary, @all
"""
import sys
from Configure import util, generalDir
sys.path.append('../trec_eval')
import trec_util
import numpy as np
from numpy import log
import pylab
from matplotlib import rc
import operator
import itertools

rc('font', **{'size': 20})


runfile = '../../data/testruns/nodup/run13.ql.nodup'
qrelsfile = '../../data/FW13-QRELS-RM.txt'
categoryfile = '../../data/official-resources-FW13-categorization.tsv'
category_prob_file = '../analysis/data/facet_translated_catdist.data'

def load_category_pref():
	f = open(category_prob_file)
	prob = []
	for c in f:
		qid, cats = c.strip().split('\t')	
		prob.append((qid, eval(cats)))
	return dict(prob)

# sublists based on categories
# each doc item is (docid, rank, relevance)
# rank is the index in the list, i.e., starting from 0
def create_user_sublists(docs, judge, category_pref):
	origin_list = [(d[0], d[1]-1, judge[d[1]-1]) for d in docs]
	# Get user preference
	user_preference = category_pref.get('All', 1)  
	pref = [user_preference]
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
		category = k
		sublist = [d[0] for d in g] 
		# sort by rank
		sublist.sort(key=operator.itemgetter(1))
		# Add to the sublists
		sublists.append(sublist)
		# Get user preference of  the sublist
		user_preference = category_pref.get(k, 0)
		#print k, user_preference
		pref.append(user_preference)
	return sublists, pref		


def kl_div(scores, oracle):
    scores = [s/sum(scores) for s in scores]
    oracle = [s/sum(oracle) for s in oracle]
    i = 0
    # KL(P||Q) = sum_i p_i * log(p_i/q_i)
    # it's defined if both P, Q sum up to 1, and 
    # if Q(i)>0 for any i such that P(i)>0
    kl = 0
    for i in range(len(oracle)):
        if oracle[i] > 0:
            p_i = oracle[i]
            q_i = scores[i]
            kl += p_i * log(p_i/q_i)  
        i += 1
    return kl

# check the entropy of sublists in terms of NDCG
def ndcg_distribution(data):
    # number of sublists per query
    list_counts = [len(s) for s in data]
    print 'number of sublists per query', 'median:', np.median(list_counts), 
    print '25q:', np.percentile(list_counts, 25),
    print '75q:', np.percentile(list_counts, 75)
    print 'mean:', np.mean(list_counts) 
    print

    # look at KL div from oracle of each query
    smooth = 0
    X = []
    Y = []
    Z = []
    U = []
    while smooth < 2:
        kl = []
        kl_random = []
        kl_user = []
        for d in data:
            oracle, userpref = d
            oracle = [dd for dd in oracle]

            d_smooth = [dd+smooth for dd in oracle]
            kl.append(kl_div(d_smooth, oracle))
            # add divergence of uniform from oracle as upper bound
            u = [1. for i in range(len(oracle))]
            kl_random.append(kl_div(u, oracle))

            # also calculate the user's divergence
            # add a small smooth to avoid 0 probability
            userpref = [u+0.0001 for u in userpref]
            kl_user.append(kl_div(userpref, oracle))

#        print 'smooth = %s'%smooth
#        print 'KL median:', np.median(kl), ',25q:', np.percentile(kl, 25), np.percentile(kl, 75)
#        print
        Y.append(np.median(kl))
        X.append(smooth)
        Z.append(np.median(kl_random))
        U = kl_user
        smooth += 0.05

    pylab.plot(X, Y, linewidth=2)
    pylab.plot(X, Z, '--r', linewidth=2)
    pylab.grid()
         
#    for u in U:
#        y = [u for i in range(len(X))]
#        pylab.plot(X, y, ':b', linewidth=2)

    pylab.savefig('plots/smooth_shape.png')




if __name__ == '__main__':
    u = util()
    run = trec_util.load_TREC_run(runfile)		
    qrels = trec_util.load_qrels(qrelsfile)
    judged_list = trec_util.judged_ranklist(run, qrels)
    categories = u.load_categories(generalDir.categoryfile)

    category_pref = load_category_pref()
    print category_pref
 
    facets_data = {}
    S = []
    U = []
    for q in run:
        docs = q[1]
        if not q[0] in judged_list:
            continue
        judge = judged_list.get(q[0])
        sublists, B, G = u.create_sublists(docs, judge, categories)

        u_sublists, user_pref = create_user_sublists(docs, judge, category_pref[q[0]])

        # The ndcg scores to be used
        score = [b[-1] for b in B]

        # Normalize the score between 0 and 1
        max_b = max(score)
        min_b = min(score)
        score = [b/(max_b-min_b) for b in score]
        S.append((score, user_pref))

    ndcg_distribution(S)

    pylab.show()

