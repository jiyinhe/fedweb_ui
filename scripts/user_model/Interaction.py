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
	def __init__(self, page_size=10, task_length=1, start=[0, 0], examineModel, filterModel):
		self.page_size = page_size
		self.K = task_length
		self.E = examineModel
		self.F = filterModel
		self.resultlist = examineModel.resultlist 

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
		self.last_visit = [0 for i in self.resultlist]
		
		# the current list the user is at
		self.current_visit = start 

	# Start a simulation
	def run(self):
		# Only stop when all documents being examined, or K document has been found   
		while not (self.rel_count == self.K or self.len(self.doc_seen) == self.doc_count):	
			# Now we are at a list, check if next doc has been seen already, if so, skip it
			if self.doc_is_seen():			
				continue

			# Now we are at a new doc, decide if examine another document
			if not self.examine_next():
				# If not, first do filtering
				listid = self.choose_list()
				self.action_list.append('filter')
				# then set the current visit to the next doc in the list
				# Note: if a list is exhausted, it won't be selected 
				self.current_visit = [listid, self.last_visit[listid]+1]

			# Now whether it's coming from a filter or that we've decided to 
			# examine the next doc, we will examine it		 

			# If the doc is in a next page, first add pagination
			if self.current_list[1]%self.page_size == 0:
				self.action_list.append('pagination')
			# Then examine doc 
			self.examine_doc()
			self.action_list.append('examine')


	# Choose a sublist 
	def choose_list(self):
		return self.F.select_list()

	# Decide if we should examine another doc
	def examine_next(self):
		# If the current visit position is larger than the maximum docs in the list, then this doc cannot be examined
		if self.current_visit[1] >= len(self.resultlist[self.current_visit[0]]):
			return False
		else:
			return self.E.examine_next()==1	
	
	# Actually examine the doc
	def examine_doc(self):
		# Get next doc from current_visit
		res = resultlist[self.current_visit[0]][self.current_visit[1]] 	
		docid = res[0]

		# add doc to seen list
		self.doc_seen.append(docid)
		# Check relevance
		self.rel_count += res[2]
		# add this position to last visit
		self.last_visit[self.current_visit[0]] = self.current_visit[1]

		# move current_visit to the next doc in the current list
		current_visit[1] = self.current_visit[1] + 1 	


	# Check if next doc in the list is already seen, 
	# if not, set the current_visit to that doc 
	# if yes, skip that doc, set the current_visit to a next doc
	def doc_is_seen(self):
		res = resultlist[self.current_visit[0]][self.current_visit[1]] 	
		docid = res[0]
		if docid in self.doc_seen:
			# move the current_visit to next doc in the list
			current_visit[1] = self.current_visit[1] + 1
			return True
		else:	
			return False





