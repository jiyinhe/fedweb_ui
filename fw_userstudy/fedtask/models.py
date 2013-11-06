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
	ui_id = models.ForeignKey(UI) 
	# The ranking
	run_id = models.ForeignKey(Run)
	# The topic
	topic_id = models.ForeignKey(Topic)


class Session(models.Model):
	session_id = models.IntegerField(primary_key=True)
	experiment_id = models.ForeignKey(Experiment)
	user_id = models.ForeignKey(User)
	task_id = models.ForeignKey(Task)
	ST = (('TR', 'Training'), ('TE', 'Testing'))
	stage = models.CharField(max_length=1, choices=ST)
	# 0: not done; 1: done
	progress = models.IntegerField()

class bookmark(models.Model):
	session_id = models.ForeignKey(Session)
	topic_id = models.ForeignKey(Topic)	
	doc_id = models.CharField(max_length=50)		



	
