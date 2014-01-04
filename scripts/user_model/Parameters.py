"""
Set the parameters for simulation
"""

# ===== Parameters for ExamineModel =====
e_model_type = ['ExpRank']
e_lambda = [5, 1, 0.5, 0.25, 0.05, 0.01] 

# ===== Parameters for FilterModel ======
uniform = lambda x: [1 for i in range(len(x))]
ndcg = lambda x: x
f_prior = [None, ndcg]
f_model_type = ['static', 'dynamic']

# ndcg@k as prior, -1 for all
ndcg_k = [-1]

# ===== Parameters for GainModel =====
gain_model_type = ['binary']

# ===== Parameters for EffortModel =====

# ===== System parameters =====
page_size = [10]

# ===== Task parameters =====
# Number of relevant documents to be found: -1: all
task_length = [1, 10, -1] 






