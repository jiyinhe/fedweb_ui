"""
Modeling whether a user wants to examine
a document at rank r, or time t

Models:

ExpRank: exponential decay function at time t 
p(e=1|r) = N_0*e^{-lambda*r}

"""
import sys
import math
import random 

class ExamineModel:
	# Set the model parameters
	# e_lambda: the decay parameter for within at time t
	# N0: the initial value, default 1, i.e., always examine the first doc
	def __init__(self, model_name, e_lambda=None, N0=1, empirical_distribution=None):
		self.model = model_name		
		self.e_lambda = e_lambda
		self.N_0 = N0
		if model_name == 'User' and empirical_distribution==None:
			print 'For model type "User", the empirical distribution should be supplied.'
			sys.exit()
		self.user_distribution = empirical_distribution

	def decay(self, t):
		return math.exp(-t*self.e_lambda)

	def examine_next(self, t):
		if self.model == 'ExpRank':
			return self.sampleExpRank(t)	
		elif self.model == 'User':
			s = self.sample_empirical(t) 
			return s 
		else:
			print 'Sorry, model %s is not available'%self.model
			sys.exit()

	def sample_empirical(self, t):
		p = self.user_distribution.get(t, 0)
		n = random.random()
		if n < p:
			return 1
		else:
			return 0		

	# Sample a user decision: whether or not to examine a doc
	# With exponential decay  
	# t: time t, e.g., the current rank of the doc in a ranked list
	def sampleExpRank(self, t):
		# sample a bernoulli mean for given exponential decay function 	
		p = self.decay(t)	
		# sample a bernoulli trial~B(p)
		n = random.random()	
		if n < p:
			return 1 
		else:
			return 0 


if __name__ == '__main__':
	for e in [5, 2, 1, 0.5, 0.1, 0.05, 0.01]:
		em = ExamineModel('ExpRank', e)
		a = []
		for t in range(10):
			c = em.to_examine_doc(t)
			a.append(c)
		print e, a




	
