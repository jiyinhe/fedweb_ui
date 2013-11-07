from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Experiment(models.Model):
	experiment_id = models.IntegerField(primary_key=True)
	exp_description = models.TextField()
	prequestionnaire = models.BooleanField(default=True)
	postquestionnaire = models.BooleanField(default=False)
	tutorial = models.BooleanField(default=True)
	UT = (('L', 'Lab'), ('F', 'Field'), ('C', 'Crowdsource'))
	exp_type = models.CharField(max_length=1, choices=UT)


class UI(models.Model):
	ui_id = models.IntegerField(primary_key=True)
	ui_description = models.TextField()

class Topic(models.Model):
	topic_id = models.IntegerField(primary_key=True)
	topic_text = models.TextField()

class Run(models.Model):
	run_id = models.IntegerField(primary_key=True)
	# Store the ranklist as a json object
	ranklist = models.TextField()

class Task(models.Model):
	task_id = models.IntegerField(primary_key=True)
	# Type of UI
	ui = models.ForeignKey(UI) 
	# The ranking
	run = models.ForeignKey(Run)
	# The topic
	topic = models.ForeignKey(Topic)

class Session(models.Model):
	session_id = models.IntegerField(primary_key=True)
	experiment = models.ForeignKey(Experiment)
	user_id = models.ForeignKey(User)
	task_id = models.ForeignKey(Task)
	ST = (('TR', 'Training'), ('TE', 'Testing'))
	stage = models.CharField(max_length=1, choices=ST)
	# 0: not done; 1: done
	progress = models.IntegerField()

# Site classification
class Site(models.Model):
	site_id = models.IntegerField(primary_key=True)
	site_name = models.CharField(max_length=50)
	site_url = models.TextField()
	category = models.CharField(max_length=45)
	

# Pool of all documents (e.g., from qrels)
class Document(models.Model):
	doc_id = models.IntegerField(primary_key=True)
	docno = models.CharField(max_length=50)
	site = models.ForeignKey(Site)
	title = models.TextField()
	summary = models.TextField()
	url = models.TextField()
	html_location = models.TextField()
	
class Bookmark(models.Model):
	session = models.ForeignKey(Session)
	topic = models.ForeignKey(Topic)	
	doc = models.ForeignKey(Document)		

class Qrels(models.Model):
	topic = models.ForeignKey(Topic)
	doc = models.ForeignKey(Document) 
	relevance = models.IntegerField() 









	
