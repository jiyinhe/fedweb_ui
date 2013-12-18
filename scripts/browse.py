"""
Simulate how users browse a result list 
Here we consider 2 types of UI:
- a basic UI
- a UI with category filter, each catetory is a sublist of
the original ranked list

We condier the following cases:
1. base case: 
User has the complete information about the ranked lists, and they are 
able to find the amount of rel info with  minimum effort.

Assumptions:
(a) all actions (read snippet, choose category) have the same cost
(b) user always reads from top-down, when goes between categories, 
he/she will continue from where s/he left, i.e., it's always beneficial
to continue at the same sublist until the right stop point.

"""
import itertools
from utils import Utils 
import operator
class BrowseBasic:
	# The ranklist contains an array of the relevance judgements of documents
	# e.g., with binary judgement: [1, 0, 0, 1] 
	ranklist = []
	cost_gain_list = []
	def __init__(self, rankedlist):
		self.ranklist = rankedlist
		self.initialize_cost_gain()

	# Computing the cost and gain to reach every relevant document
	def initialize_cost_gain(self):
		rel = [(i+1, self.ranklist[i]) for i in range(len(self.ranklist))]
		self.cost_gain_list = list(itertools.ifilter(lambda x: x[1]>0, rel))

	# Compute best case cost for given gain
	def min_effort(self, gain):
		if len(self.cost_gain_list)<gain:
			return float('inf') 
		else:
			return self.cost_gain_list[gain][0]	
	

class BrowseCategory:
	# The sublists contains an array of arrays of relevance judgement of documents
	# e.g., [[1, 0, 0, 1], [1, 1, 0], ...]
	sublists = []
	cost_gain_list = []
	def __init__(self, sublists):
		self.sublists = sublists 
		self.initialize_cost_gain()

	def initialize_cost_gain(self):
		self.cost_gain_list = []
		for s in self.sublists:
			#cost is read snippet + choose category
			rel = [(i+1+1, s[i]) for i in range(len(s))]
			#filter relevant docs
			cost = list(itertools.ifilter(lambda x: x[1]>0, rel))
			#print cost
			self.cost_gain_list.append(cost)
		#print sum([len(x) for x in self.cost_gain_list])
	# Find the path of user that minimize the effort	
	# User will go down a list and stop at a rank
	# of a relevant doc, the total number of relevant
	# docs should sum up to gain, and the cost to reach
	# these docs should be minimized.
	# 
	# The cost list contains the rank of each of the 
	# relevant doc in a sublist (i.e., the cost)
	def min_effort(self, gain):
		#(1)Get possible length and cost of each sublist
		# [((list_id, num_rel_docs), cost)...]
		#print "prepare data"
		costs = self.cost_gain_list
		C = []
		for i in range(len(costs)):
			tmp = costs[i]
			if len(tmp)==0:
				continue
			for j in range(len(tmp)):
				# already trim off the relevant documents that are 
				# beyond the target value (gain), user will stop
				# before that
				if j+1 < gain:
					# j should sum up to gain
					C.append((j+1, i, tmp[j][0]))	
			
		#print "solve subset problem for target %s"%gain
		#(2)Find combinations of length sum to gain
		# and minimize the effort
		C = sorted(C, key=operator.itemgetter(0, 2))
		u = Utils()
		cost, route, step = u.subset_sum_min(C, gain)
		print cost, step
		print route
		for r in route:
			print self.sublists[r[1]][0:10] 

