"""
Some supporting functions
"""
import itertools
import operator 

class Utils:
	def __init__(self):
		self.m = 1000000000 
		self.step = 0
		self.route = []
	def partial_sum(self, C, target, partial):
		self.step += 1
		s = sum([p[0] for p in partial])
		c = sum([p[2] for p in partial])
		#print 
		#print 'start---------------------------------'
		#print 'level', t 
		#print 'current C', C
		#print 'current partial', partial, 'sum:', s, 'cost:', c 
		# check for partial sum
		if s == target:
			#print 'found:', s, 'cost:', c, partial
			if c < self.m:
				self.m = c
				self.route = partial
				# We can't get less cost then the targetd gain	
				if self.m == target:
					return 
		if s >= target:
			#print 'exceed'
			return -1  
		# If with a length less than target, the cost
		# is already > current minimum, we can also stop
		# adding new items: this doesn't work, it somehow breaks 
		# the loop of the summing up 
		#elif s < target and c >= self.m:
			#print 'exceed min'
		#	return -1
 
		for i in range(len(C)):
			n = C[i]
			remain = C[i+1:]
			# If the new item is in the same sublist as some other items
			# in the partial list, then it should not be added, any subsequent
			# partial list will be invalid
			if n[1] in [p[1] for p in partial]:
				continue
			exceed = self.partial_sum(remain, target, partial+[n])	
				
			# We can break becuase:
			# the levels are sorted first by level, and within level by 
			# cost. If now it's exceeding, replacing 
			# current item with any items in the remaining will:
			# - sum to a larger count
			# - sum to the same count, but with larger cost
			if exceed == -1:
				break
		return 0 
	# Find the subset of a set of numbers that sum up to a number
	# C contains [(j, i, cost)...]
	# sum of cost should be minimized
	# j is the number that should sum up to target
	# i is a constraint: at a time, only one item with the same i can be in the list 
	def subset_sum_min(self, C, target):
		res = []
		C.sort(key=operator.itemgetter(0, 2))
		self.partial_sum(C, target, [])	
		#print self.m, 'steps:', self.step
		#print self.route
		return self.m, self.route, self.step


if __name__ == '__main__':
	C = [
		(1, 0, 3), (1, 1, 2), (1, 2, 5), (1, 3, 2),
		(2, 0, 5), (2, 1, 5), (2, 2, 7), (2, 3, 4),
		(3, 0, 6), (3, 1, 8), (3, 2, 8), (3, 3, 7),
		(4, 0, 8)
	]
	u = Utils()
	C.sort(key=operator.itemgetter(0, 2))
	u.subset_sum_min(C, 5)
	"""
	C = [(3, 0, 1), (4, 0, 2), (5, 0, 3), (7, 0, 3), (8, 0, 4), (9, 0, 4), (10, 0, 5)]

	u = Utils()
	u.subset_sum_min(C, 15) 
	"""	

