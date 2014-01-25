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
	def __init__(self, resultlist, prior=None, model_type='static'):
		self.resultlist = resultlist
		self.model_type = model_type
		# keep history of the rel/non-rel docs encontered before	
		#self.history = [[0, 0] for i in range(len(resultlist))]

		if prior == None:
			# [0]: prior probability
			# [2]: list index
			a = float(1)/float(len(resultlist))
			self.prior = [[a, i] for i in range(len(resultlist))]
			self.alpha0 = [[a, i] for i in range(len(resultlist))]
		else:
			#print prior
			sum_a = float(sum(prior))
			self.prior = [[float(prior[i])/sum_a, i] for i in range(len(prior))]
			self.alpha0 = [[float(prior[i])/sum_a, i] for i in range(len(prior))] 
			#print self.prior 
			if not len(prior) == len(resultlist):
				print 'ERROR: prior should have the same length as resultlist'
				sys.exit()

	# last_visit: an array of len(resultlist)
	# storing the last rank visited in a sublist
	# Use this to peek next doc, check if it's seen before in other lists
	def select_list(self, last_visit):
		idx = self.sample_list(last_visit)			
		return idx	
	
	""" choose based on prior """
	def sample_list(self, last_visit):
		#print self.prior
		# fist check if some of the list has been exhausted
		#print 'last', last_visit
		#print [len(r) for r in self.resultlist]
		prior = []
		for p in self.prior:
			rank = last_visit[p[1]]
			#print  rank, len(self.resultlist[p[1]])
			# If a sublist is at the end, do not select it
			if not rank >= len(self.resultlist[p[1]])-1:
			#if not p[1] >= len(self.resultlist[p[2]])-1:
				prior.append((p[0], p[1]))
			#else:
				#print 'rank', rank, len(self.resultlist[p[1]])
			#	print p
		if prior == []:
			return -1
		
		# hyperparameter
		alpha = [p[0] for p in prior]
		if sum(alpha) == 0:
			alpha = [float(1)/float(len(prior)) for p in prior]
		# Otherwise renormalize it to sum up to 1, to avoide NaN
		alpha = [a/sum(alpha) for a in alpha]
	
		# We need to draw sample from a categorical distribution  
		# Using Dirichlet as prior, we have p|a = (p_1, ..., p_k)~Dir(k, alpha)
		# P is the parameter of the categorical distribution
		P = random.dirichlet(alpha, 1)[0]	
		# The we can draw X|P = (x_1, ..., x_n)~Cat(k, P) 
		# In fact here we only need to draw one x at a time
		# Use the numpy.multinomial function to generate a random value
		# It seems to be equivelent 
		#print alpha
		#print P
		#print 
		idx = list(random.multinomial(1, P, size=1)[0]).index(1)	
		listid = prior[idx][1]
		#print 'select', idx, listid	
		#if self.model_type == 'dynamic':
		#	print
		#	print prior
		#	print listid
		return listid 
	
	""" update the prior"""
	# record: current_visit: (listid, rank) 
	def update_prior(self, record):
		#print self.prior
		listid = record[0]
		rank = record[1]
		#print listid, rank
		res = self.resultlist[listid][0:rank + 1]			
	
		# Update the prior based on the seen relevant docs
		# let alpha = (alpha_0 + #rel)/(alpha_0+#seen)
		num_seen = len(res)
		num_rel = sum([int(r[2]>0) for r in res])
		#print num_seen, num_rel, self.alpha0
		#print num_seen, num_rel, (self.alpha0 + num_rel)/(self.alpha0 + num_seen)	
		#print 'update:', num_seen, num_rel, listid, self.prior[listid][0], self.alpha0[listid]
		self.prior[listid][0] = float(self.alpha0[listid][0] + num_rel)/float(self.alpha0[listid][0] + num_seen)			
		#print 'new prior:', self.prior[listid][0]



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
		#print record
		fm.update_prior(record)
		s.append(fm.select_list())
	s.sort()
	for k, g in itertools.groupby(s):
		print k, len(list(g))

	
