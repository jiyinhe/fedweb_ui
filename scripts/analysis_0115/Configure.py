"""
Configuration to perform analysis
"""

# parameter effect analysis based on effort
class paramEffectEffort(object):
	simulation_dir = '../../data/simulation/'
	output_dir = 'plots/param_effect'


# parameter effect analysis based on gain
class paramEffectGain(object): 
	simulation_dir = '../../data/gain_experiments_jan2015/simulation'
	output_dir = 'plots/param_effect/'

# per query analysis based on effort
class perQueryEffort(object): 
	simulation_dir = '../../data/simulation'
	simulation_basic_dir = '../../data/simulation_basic'
	output_dir = 'plots/per_query_effort/'


# per query analysis based on gain
class perQueryGain(object): 
	simulation_dir = '../../data/gain_experiments_jan2015/simulation'
	simulation_basic_dir = '../../data/gain_experiments_jan2015/simulation_basic'
	output_dir = 'plots/per_query_gain/'
 


