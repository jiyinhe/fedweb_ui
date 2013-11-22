from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
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
	def get_ranklist(self, topic_id, run_id):
		res = self.get(topic_id=topic_id, run_id=run_id)
		ranklist = js.loads(res.ranklist)
		# To keep the ranking
		id_ranklist = dict([(ranklist[i], i) for i in range(len(ranklist))])
		docs = Document.objects.filter(doc_id__in=ranklist)
		docs = [[id_ranklist[d.doc_id], 
			{
				'id':d.doc_id, 
				'title': '.' if d.title=='' else d.title, 
				'url': d.url if len(d.url)<=80 else d.url[0:80]+'...', 
				'summary': d.summary,
				'site': d.site.site_name,
				'category': d.site.category,
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


class Task(models.Model):
	task_id = models.IntegerField(primary_key=True)
	# Type of UI
	ui = models.ForeignKey(UI) 
	# The ranking
	run = models.ForeignKey(Run)
	# The topic
	topic = models.ForeignKey(Topic)

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
		try:
			qryset = self.filter(user_id=user_id).order_by(stage)
			return qryset[-1]
		except:
			return 0
		
	def get_session(self, session_id):
		return self.get(session_id__exact=session_id)

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
    def get_bookmark_count(self, sess_id, topic_id):
		try:
			bookmarks = Bookmark.objects.filter(topic_id=topic_id,session_id=sess_id,selected_state=1)
			return bookmarks.count()
		except Bookmark.DoesNotExist:
			return 0
	
class Bookmark(models.Model):
	session = models.ForeignKey(Session)
	topic = models.ForeignKey(Topic)	
	doc = models.ForeignKey(Document)		
	selected_state = models.IntegerField()
	objects = BookmarkManager()
    
	
class Qrels(models.Model):
	topic = models.ForeignKey(Topic)
	doc = models.ForeignKey(Document) 
	relevance = models.IntegerField() 









	
