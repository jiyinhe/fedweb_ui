"""
Configuration to perform analysis
"""

# parameter effect analysis based on effort
class paramEffectEffort {
	simulation_dir = '../../data/simulation/'
	outputdir = 'plots/param_effect_effort/'
}

# parameter effect analysis based on gain
class paramEffectGain {
	simulation_dir = '../../data/gain_experiments_jan2015/simulation'
	outputdir = 'plots/param_effect_gain/'
}

# per query analysis based on effort
class perQueryEffort {
	simulation_dir = '../../data/simulation'
	simulation_basic_dir = '../../data/simulation_basic'
	outputdir = 'plots/per_query_effort/'
}


# per query analysis based on gain
class perQueryGain {
	simulation_dir = '../../data/gain_experiments_jan2015/simulation'
	simulation_basic_dir = '../../data/gain_experiments_jan2015/simulation_basic'
	outputdir = 'plots/per_query_gain/'
} 


