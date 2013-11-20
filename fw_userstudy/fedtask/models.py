from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
import simplejson as js
import operator

# Create your models here.
class Experiment(models.Model):
	experiment_id = models.IntegerField(primary_key=True)
	exp_description = models.TextField()
	prequestionnaire = models.BooleanField(default=True)
	postquestionnaire = models.BooleanField(default=False)
	tutorial = models.BooleanField(default=True)
	exp_type = models.CharField(max_length=45)
	

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
	# This need to be re-organized	
	# Get current search session for a user
	"""
	def get_current_session(self, user_id):
		session_id = 0
		session_type = ''
		# Check if the user has done a training session		
		session = self.filter(user_id=user_id, stage = 'train', progress=1)
		# If no finished training session, then go to training session
		if len(session) == 0:
			pass	
		# Otherwise, directly go to a test session			
		else:
			pass
		# Search for a session that the user has not finished yet	
		session = self.filter(user_id=user_id, progress=0)
		if len(session) == 0:
			# No session found, start a new session
			max_id = self.all().aggregate(Max('session_id'))
			if max_id['session_id__max'] == None:
				session_id = 1
			else:
				session_id = max_id['session_id__max'] + 1
			
		else:
			# Otherwise return current unfinished session
			print session	
		print session_id, session_type
		return session_id, session_type
	"""
	def get_session(self, session_id):
		return self.get(session_id__exact=session_id)

class Session(models.Model):
	session_id = models.IntegerField(primary_key=True)
	experiment = models.ForeignKey(Experiment)
	user = models.ForeignKey(User)
	task = models.ForeignKey(Task)
	ST = (('train', 'Training'), ('test', 'Testing'))
	stage = models.CharField(max_length=5, choices=ST)
	# 0: not done; 1: done
	progress = models.IntegerField()
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









	
