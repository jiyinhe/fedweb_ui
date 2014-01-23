"""
Format data for R analysis of relative importance
of variables in a multiple regression setup
"""
import SimuData as simd
import itertools
import numpy as np

dataroot = '/export/data2/fedweb_userstudy/'
#dirlist = ['simulation-official-category', 'simulation-official-category-1', 'simulation-official-category-2', 'simulation-official-category-3']
dirlist = ['simulation-official-category']
#params = ['e_lambda', 'f_prior', 'f_model', 'task_length']

outpudir = 'data/'
params = {
	'e_lambda': [0.1],
	'f_prior': ['None', 'NDCG'],
	'f_model': ['static', 'dynamic'],
	'task_length': [1, 10, -1]
}

s = simd.SimuData(dataroot, dirlist, params.keys())

def data_all():
	header = ['e_lambda', 'f_prior', 'f_model', 'qid', 'effort']
	for task_length in [1, 10, -1]:
		f = open('%s/task_length_%s.txt'%(outpudir, task_length), 'w')
		f.write(' '.join(header)+'\n')
		E = ['e_lambda=%s'%e for e in [1,  0.1,  0.01,  0.001]]
		FP = ['f_prior=%s'%fp for fp in ['None', 'NDCG']]
		FM = ['f_model=%s'%fm for fm in ['static', 'dynamic']]
		T = ['task_length=%s'%task_length]
		P = itertools.product(T, E, FP, FM)
		for p in P:
			print p
			data, qids = s.get_data(p)
			qids = [qids for i in range(len(data))]	
			qrys = [q for sublist in qids for q in sublist]
			data = [d for sublist in data for d in sublist]
			e = [p[1].split('=')[1] for i in range(len(data))]
			fp = [p[2].split('=')[1] for i in range(len(data))]
			fm = [p[3].split('=')[1] for i in range(len(data))]
			D = [' '.join([e[i], fp[i], fm[i], str(qrys[i]), str(data[i])]) for i in range(len(data))]

			f.write('\n'.join(D)+'\n')
		f.close()	


	
if __name__ == '__main__':
	data_all()		





