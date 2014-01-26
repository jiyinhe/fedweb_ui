import sys
import ijson,json

MAXCLICKS = 50
DEBUG = 1

class LogData:

	def __init__(self):
		self.stream	= ""
		self.clicks = []
		self.hovers = ""
		self.actions = "" 

	def get_logobjects(self):
		# unpack json returned by elastic search
		# hits is a list of log objects
		return self.stream

	def load_data(self,fname):
		fh = open(fname)
		self.stream = ijson.items(fh,'hits.hits.item')
		return self.stream
	
# Go through all logobjects and pass each object to an appropriate
# handler to extract object dependend information. 
# Object level information
#	 state
#	 received_at, date recieved by index
#	 created_at, date created at client
#	 event_properties: need dedicated handlers 
#	 event_type
#          "event_type": "mouse_click",
#          "event_type": "mouse_movements",
#          "event_type": "bookmark",
#          "event_type": "bookmark_try", (ignore)
#          "event_type": "browser_close", (ignore)
#          "event_type": "category_filter",
#          "event_type": "completed_task",
#          "event_type": "gave_up_task",
#          "event_type": "login", (ignore)
#          "event_type": "logout", (ignore)
#          "event_type": "paginate",
# Update the information for each user,query combination.
# Grouping key: (user_id, query_id)
# 	user_id: the username part of the key by which we group
# 	topic_id: the query the other part of the key by which we group
# General information extracted (for each object)
# 	time: create a time ordered list of events.
# 	location: events possibly happen at different locations (pages)
# Specific information
# 	results_list:	ids of the documents shown to the user (not for
#				  	mouse_click/ mouse_movements
#	relevance:	only for bookmark
#	category:	only for category_filter 
#	currentpage:	only for paginate

	def group_logevents_by_user_and_query(self):
		user_query_rows = {}
		i = 0
		for o in self.get_logobjects():
			if i%1000 == 0: print i
			i+=1
			# obtain general information
			data = o['_source']
			timestamp = data['created_at']
			event_type = data['event_type']
			state = data['state']
			loc,user_id,topic_id,reslist = self.handle_state(state)
			if user_id < 27 or user_id == 37 or user_id == 45: continue

			# obtain event specific properties and add to event
			event_props = data['event_properties']
			event = [timestamp,loc,event_type,reslist]
			# add list of mouse clicks as (location, group_id) tuples
			if event_type == "mouse_click":
				event.append(self.handle_mouse_click(event_props))
			# add number of mouse hovers 
			elif event_type == "mouse_movements":
				event.append(self.handle_mouse_movements(event_props))
			# add bookmark relevant/non-relevant value, i.e., {1,-1}
			elif event_type == "bookmark":
				event.append(self.handle_bookmark(event_props))
			# add category name, i.e., {category_0, category_1,...}
			elif event_type == "category_filter":
				event.append(self.handle_category_filter(event_props))
			# add completed_task as 1
			elif event_type == "completed_task":
				#self.handle_completed_task(event_props)
				event.append(1)
			# add gave up as 1
			elif event_type == "gave_up_task":
				#self.handle_gave_up_task(event_props)
				event.append(1)
			# add paginate, as current page
			elif event_type == "paginate":
				#self.handle_paginate(event_props))
				event.append('current_page')
			else:
				# ignore login,logout,bookmark_try, browser_close
				continue
			key = (user_id,topic_id)		
			value = event
			if key in user_query_rows:
				user_query_rows[key].append(value)
			else:
				user_query_rows[key] = [value]	
		return user_query_rows

# state consists of:
#			screen_resolution 	(ignore)
#			user_id				(multikey)
#			results_list		
#			language			(ignore)
#			run_id				(ignore)
#			viewport_dimensions	(ignore)
#			visitor_key			(ignore)
#			topic_id			(multikey)
#			user_agent_string	(ignore)
#			browser_version		(ignore)
#			current_category	(ignore)
#			platform			(ignore)
#			browser_dimensions	(ignore)
#			session_id			(ignore)
#			current_location	
#			query				(ignore)
#			ip_address			(ignore)
#			browser				(ignore)
# return location, user_id, topic_id, results_list
	def handle_state(self,data):
		# some values are possibly missing
#		user_id=""
#		if 'user_id' in data: 
#			user_id = data['user_id']
# use session_id instead as we can derive the ui from that
		session_id=""
		if 'session_id' in data: 
			session_id = data['session_id']
		results_list = []
		if 'results_list' in data: 
			results_list = data['results_list']
		topic_id = ""
		if 'topic_id' in data: 
			topic_id = data['topic_id']
		location = ""
		if 'current_location' in data: 
			location = data['current_location']
		return location,session_id,topic_id,results_list

# object consisting of multiple (buffered)  mouse movements
# return number of movements
#'event_properties': [	{'timestamp': '2014-01-17T09:11:23.855+01:00', 
#						'mouse_position': 
#							{'y': 464, 'x': 648}, 
#						'viewport_dimensions': 
#							{'width': 1423, 'height': 729}},
#						{'timestamp': '2014-01-17T09:11:23.905+01:00', 
#						'mouse_position': 
#							{'y': 464, 'x': 647}, 
#						'viewport_dimensions': 
#							{'width': 1423, 'height': 729}},
#					],
	def handle_mouse_movements(self,data):
		return len(data)

# object consisting of multiple (buffered)  mouse clicks
# return list of (location,group_id) tuples
# a mouse clicks  event_properties looks like this
#			node_name
#			mouse_position
#			node_classes
#			node_id
#			node_data_attrs
	def handle_mouse_click(self,data):
		click = []
		if 'node_data_attrs' in data:
			node_data_attrs = data['node_data_attrs']
			if 'rankgroupid' in node_data_attrs:
				click.append(node_data_attrs['rankgroupid'])
		return click

# a bookmark's eventproperties looks like this:
#'event_properties': 
#	{'node_id':'FW13-e055-7090-04_bookmark', 
#	'response': {'count': 1, 
#				'userscore': 
#					{'clicks_perc': 98, 
#					'rel_perc': 10, 
#					'relnum': 1, 
#					'clicksleft': 49,
#					'rel_to_reach': 9}, 
#				'done': False, 
#				'feedback': 1}, 
#	'query_time_ms': 59},
# return the following information:	numrel,clickcount,feedback,done
# Clickcount: derived from clicksleft, as it is more convenient for
# calculating effort. 
# Numrel: the number of relevant documents # found.
# Done: whether the user is done with task (found 10 relevant docs)
# Feedback: whether the clicked doc is relevant
	def handle_bookmark(self,data):
		response = data['response']
		userscore = response['userscore']
		feedback = response['feedback']
		done = response['done']
		numrel = userscore['relnum']
		clicksleft = userscore['clicksleft']
		clickcount = MAXCLICKS - clicksleft
		return numrel,clickcount,feedback,done
		
# a category_filter's event properties looks like this:
#'event_properties': 
#	{'node_id': 'category_5'}, 
# return the following information:
#	category
	def handle_category_filter(self,data):
		return data['node_id']

# define some filters that massage the data to get:
#	 per user, per query: time spent, clicks, relevant, irrelevant,
#	 category, giveup, paginate, search depth
# 		 for successful queries
#		 for failed queries
#		 for give up queries
	def filter(self,data,filters):
		# for each user-query pair in our data, get the list of events
		# and filter the list based on filters
		d = {}
		for key,values in data.items():
			for (f,v) in filters.items():
				if f == 'location': # restrict to given location
					values = self.filter_location(values,v)
				elif f == 'click': # remove clicks
					values = self.filter_click(values,v)
				elif f == 'movement': # remove movements
					values = self.filter_movement(values,v)
				elif f == 'order': # reorder values
					values = self.filter_order(values,v)
				else:
					if DEBUG: print "error unknown filter", f
					continue
			d[key] = values
		return d

# an event looks like this:
#	event = [timestamp,loc,event_type,reslist]

	# return all events that are on page
	def filter_location(self,data,page):
		return  [d for d in data if page == d[1]]

	# return only clicks, or everything but clicks depending on flag
	def filter_click(self,data,flag):
		if flag: #filter (remove) clicks
			return [d for d in data if 'mouse_click' != d[2]]
		else: # filter (remove) everything else
			return [d for d in data if 'mouse_click' == d[2]]

	# return only movements, or everything but movements depending on flag
	def filter_movement(self,data,flag):
		if flag: #filter (remove) movement
			return [d for d in data if 'mouse_movements' != d[2]]
		else: # filter (remove) everything else
			return [d for d in data if 'mouse_movements' == d[2]]

	# order by index
	def filter_order(self,data,index):
		return sorted(data,key=lambda x: x[index])	

	def cache2file(self,fname,data):
		fh = open(fname,'w')
		fh.write(str(data))
		fh.close()

def main():		
	inputfile = "alldata_26-01-2014_11:00.log"
	#inputfile = "alldata_24-01-2014_13:13.log"
	#inputfile = "clicks_24-01-2014_13:00.log"
	ld = LogData()
	ld.load_data(inputfile)
	data = ld.group_logevents_by_user_and_query()

	# filter the data
	page = 'http://zookst9.science.uva.nl:8002/study/task/'
	data = ld.filter(data, {'location':page,
							'click':1,
							'movement':1,
							'order':0})
	for (k,v) in data.items():
		print k
		print v
		print 

if __name__ == "__main__":
	#import cProfile
	#cProfile.run('main()')
	main()
