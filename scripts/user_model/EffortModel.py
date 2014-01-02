"""
Modeling user effort 

Uniform model: all actions share the same cost
Weighted model: different weights are assigned to different action types
"""
import sys

class EffortModel:

	# effort_type: uniform or weighted
	# action_types: an array of different action types
	# weights: an array of the same length as action_types, assigning weight to each action_type

	def __init__(self, effort_type='uniform', action_types=None,  weights=None):
		# Default
		if action_types == None:
			action_types = ['examine', 'pagination', 'filter']

		if effort_type == 'uniform':
			self.action_effort = dict([(e, 1) for e in action_types])
		else:
			if weights == None:
				print 'For non-uniform effort, weights should be supplied'
				sys.exit()
			elif not len(weights) == len(action_types):
				print 'Length of weights should be the same as length of action_types'
				sys.exit()
			else:
				self.action_effort = dict([(action_types[i], weights[i]) for i in range(len(weights))])


	# Compute the effort for an action list
	# actions do not exist in the action_effort will not be counted
	def compute_effort(self, action_list):
		effort = [self.action_effort.get(a, 0) for a in action_list]	
		return sum(effort)
	




if __name__ == "__main__":
	ef = EffortModel()	
	print 'default', ef.action_effort

	ef = EffortModel(action_types=['examine', 'category'])
	print 'custom action_types, uniform', ef.action_effort
	
	ef = EffortModel(effort_type='weighted', action_types=['examine', 'category'], weights=[1, 2])			
	print 'custom weights', ef.action_effort

	action_list = ['examine', 'examine', 'examine', 'category', 'examine']
	e = ef.compute_effort(action_list)
	print action_list, e
