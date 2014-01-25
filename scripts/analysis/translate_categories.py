import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fw_userstudy.settings")
import sys
sys.path.append(os.path.abspath('../../fw_userstudy/'))
import fedtask.models
from fedtask.views import process_category_info

topics = ['7040', '7042', '7046', '7047', '7084', '7056', '7129', '7067', '7068', '7069', '7075',
'7076', '7080', '7209', '7132', '7087', '7089', '7090', '7407', '7348', '7094', '7096',
'7097', '7099', '7465', '7103', '7109', '7115', '7504', '7505', '7506', '7124', '7127',
'7001', '7258', '7003', '7004', '7007', '7009', '7145', '7018', '7404', '7406', '7485',
'7025', '7030', '7415', '7033', '7034', '7039']
topics.sort()

print len(topics)


namesd={}
for t_id in topics:
	docs = fedtask.models.Ranklist.objects.get_ranklist(t_id, '3', '0')
	categories = process_category_info(docs)
	catnames = []
	for c in categories:
		catnames.append(c['name'])
	namesd[t_id] = catnames

catdist = {}
fh = open('data/facet_catdist.data','r')
text = fh.read()
fh.close()
lines = text.split("\n")

new_catd = {}
for l in lines:
	if not l: continue
	t_id, catd = l.split('\t')
	catd = eval(catd)		
	catnames = namesd[t_id]
	new_catd[t_id]={}
	for (c,val) in catd.items():
		cindex = c.replace("category_","")
		if cindex == 'all':
			cindex = 0	
		else:
			cindex = int(cindex)+1
		new_catd[t_id][catnames[cindex]]=val
translated_cats = new_catd.items()
translated_cats.sort()
fh = open('data/facet_translated_catdist.data','w')
for (k,v) in translated_cats:
	 fh.write("%s	%s\n"%(k, str(v)))
fh.close()
