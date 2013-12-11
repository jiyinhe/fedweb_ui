from django.db import models, connection
from django.contrib.auth.models import User
from django.db.models import Max
from django.http import HttpRequest, QueryDict
from whoosh.highlight import highlight, Highlighter, WholeFragmenter, HtmlFormatter
from whoosh.analysis import FancyAnalyzer
import simplejson as js
import operator

# Create your models here.
class ExperimentManager(models.Manager):
	def find_experiment(self, expmnt_id):
		try:
			return Experiment.objects.get(experiment_id=expmnt_id)
		except Experiment.DoesNotExist:
			print "Error: we found no experiment. Populate the\
				experiment table first. Or try a different experiment ID"
			return 0		

class Experiment(models.Model):
	experiment_id = models.IntegerField(primary_key=True)
	exp_description = models.TextField()
	exp_tasks = models.TextField()
	pre_qst = models.BooleanField(default=True)
	post_qst = models.BooleanField(default=False)
	tutorial = models.BooleanField(default=True)
	exp_type = models.CharField(max_length=45)
	objects = ExperimentManager()
	

class UI(models.Model):
	ui_id = models.IntegerField(primary_key=True)
	ui_description = models.TextField()

class Topic(models.Model):
	topic_id = models.IntegerField(primary_key=True)
	topic_text = models.TextField()

class Run(models.Model):
	run_id = models.IntegerField(primary_key=True)
	description = models.TextField()

class RanklistManager(models.Manager):
	def get_ranklist(self, topic_id, run_id, session_id):
		res = self.get(topic_id=topic_id, run_id=run_id)
		frag = WholeFragmenter()
		analyzer = FancyAnalyzer()
		format = HtmlFormatter(tagname="b")

		print 'here'
		print highlight(u"lol bla lol bla lol", ['bla'], analyzer, frag, format)
		print 'here'
		ranklist = js.loads(res.ranklist)
		# To keep the ranking
		id_ranklist = dict([(ranklist[i], i) for i in range(len(ranklist))])
		docs = Document.objects.filter(doc_id__in=ranklist)
		bookmarks = Bookmark.objects.filter(topic_id=topic_id,
										session_id=session_id)
		# get the docids
		bookmarks = [b.doc_id.strip("_bookmark") for b in bookmarks]
		bookmarks = set(bookmarks) # faster lookup
		docs = [[id_ranklist[d.doc_id], 
			{
				'id':d.doc_id, 
				'title': '.' if d.title=='' else d.title, 
				'url': d.url if len(d.url)<=80 else d.url[0:80]+'...', 
				'summary': '...',
#				'summary': highlight(d.summary.replace('\n',' '),
#'bla',analyzer,frag,format) if len(d.summary)<=350 else highlight(d.summary[0:350].replace('\n',' '), 'bla',analyzer,frag,format)+'...',
				'site': d.site.site_name,
				'category': d.site.category,
				'bookmarked': 1 if d.doc_id in bookmarks else 0
			}] for d in docs]
		docs.sort(key=operator.itemgetter(0))
		return docs 

class Ranklist(models.Model):
	run = models.ForeignKey(Run)
	topic = models.ForeignKey(Topic)
	# Store the ranklist as a json object
	ranklist = models.TextField()
	objects = RanklistManager()

# Site classification
class Site(models.Model):
	site_id = models.CharField(max_length=45, primary_key=True)
	site_name = models.CharField(max_length=50)
	site_url = models.TextField()
	category = models.CharField(max_length=45)
	

class DocumentManager(models.Manager):
	# get the html location of the document
	def get_html_location(self, doc_id):
		try:
			doc = self.get(doc_id=doc_id)
			return doc.html_location 
		except Document.DoesNotExist:
			return None	


# Pool of all documents (e.g., from qrels)
class Document(models.Model):
	doc_id = models.CharField(max_length=50, primary_key=True)
	site = models.ForeignKey(Site)
	title = models.TextField()
	summary = models.TextField()
	url = models.TextField()
	html_location = models.TextField()
	objects = DocumentManager()

class TaskManager(models.Manager):
	def get_session_task(self, sess):
	    # to get the task we first get the index of the task our
		# experiment
		task_index = sess.task_progress + sess.training_progress
		expmnt = Experiment.objects.get(experiment_id=sess.experiment_id)
		tasks = js.loads(expmnt.exp_tasks)
		# we get the task_id using the task list and index
		task_id = tasks[task_index]
		task = Task.objects.get(task_id=task_id)
		return task

	def completed_train_task(self, user):
		sess_id = User.objects.get(username=user).id
		sess = Session.objects.get(session_id=sess_id)
		sess.training_progress +=1
		sess.save()

	def completed_test_task(self, user):
		sess_id = User.objects.get(username=user).id
		sess = Session.objects.get(session_id=sess_id)
		sess.task_progress +=1
		sess.save()

class Task(models.Model):
	task_id = models.IntegerField(primary_key=True)
	# Type of UI
	ui = models.ForeignKey(UI) 
	# The ranking
	run = models.ForeignKey(Run)
	# The topic
	topic = models.ForeignKey(Topic)
	objects = TaskManager()

class SessionManager(models.Manager):
	# Call this the first time a user is registered
	# a session keeps track of how far a user is in an experiment
	# for now a user may only partake in one experiment and does only
	# has one session. We can make this dependent on "stage" to create
	# a within subject design.
	def register_session(self, user_id):
		new_sess = Session(user_id=user_id)
		return new_sess

	def get_session_stage(self, user_id):
		# session may be multiple if we have a within subject design
		# we use stage to keep track of this
		qryset = self.filter(user_id=user_id).order_by('-stage')
		if qryset:
			return qryset[0]
		else:
			return 0
		
	def get_session(self, request):
		user_id = User.objects.get(username=request.user).id
		sess = self.get(session_id=user_id)
		return sess

	def completed_pre_qst(self, request):
		user_id = User.objects.get(username=request.user).id
		sess = self.get(session_id=user_id)
		sess.pre_qst_progress=1
		sess.save()

class Session(models.Model):
	session_id = models.IntegerField(primary_key=True)
	experiment = models.ForeignKey(Experiment)

	# progress indicates whether a user has completed this step
	# a zero is not complete, a 1 or higher is complete
	pre_qst_progress = models.IntegerField() 
	post_qst_progress = models.IntegerField()
	training_progress = models.IntegerField()
	task_progress = models.IntegerField()

	user = models.ForeignKey(User)
	stage = models.IntegerField()
	objects = SessionManager()

class BookmarkManager(models.Manager):

	# wrapper in case request does not have session_id and topic_id
	# (i.e., on page load)
	def get_bookmark_count_wrap(self, sess_id, t_id):
		request = HttpRequest()	
		request.POST=QueryDict('session_id='+str(sess_id)+'&topic_id='+str(t_id))
		return self.get_bookmark_count(request)

	def get_bookmark_count(self, request):
		sess_id=request.POST['session_id']
		topic_id=request.POST['topic_id']
		try:
			bookmarks = Bookmark.objects.filter(topic_id=topic_id,session_id=sess_id,selected_state=1)
				
			return bookmarks.count()
		except Bookmark.DoesNotExist:
			return 0

	def training_feedback_bookmark(self, request):
		# only in training
		if "task-train" in request.META['HTTP_REFERER']:
			sess_id=request.POST['session_id']
			topic_id=request.POST['topic_id']
			doc_id=request.POST['doc_id'].strip("_bookmark")
			state = request.POST['selected_state']
			# only feedback if bookmarking not unbookmarking
			if state == "1":
				try: # did we bookmark a relevant doc, pos feedback
					Qrels.objects.get(topic_id=topic_id,doc_id=doc_id)
					return "positive_feedback"
				except Qrels.DoesNotExist: # otherwise neg feedback
					return "negative_feedback"
			if state == "0":
				return "delete_feedback"
		return "no_feedback"

	def update_bookmark(self, request):
		d_id = request.POST['doc_id']
		s_id = request.POST['session_id']
		t_id = request.POST['topic_id']
		state = request.POST['selected_state']
#		   insert bookmark activity
		if state == "0": # unregister bookmark
#		   first find the bookmarked document
			try:
				b = Bookmark.objects.get(\
							doc_id=d_id,\
							session_id=s_id,\
							topic_id=t_id,\
							selected_state=1)
				b.delete()
			except Bookmark.MultipleObjectsReturned:
				print "removing all entries of the bookmarks"
				b = Bookmark.objects.filter(\
							doc_id=d_id,\
							session_id=s_id,\
							topic_id=t_id,\
							selected_state=1)
				b.delete() # delete complete queryset
		else:
#		   save the new entry for the bookmarked document
			try:
				b = Bookmark.objects.get(\
							doc_id=d_id,\
							session_id=s_id,\
							topic_id=t_id)
			except Bookmark.DoesNotExist:				
				b = Bookmark(\
					doc_id=d_id,\
					session_id=s_id,\
					topic_id=t_id,\
					selected_state=state)
				b.save()
	
	
class Bookmark(models.Model):
	session = models.ForeignKey(Session)
	topic = models.ForeignKey(Topic)	
	doc = models.ForeignKey(Document)		
	selected_state = models.IntegerField()
	objects = BookmarkManager()
    
class QrelsManager(models.Manager):
	pass
	
class Qrels(models.Model):
	topic = models.ForeignKey(Topic)
	doc = models.ForeignKey(Document) 
	relevance = models.IntegerField() 
	objects = QrelsManager()









	
