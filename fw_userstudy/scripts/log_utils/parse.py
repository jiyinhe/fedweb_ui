import sys
import json


class LogData:

	def __init__(self):
		self.rawdata = ""
		self.clicks = ""
		self.hovers = ""
		self.actions = "" 


	def load_data(self,fname):
		fh = open(fname)
		self.rawdata = json.load(fh)
		fh.close()
	
hits= tmp2.data['hits']['hits']

time_hit_pairs = [(h['_source']['created_at'],h) for h in hits]
time_hit_pairs.sort()
for h in time_hit_pairs:
	try:
		data = h[1]['_source']
		event = data['event_type']
		if 'event_properties' in data:
			properties = data['event_properties']
			if 'node_data_attrs' in properties:
				print h[0],event,properties['node_data_attrs']
			elif event=='mouse_movements':
				for p in properties:
					print h[0],event,p['node_data_attrs']
			else:
				print h[0],event
		else:
			print h[0],event
#[1]['_source']['created_at'], h#['user_id'],h[1]['_source']['event_properties']
	except:
		print "************************** missing **********************"
		print


