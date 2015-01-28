"""
User effort best cases in terms of moves

This is a copy of simulate.py
It is used for simulating users with different prior knowledge.
- perfect: NDCG
- random: uniform
- in betwee: adding smooth to NDCG prior

To run this simulation, the following parameters can be fixed:
lambda: 0.01
f_prior: NDCG

varying parameters:
task_length: 1, 10, -1
smooth: 

"""
from trec_eval import trec_util, NDCG
import itertools
import operator
from user_model import Interaction, EffortModel, GainModel, ExamineModel, FilterModel 
from user_model import Parameters as P
import sys
import os

runfile = '../data/testruns/nodup/run13.ql.nodup'
qrelsfile = '../data/FW13-QRELS-RM.txt'
#categoryfile ='../data/resources-FW13-categorization.tsv'
categoryfile = '../data/official-resources-FW13-categorization.tsv'

def generate_parameters():
    if P.interface == 'basic':
        params = ['index', 'page_size', 'gain_type', 'e_model', 'task_length']
        p = itertools.product(P.page_size, P.gain_model_type, P.e_model_type, P.task_length)
        p = list(p)
    else:
        params = ['index', 'page_size', 'gain_type', 'ndcg_k','e_model',
        'task_length', 'f_model', 'f_prior',
        'e_lambda', 'smooth'    
            ]
        p = itertools.product(P.page_size, P.gain_model_type, P.ndcg_k, P.e_model_type, P.task_length, P.f_model_type, P.f_prior, P.e_lambda, P.smooth)
        p = list(p)
        p = list(itertools.ifilter(lambda x: not(x[6]==None and x[8]>0), p))
    pa = [[i, list(p[i])] for i in range(len(p))]
    for p in pa:
        print p
    print
    return pa, params
 
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

"""
simulate interaction with basic interface  
"""    
def simulate_basic(judged_list, page_size, task_length):
    action_list = []
    rel_count = 0
    doc_count = 0
    total_doc = len(judged_list)

    while doc_count < total_doc: 
        if rel_count >= task_length:
            break    
        if not doc_count == 0 and doc_count%page_size == 0:
            action_list.append('pagination')
        action_list.append(('examine', 'dummy'))
        rel_count += judged_list[doc_count]
        doc_count += 1
    return action_list


"""
params: 'page_size', 'gain_type', 'ndcg_k', 'e_model', 
    'task_length', 'f_model', 'f_prior',
    'e_lambda', 'smooth'
"""
def simulate(run, judged_list, param):
    action_lists = []
    for q in run:
        qid = q[0]
        #print qid
        # doc tuple (docno, rank, score)
        docs = q[1]
        if not qid in judged_list:
            continue
        judge = judged_list[qid]
        # check gain type (binary or graded)
        if param[1] == 'binary':
            judge = [int(j>0) for j in judge] 

        # basic params are different
        if P.interface == 'basic':
            task_length = param[3]
            if task_length == -1:
                task_length = sum(judge)
            page_size = param[0]
            actionlist = simulate_basic(judge, page_size, task_length)
            action_lists.append((qid, actionlist))
        else:

            task_length = param[4]
            if task_length == -1:
                task_length = sum(judge)
            # Get sublist and their binary/graded NDCG scores
            # First entry is the original list
            sublists, B, G = create_sublists(docs, judge)
            #print B
            #print G
            # ExamineModel
            e = ExamineModel.ExamineModel(param[3], e_lambda=param[7])
            # FilterModel     
            p = None
            if not param[6] == None:
                # get smooth value
                smooth = param[8]
                # we only use binary_NDCG
                #print smooth
                prior = [b[param[2]] for b in B]
                #print prior
                prior = [x+smooth for x in prior]
                #print prior
                p = param[6](prior) 
            f = FilterModel.FilterModel(sublists, p, model_type=param[5])
            inter = Interaction.Interaction(e, f, task_length=task_length)    
            inter.run()
            action_lists.append((qid, inter.action_list))
    return action_lists


# Load categories        
categories = load_categories(categoryfile)



# I don't remember why we provide an extra qrels option. It seems to be
# for alternaltive qrels, but I don't remember why. 
# Possbilities are: duplicates, binary/graded
# The run we used is a run after duplicate removal, so duplicates don't apply
# The binary/graded options are processed during simulation.
# so I don't know what this option is for.
if __name__ == '__main__':
    if len(sys.argv)<3:
        print 'usage: python simulate.py outputdir runs(number of simulations) qrels'
        sys.exit()
    outputdir = sys.argv[1]
    N = int(sys.argv[2])
    if len(sys.argv)==4:
        qrelsfile = sys.argv[3]

    output_param_file = '%s/%s'%(outputdir, 'param.txt')

    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    
    run = trec_util.load_TREC_run(runfile)        
    qrels = trec_util.load_qrels(qrelsfile)
    judged_list = trec_util.judged_ranklist(run, qrels)
    params, paramnames = generate_parameters()
    # Write the parameters
    outp = open(output_param_file, 'w')
    # write the header
    outp.write('%s\n'%' '.join(paramnames))            
    # write the content
    for p in params:
        pid = p[0]
        line = ['%s'%x for x in p[1]]
        if not (P.interface == 'basic') and not (line[6] == 'None'):
            line[6] = 'NDCG'
        #print line
        outp.write('%s %s\n'%(pid, ' '.join(line)))
    outp.close()
    for p in params:
        pid = p[0]
        param = p[1]
        print pid, param
        outfile = '%s/%s.txt'%(outputdir, pid)
        out = open(outfile, 'w')
        # Write header
        qids = [q for q in qrels]
        qids.sort()
        out.write(' '.join(qids)+'\n')
        # Simulation
        for n in range(N):
            action_lists = simulate(run, judged_list, param)
            action_lists.sort(key=operator.itemgetter(0))
            scores = []
            for action_list in action_lists:
                qid = action_list[0]
                actions = action_list[1]
                a = [aa[0] for aa in actions]
                # we use default effort setting
                ef = EffortModel.EffortModel()
                score = ef.compute_effort(a)    
                #print a, score
                scores.append(score)
            line = ' '.join(['%s'%s for s in scores])
            out.write(line+'\n')
        out.close()        

