"""
Get following stats:
 - # rel per query
 - # category covered per query

"""
catefile = '../data/resources-FW13-categorization.tsv'

def load_engine_category(inputfile):
	sites = []
	f = open(inputfile)
	for c in f:
		strs = c.strip().split('\t')
		site_id = strs[0]
		cate = strs[3]
		sites.append((site_id, cate))
	f.close()
	return sites


def load_duplicate(inputfile): 
	f = open(inputfile)
	for c in f:
		c.strip().split('\t')
		
	f.close()

load_engine_category(catefile)
