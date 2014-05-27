"""
Load data according to parameter settings
"""
def load_parameter_record(inputfile):
    f = open(inputfile)
    lines = f.readlines()
    pa = []
    for l in lines[1:]:
        pa.append(l.strip().split(' '))
    f.close()
    return pa

def load_data(inputdir, pa):
    all_data = []
    for p in pa:
        idx = p[0]
        f = open('%s/%s.txt'%(inputdir, idx))
        lines = f.readlines()
        qids = lines[0].strip().split(' ')
        results = [l.strip().split(' ') for l in lines[1:]]	
        i = 0
        D = []
	for q in qids:
	    data = [int(r[i]) for r in results]
            D.append((q, data))
            i += 1
	f.close()		
        all_data.append((p[0], dict(D)))
    return dict(all_data)

if __name__ == '__main__':
    inputdir = '../../data/simulation'
    pafile = '%s/param.txt'%(inputdir)
    pa = load_parameter_record(pafile) 
    all_data = load_data(inputdir, pa)
