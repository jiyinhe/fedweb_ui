"""
Assume there are a number of sublists of document rankings (as a result of filtering)
the user does the following:

- pick a sublist
- goes down with a probability of examining a document at rank r, or do something else
- doing something else means: e.g., does filtering -> go to a different sublist   
- assuming users will always skip documents that have already encountered
- there is pagination

"""
import ExamineModel, FilterModel 

class Interaction:
	# page_size: number of documents shown in one page?
	# task_length: number of relevant documents to be found
	# start: the index of the starting doc (list_id, doc_rank)
	#
	# examineModel: instance of the ExamineModel class
	# filterModel: an instance of the FilterModel class  
	#
	def __init__(self, examineModel, filterModel, page_size=10, task_length=1, start=[0, 0]):
		self.page_size = page_size
		self.K = task_length
		self.E = examineModel
		self.F = filterModel
		self.resultlist = filterModel.resultlist 

		# Assume the first result will always be examined
		self.N0 = 1
		
		# To store the user actions
		self.action_list = []

		# To store the documents that have been examined
		self.doc_seen = []

		# Total documents
		self.doc_count = sum([len(d) for d in self.resultlist]) 

		# Number of relevant docs found
		self.rel_count = 0

		# last visted rank in each sublist
		self.last_visit = [-1 for i in self.resultlist]
		
		# the current list the user is at
		self.current_visit = start 

	# Start a simulation
	def run(self):
		# Only stop when all documents being examined, or K document has been found   
		while not len(self.doc_seen) >= self.doc_count:	
			#print 'task_length', self.K, 'found:', self.rel_count
			if self.rel_count >= self.K:
				break
			#print 'doc_seen_list', self.doc_seen
		
			# Now we are at a new doc, decide if examine another document
			if not self.examine_next():
				# If not, first do filtering
				listid = self.choose_list()
				# If no list is selected, then 
				if listid == -1:
					#print sum([s[2] for s in self.resultlist[0]])
					#print 'task_length', self.K, 'found:', self.rel_count, 
					#print 'Error: Something wrong, debug:', #self.doc_seen 
					continue
				# then set the current visit to the next doc in the list
				# Note: if a list is exhausted, it won't be selected 
				self.current_visit = [listid, self.last_visit[listid]+1]
				# After filtering, we now decide to visit this doc
				#print self.current_visit
				#print [len(r) for r in self.resultlist]
				doc = self.resultlist[self.current_visit[0]][self.current_visit[1]]
				self.action_list.append(('filter', (self.current_visit[0], self.current_visit[1], doc)))
			#	print 'filter', self.current_visit


			# Now we have to examine next doc, but first check if it's seen already, if so, skip it
			if self.doc_is_seen():			
				# set the last current_visit to last visited 
				self.last_visit[self.current_visit[0]] = self.current_visit[1]
				# move current_visit to next doc, prepare next iteration 
				self.current_visit[1] = self.current_visit[1] + 1
			#	print 'doc seen'
				continue
			

			#print self.current_visit
			# Now whether it's coming from a filter or that we've decided to 
			# examine the next doc, we will examine it		 
			#print 'examine next', self.current_visit
			# If the doc is in a next page, first add pagination
			if self.current_visit[1]>0 and self.current_visit[1]%self.page_size == 0:
				doc = self.resultlist[self.current_visit[0]][self.current_visit[1]]
				self.action_list.append(('pagination', (self.current_visit[0], self.current_visit[1], doc)))

			# Then examine doc 
			self.examine_doc()
			doc = self.resultlist[self.current_visit[0]][self.current_visit[1]]
			self.action_list.append(('examine', (self.current_visit[0], self.current_visit[1], doc)))
			# If FilterModel is dynamic, then update the model after examine
			if self.F.model_type == 'dynamic':
				self.F.update_prior(doc)

			# After examine
			# add this position to last visit
			self.last_visit[self.current_visit[0]] = self.current_visit[1]

			# move current_visit to the next doc in the current list
			self.current_visit[1] = self.current_visit[1] + 1 	

			#print self.rel_count
			#print len(self.action_list), self.rel_count, self.K

	# Choose a sublist 
	def choose_list(self):
		return self.F.select_list(self.last_visit)

	# Decide if we should examine another doc
	def examine_next(self):
		# If the current visit position is larger than the maximum docs in the list, then this doc cannot be examined
		#print self.current_visit
		if self.current_visit[1] >= len(self.resultlist[self.current_visit[0]]):
			return False
		else:
			# Get current rank
			t = self.current_visit[1]
			return self.E.examine_next(t)==1	
	
	# Actually examine the doc
	def examine_doc(self):
		# Get next doc from current_visit
		res = self.resultlist[self.current_visit[0]][self.current_visit[1]] 	
		docid = res[0]

		# add doc to seen list
		self.doc_seen.append(docid)
		# Check relevance
		self.rel_count += res[2]
		

	# Check if next doc in the list is already seen, 
	# if not, set the current_visit to that doc 
	# if yes, skip that doc, set the current_visit to a next doc
	def doc_is_seen(self):
		listid = self.current_visit[0]
		rank = self.current_visit[1]
		if rank >= len(self.resultlist[listid]):
			return False
		res = self.resultlist[listid][rank] 	
		docid = res[0]
		if docid in self.doc_seen:
			return True
		else:	
			return False




if __name__ == '__main__':
	resultlist = [[(1, 1, 0), (2, 2, 1), (3, 3, 0), (4, 4, 0), (5, 5, 1)],
			[(1, 1, 0), (3, 3, 0), (5, 5, 1)],
			[(2, 2, 1), (4, 4, 0)],
			]
	e_lambda =0.5 
	e = ExamineModel.ExamineModel('ExpRank', e_lambda)
	prior = None
	f = FilterModel.FilterModel(resultlist, prior)	
	task_length=2
	print resultlist
	inter = Interaction(e, f, task_length=task_length)	
	inter.run()
	print inter.action_list










	
