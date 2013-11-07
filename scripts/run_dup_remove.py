import sys

def load_duplicate(inputfile): 
	dupId = 0
	dup = {}
	f = open(inputfile)
	for c in f:
		dupId += 1
		strs = c.strip().split('\t')
		for s in strs[1:]:
			dup[s] = dupId 
	f.close()
	return dup

def remove_dup(runfile, dup):
	f = open(runfile)
	dup_rec = set([]) 
	current_qid = ''
	rank = 0
	for c in f:
		strs = c.strip().split(' ')
		docno = strs[2]
		qid = strs[0]
		if not current_qid == qid:
			dup_rec = set([])
			current_qid = qid
			rank = 0
		# Check if there is a doc among the dup ranked higher than this one
		dupID = dup.get(docno, -1)
		if dupID < 0:
			rank += 1
			print '%s Q0 %s %s %s %s'%(qid, docno, rank, strs[4], strs[5])
		elif not dupID in dup_rec:
			rank += 1
			print '%s Q0 %s %s %s %s'%(qid, docno, rank, strs[4], strs[5])
			dup_rec.add(dupID)

	f.close()


if len(sys.argv)<2:
	print "usage: python run_dup_remove.py dupfile runfile"
	sys.exit()


dupfile = sys.argv[1]
runfile = sys.argv[2]

dup = load_duplicate(dupfile)
remove_dup(runfile, dup)
