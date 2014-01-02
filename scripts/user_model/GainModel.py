"""
The user gains in terms of the relevant documents they found

models:
- binary: 0/1 
- graded: graded relevance judgement

"""

class GainModel:

	def __init__(self, model_type='binary'):
		self.model_type = model_type


	# The judged list should contain relevance judgements in the order of  
	# the list of documents users have encoutered during search
	def compute_gain(self, judged_list):
 		if self.model_type == 'binary':
			return self.binary_model(judged_list)
		elif self.model_type == 'graded':
			return self.graded_model(judged_list)



	def binary_model(self, judged_list):
		judge = [int(j>0) for j in judged_list]
		return sum(judge)	 

	def graded_model(self, judged_list):
		return sum(judged_list)




if __name__ == '__main__':
	a = [2, 0, 1, 4, 0, 0, 3]
	b = GainModel('binary')
	c = GainModel('graded')
	print a
	print 'binary', b.compute_gain(a)	
	print 'graded', c.compute_gain(a)
