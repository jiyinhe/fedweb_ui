"""
Simulate user gain using distributions
generated from user experiment data

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
search_depth_prob_file = 'analysis/data/facet_searchdepth_prob.data'
category_prob_file = 'analysis/data/facet_translated_catdist.data'

def generate_parameters():
	# I simply add moves as parameter, but left task_length as a dummy parameter
	# as I want to keep the order so that we don't need to change a lot in other parts of the script
	params = ['index', 'page_size', 'gain_type', 'ndcg_k','e_model',
		'task_length', 'f_model', 'f_prior', 'moves'
		]

	# Change from simulation_user.py, here we will change user moves
	#p = [[10, 'binary', '-1', 'User', 10, 'static', P.f_prior[2], P.moves]]	
	p = itertools.product([10], ['binary'], [-1], ['User'], [10], ['static'], P.f_prior, P.moves)
	p = list(p)

	pa = [[i, list(p[i])] for i in range(len(p))]
	return pa, params
 
def load_categories(catefile):
	f = open(catefile)
	content = [d.strip().split('\t') for d in f.readlines()]
	f.close()
	# category tuple: (site_id, category)	
	categories = [(d[0], d[3].strip().split(',')) for d in content]
	return dict(categories)	

def load_search_depth_prob():
	f = open(search_depth_prob_file)
	prob = []
	for c in f:
		depth, p = c.strip().split('\t')
		prob.append((int(depth), float(p)))
	f.close()	
	prob.sort(key=operator.itemgetter(0))
	if prob[0][0]>0:
		prob.extend([(i, prob[0][1]) for i in range(prob[0][0])])
	prob.sort(key=operator.itemgetter(0))
	return dict(prob)

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
def create_sublists(docs, judge, category_pref):
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

"""
simulate interaction with basic interface  
"""	
def simulate_basic(judged_list, page_size, moves):
	action_list = []
	rel_count = 0
	doc_count = 0
	total_doc = len(judged_list)

	while doc_count < total_doc: 
		if moves > 0 and len(action_list)>=moves:
			break	
		if not doc_count == 0 and doc_count%page_size == 0:
			action_list.append(('pagination', ('dummy', [0])))
			if moves > 0 and len(action_list)>=moves:
				break
		action_list.append(('examine', ('dummy', [judged_list[doc_count]])))
		rel_count += judged_list[doc_count]
		doc_count += 1
	return action_list


"""
params: 'page_size', 'gain_type', 'ndcg_k', 'e_model', 
	'task_length', 'f_model', 'f_prior',
	'e_lambda'	
"""
def simulate(run, judged_list, param, search_depth_prob, cate_pref):
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
			moves = param[7]
			page_size = param[0]
			actionlist = simulate_basic(judge, page_size, moves)
			action_lists.append((qid, actionlist))
		else:
			# task_length is now a dummy parameter
			task_length = param[4]
			if task_length == -1:
				task_length = sum(judge)
			# Get sublist and their binary/graded NDCG scores
			# First entry is the original list
			sublists, pref = create_sublists(docs, judge, cate_pref[qid])
			#print B
			#print G
			# ExamineModel
			e = ExamineModel.ExamineModel(param[3], empirical_distribution=search_depth_prob)
			# FilterModel	 
			p = None
			if not param[6] == None:
				# Use empirical user preference of cateogry 
				p = param[6](pref) 
			f = FilterModel.FilterModel(sublists, p, model_type=param[5])
			inter = Interaction.Interaction(e, f, task_length=task_length)	
			moves = param[7]
			inter.run_gain(moves)
			action_lists.append((qid, inter.action_list))
	return action_lists


# Load categories		
categories = load_categories(categoryfile)


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

	search_depth_prob = load_search_depth_prob()
	cate_pref = load_category_pref()
	
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
			line[6] = 'User'
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
			action_lists = simulate(run, judged_list, param, search_depth_prob, cate_pref)
			action_lists.sort(key=operator.itemgetter(0))
			scores = []
			for action_list in action_lists:
				qid = action_list[0]
				actions = action_list[1]
				#print len(actions)
				# Get documents that were examined.
				# Each action has a "visited doc", but we only need the examined ones 
				# to determine uesr gain 
				examined_judge = [a[1][-1][-1] for a in itertools.ifilter(lambda x: x[0] == 'examine', actions)]
				# Compute gain
				score = sum(examined_judge)
				#print a, score
				scores.append(score)
			line = ' '.join(['%s'%s for s in scores])
			out.write(line+'\n')
		out.close()		



