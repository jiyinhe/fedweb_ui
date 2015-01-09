"""
Set the parameters for simulation
"""

# ===== Parameters for ExamineModel =====
e_model_type = ['ExpRank']
#e_lambda = [1, 0.1, 0.01, 0.001] 

# WE use the following e_lambdas for RQ1 (influence of user patience and accuracy)
# figure 4: Influence of user patience and their accuracy in choosing result lists.
e_lambda = [1, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001, 0.0005]

# We use 0.01 for RQ2 (comparing systems), figure 5: When does RLR interface help?
# e_lambda = [0.01]

# ===== Parameters for FilterModel ======
uniform = lambda x: [1 for i in range(len(x))]
ndcg = lambda x: x
user = lambda x: x
# Option user is used when user data is used to compute the parameters.
#f_prior = [None, ndcg, user]
f_prior = [None, ndcg]

# We decided to leave out option dynamic for all experiments.
#f_model_type = ['static', 'dynamic']
f_model_type = ['static']


# ndcg@k as prior, -1 for all
# I believe we left out other options.
ndcg_k = [-1]

# ===== Parameters for GainModel =====
gain_model_type = ['binary']

# ===== Parameters for EffortModel =====

# ===== System parameters =====
page_size = [10]

# ===== Task parameters =====
# Number of relevant documents to be found: -1: all
# task_length = [1, 10, -1] 

# For gain based experiment, this parameter does not make a difference.
task_length = [-1]

# Our user experiment was using task_length=10
#task_length = [10]

interface = 'category' 
#interface = 'basic'

# ========== Gain parameter =======
# This is a parameter specific to gain based experiments
# Set the maximum number of moves a user will make
# -1 means the user will go through all documents.
moves = [10, 20, 50]




