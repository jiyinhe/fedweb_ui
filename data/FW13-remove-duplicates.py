#! /usr/bin/python

import sys
from os import path

#input
args = sys.argv
if not len(args)==4 :
    print('Usage: ./%s QRELS DUPFILE RUN\n(where the arguments denote the file locations for the files FW13-QRELS-RM.txt, duplicates.txt, and the run-file)'%(path.basename(args[0])))
    sys.exit()
elif not (args[1].endswith('FW13-QRELS-RM.txt') and args[2].endswith('duplicates.txt')):
    print('Please use original qrels and duplicates files.')
    sys.exit()

qrelsfile, dupfile, runfile = args[1],args[2],args[3] 
runfile = path.basename(runfile)
qrels_filtered = '%s-%s.txt'%(qrelsfile[:-4],runfile)


#create duplicates map
fIDdup = open(dupfile,'r')
dupmap = {}
dupID = 0
for line in fIDdup:
    dupID += 1
    parts = line.strip().split()
    for part in parts[1:]:
        dupmap[part] = dupID
fIDdup.close()

#create filtered qrels file
seendups = []
fIDqrels = open(qrelsfile,'r')
fIDqrels_filtered = open(qrels_filtered,'w')
#Note: duplicates have been detected within topics, 
#therefore keeping 'seendups' over all topics is allowed and simpler.
for line in fIDqrels:
    (qID,zero,sID,level) = line.strip().split()
    if sID in dupmap:
        dupID = dupmap[sID]  
        if dupID in seendups:
            level = '0'
        else:
            seendups.append(dupID)    
    fIDqrels_filtered.write('%s 0 %s %s\n'%(qID,sID,level))        

fIDqrels_filtered.close()
fIDqrels.close()



