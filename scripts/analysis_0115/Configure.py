"""
Configuration to perform analysis
"""
import sys
sys.path.append('../trec_eval')
import trec_util, NDCG
import operator
import itertools

# parameter effect analysis based on effort
class paramEffectEffort(object):
   simulation_dir = '../../data/simulation/'
   # simulation_dir = '../../data/simulation_user/'
   output_dir = 'plots/param_effect'


# parameter effect analysis based on gain
class paramEffectGain(object): 
    simulation_dir = '../../data/gain_experiments_jan2015/simulation'
    # for user parameter
    #simulation_dir = '../../data/gain_experiments_jan2015/simulation_user'
    output_dir = 'plots/param_effect/'

# per query analysis based on effort
class perQueryEffort(object): 
    simulation_dir = '../../data/simulation'
    simulation_basic_dir = '../../data/simulation_basic'
    # for user parameter
    #simulation_dir = '../../data/simulation_user'
    #simulation_basic_dir = '../../data/simulation_basic'
    output_dir = 'plots/per_query_effort/'
    

# per query analysis based on gain
class perQueryGain(object): 
    simulation_dir = '../../data/gain_experiments_jan2015/simulation'
    #simulation_dir = '../../data/gain_experiments_jan2015/simulation_user'
    simulation_basic_dir = '../../data/gain_experiments_jan2015/simulation_basic'
    #simulation_basic_dir = '../../data/gain_experiments_jan2015/simulation_user_basic'
 
    output_dir = 'plots/per_query_gain/'
 

class generalDir(object):
    runfile = '../../data/testruns/nodup/run13.ql.nodup'
    qrelsfile = '../../data/FW13-QRELS-RM.txt'
    #categoryfile ='../data/resources-FW13-categorization.tsv'
    categoryfile = '../../data/official-resources-FW13-categorization.tsv'

class util(object):
    def load_categories(self, catefile):
        f = open(catefile)
        content = [d.split('\t') for d in f.readlines()]
        f.close()
        # category tuple: (site_id, category)	
        categories = [(d[0], d[3].split(',')) for d in content]
        return dict(categories)	

    def compute_ndcg(self, judged_list):
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
    def create_sublists(self, docs, judge, categories):
        origin_list = [(d[0], d[1]-1, judge[d[1]-1]) for d in docs]
        # compute the ndcg scores
        judged_list = [d[2] for d in origin_list]	
        ndcg_b, ndcg_g = self.compute_ndcg(judged_list)
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
            ndcg_b, ndcg_g = self.compute_ndcg(judged_list)
            B.append(ndcg_b)
            G.append(ndcg_g)
        return sublists, B, G
