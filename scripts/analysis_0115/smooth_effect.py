"""
Study the effect of different smooth parameters
, i.e., different user qualities ranging from 
very accurate to almost random

Prepare the data for R

dependent variable: counts facet > basic
independent variables: 
- user quality
- facet entropy
- basic performance (difficulty of query)
- task type
"""
import sys
sys.path.append('../trec_eval')
import trec_util, NDCG 
import numpy as np
from math import log
import load_data as ld
import itertools
from Configure import generalDir, util

datadir_basic = '../../data/simulation_basic/'
datadir_smooth = '../../data/simulation_smooth3/'
outdir = 'data/'

# only consider these user accuracy parameters
u_levels = ['0', '0.1', '0.5', '1']

runfile = generalDir.runfile
qrelsfile = generalDir.qrelsfile
categoryfile = generalDir.categoryfile

u = util()


def make_data(basic_data, smooth_data, pa_b, pa, facet_entropy):
    # header
    # map user quality to levels
    for b in basic_data:
        # independent variable task
        task = pa_b[int(b)][4]
        b_data =  basic_data[b]
        # find correponding faceted simulation with the same task
        task_p = list(itertools.ifilter(lambda x: x[5]==task, pa))
        D = [','.join(['diff', 'f_entropy', 'f_relevance', 'q_difficulty', 'u_quality'])]
        for p in task_p:
            idx = p[0]
            s_data = smooth_data[idx]
            # independent variable  user level
            u_level = p[-1]
            if not u_level in u_levels:
                continue
            for q in s_data:
                # independent variable query difficulty
                basic_performance = b_data[q][0]
                # independent varialbe facet entropy
                entropy, mean_ndcg = facet_entropy[q]
                # dependent variable diff
                diff = b_data[q] - np.median(s_data[q]) 
                diff = int(diff[0]>0)

                line = [str(diff), str(entropy), str(mean_ndcg), str(basic_performance), str(u_level)]
                D.append(','.join(line))
        f = open('%s/smooth_data_task%s.csv'%(outdir, task), 'w')
        f.write('\n'.join(D))
        f.close() 

 
# Entropy of NDCG scores
def sublist_entropy(scores):
    tot_score = sum(scores)
    H = 0
    for s in scores:
        if s > 0:
            p = s/tot_score
            H += - p * log(p)
    return H

# Prepare data to describe the properties of the sublists
# hypothesis:
# - sublist needs to contain diverse relevant info, and 
# to be able to seperate relevant versus non-relevant info
# to be useful.   
def prepare_data_sublists():
    run = trec_util.load_TREC_run(runfile)		
    qrels = trec_util.load_qrels(qrelsfile)
    judged_list = trec_util.judged_ranklist(run, qrels)
    categories = u.load_categories(generalDir.categoryfile)
    
    facets_data = {}
    for q in run:
        docs = q[1]
        if not q[0] in judged_list:
            continue
        judge = judged_list.get(q[0])
        sublists, B, G = u.create_sublists(docs, judge, categories)

        ndcg_scores = [b[-1] for b in B]
        entropy = sublist_entropy(ndcg_scores)
        mean_ndcg_scores = np.mean(ndcg_scores)

        facets_data[q[0]] = (entropy, mean_ndcg_scores)
    return facets_data 


if __name__ == '__main__':
    # load data
    pafile = '%s/param.txt'%(datadir_basic)
    pa_b = ld.load_parameter_record(pafile) 
    basic_data = ld.load_data(datadir_basic, pa_b)

    pafile = '%s/param.txt'%(datadir_smooth)
    pa = ld.load_parameter_record(pafile) 
    smooth_data = ld.load_data(datadir_smooth, pa)

    facet_entropy = prepare_data_sublists()

    make_data(basic_data, smooth_data, pa_b, pa, facet_entropy)   



