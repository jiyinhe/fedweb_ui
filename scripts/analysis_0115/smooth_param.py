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

rc('font', **{'size': 20})


runfile = '../../data/testruns/nodup/run13.ql.nodup'
qrelsfile = '../../data/FW13-QRELS-RM.txt'
categoryfile = '../../data/official-resources-FW13-categorization.tsv'
 

def kl_div(scores):
    normalized = [s/sum(scores) for s in scores]  
    p_random = 1./len(scores)
    H_P = 0
    H_PQ = 0
    for p in normalized:
        if p > 0:
            H_P += - (p * log(p))
            H_PQ += -(p * log(p_random))

    kl = H_PQ - H_P 
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

    # look at KL div from uniform of each query 
    smooth = 0
    X = []
    Y = []
    while smooth < 2:
        kl = []
        for d in data:
            d_smooth = [dd+smooth for dd in d]
            kl.append(kl_div(d_smooth))
        print 'smooth = %s'%smooth
        print 'KL median:', np.median(kl), ',25q:', np.percentile(kl, 25), np.percentile(kl, 75)
        print
        Y.append(np.median(kl))
        X.append(smooth)
        smooth += 0.05
        
    pylab.plot(X, Y, linewidth=2)
    pylab.grid()
    pylab.savefig('plots/smooth_shape.png')

if __name__ == '__main__':
    u = util()
    run = trec_util.load_TREC_run(runfile)		
    qrels = trec_util.load_qrels(qrelsfile)
    judged_list = trec_util.judged_ranklist(run, qrels)
    categories = u.load_categories(generalDir.categoryfile)
    
    facets_data = {}
    S = []
    for q in run:
        docs = q[1]
        if not q[0] in judged_list:
            continue
        judge = judged_list.get(q[0])
        sublists, B, G = u.create_sublists(docs, judge, categories)

        # The ndcg scores to be used
        score = [b[-1] for b in B]

        # Normalize the score between 0 and 1
        max_b = max(score)
        min_b = min(score)
        score = [b/(max_b-min_b) for b in score]
        S.append(score)

    ndcg_distribution(S)

    pylab.show()

