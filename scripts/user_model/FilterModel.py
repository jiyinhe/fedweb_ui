"""
Modeling how users choose a sublist

Models:
- static: choose a sublist based on certain prior probability
- dynamic: users update their expectation for a sublist
To realize dynamic model, call update_prior externally after choose_list

priors:
- uniform
- weighted

"""
import sys
from numpy import random, argmax
import operator 
import itertools

class FilterModel:
	# resultlist contains an array of arrays:
	# - each subarray is a sub ranked list
	# - each item contains the (doc_id, rank, relevance_judge) 
	# prior: the priors, if None, then uniform
	def __init__(self, resultlist, prior=None):
		self.resultlist = resultlist
		# keep history of the rel/non-rel docs encontered before	
		self.history = [[0, 0] for i in range(len(resultlist))]

		if prior == None:
			# Keep track of how many times a list has been selected 
			self.prior = [[1, 0, i] for i in range(len(resultlist))]
		else:
			self.prior = [[prior[i], 0, i] for i in range(len(prior))]
			if not len(prior) == len(resultlist):
				print 'ERROR: prior should have the same length as resultlist'
				sys.exit()
		
	def select_list(self):
		idx = self.sample_list()			
		return idx	
	
	""" choose based on prior """
	def sample_list(self):
		print self.prior
		# fist check if some of the list has been exhausted
		prior = []
		for p in self.prior:
			if not p[1] >= len(self.resultlist[p[2]])-1:
				prior.append((p[0], p[2]))
		if prior == []:
			return -1
		# hyperparameter
		alpha = [p[0] for p in prior]
		# We need to draw sample from a categorical distribution  
		# Using Dirichlet as prior, we have p|a = (p_1, ..., p_k)~Dir(k, alpha)
		# P is the parameter of the categorical distribution
		P = random.dirichlet([p[0] for p in prior], 1)[0]	
		# The we can draw X|P = (x_1, ..., x_n)~Cat(k, P) 
		# In fact here we only need to draw one x at a time
		# Use the numpy.multinomial function to generate a random value
		# It seems to be equivelent 
		idx = list(random.multinomial(1, P, size=1)[0]).index(1)	
		
		# add this idx to the list
		self.prior[idx][1] += 1	  
		return idx 
	
	""" update the prior"""
	# record: a tuple (listid, rank, relevance)
	def update_prior(self, record):
		print self.prior
		listid = record[0]
		rel = record[2]
		
		# Update the prior based on the seen relevant docs
		# Dir(c+alpha) where c is the new observation
		if rel > 0:
			self.prior[listid][0] += 1			
		print self.prior

if __name__ == "__main__":
	resultlist = [[(1, 0, 0),(2, 1, 1),(3, 2, 0)],
			[(1, 0, 1),(2, 1, 0),(3, 2, 1)],
			[(1, 0, 0),(2, 1, 1),(3, 2, 1)],	
			]
	a = [0.5, 0.3, 0.2]
	fm = FilterModel(resultlist, prior=a)
	#print a
	s = []
	j = 0
	for i in range(10):
		if j > 2:
			j = 0
		record = [j, 2, resultlist[j][2][2]]
		j += 1
		print record
		fm.update_prior(record)
		s.append(fm.select_list())
	s.sort()
	for k, g in itertools.groupby(s):
		print k, len(list(g))

	
