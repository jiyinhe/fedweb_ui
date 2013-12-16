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

class BrowseBasic:
	# The ranklist contains an array of the relevance judgements of documents
	# e.g., with binary judgement: [1, 0, 0, 1] 
	ranklist = []
	costlist = []
	gainlist = []
	def __init__(self, sublists):
		self.ranklist = rankedlist
		self.initialize_cost_gain()
		self.initialize_gain()	

	# Computing the cost and gain to reach every relevant document
	def initialize_cost_gain(self):
		rel = [(i+1, self.ranklist[i]) for i in self.ranklist]
		X = itertools.filter(lambda x: x[1]>0, rel)
		print list(X)

class BrowseCategory:
	# The sublists contains an array of arrays of relevance judgement of documents
	# e.g., [[1, 0, 0, 1], [1, 1, 0], ...]
	sublists = []
	def __init__(self, sublists):
		self.sublists = sublists 

	
