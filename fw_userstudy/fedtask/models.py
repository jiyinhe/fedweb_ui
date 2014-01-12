from django.db import models, connection
from django.contrib.auth.models import User
from django.db.models import Max
from django.http import HttpRequest, QueryDict
from whoosh.highlight import highlight, Highlighter, WholeFragmenter, HtmlFormatter
from whoosh.analysis import FancyAnalyzer
import simplejson as js
import operator
from fw_userstudy import settings 
from django.db.models import Sum
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

class TopicManager(models.Manager):
	pass
	

class Topic(models.Model):
	topic_id = models.IntegerField(primary_key=True)
	topic_text = models.TextField()
	objects = TopicManager()

class Run(models.Model):
	run_id = models.IntegerField(primary_key=True)
	description = models.TextField()

class RanklistManager(models.Manager):
	def get_ranklist(self, topic_id, run_id, session_id):
		res = self.get(topic_id=topic_id, run_id=run_id)
		frag = WholeFragmenter()
		analyzer = FancyAnalyzer()
		format = HtmlFormatter(tagname="b")

		ranklist = js.loads(res.ranklist)
		# To keep the ranking
		id_ranklist = dict([(ranklist[i], i) for i in range(len(ranklist))])
		docs = Document.objects.filter(doc_id__in=ranklist)
		bookmarks = Bookmark.objects.filter(topic_id=topic_id,
										session_id=session_id)
		# get the query for highlighting
		query = [q.text for q in analyzer(Topic.objects.get(topic_id=topic_id).topic_text)]
		# get the docids
		bookmarks = [b.doc_id.strip("_bookmark") for b in bookmarks]
		bookmarks = set(bookmarks) # faster lookup
		ids = [(d.summary, d.doc_id) for d in docs]	
		for (sum,id) in ids[:10]:
			print 
		docs = [[id_ranklist[d.doc_id], 
			{
				'id':d.doc_id, 
				'title': '.' if d.title=='' else d.title, 
				'url': d.url if len(d.url)<=80 else d.url[0:80]+'...', 
				'summary':self.get_highlighted_summary(d.summary,query,analyzer,frag,format),
				'site': d.site.site_name,
				'category': d.site.category,
				'bookmarked': 1 if d.doc_id in bookmarks else 0
			}] for d in docs]
		docs.sort(key=operator.itemgetter(0))
		
		return docs 

	def get_highlighted_summary(self,summary,query, analyzer,frag,format):
		summary = unicode(summary.replace('\n', ' '))
		if len(summary) > 350:
			summary = unicode(summary.replace('\n', ' '))[0:350]+'...'
		hl = highlight(summary,query,analyzer,frag,format)
		if hl:
			return hl
		else:
			return summary

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
	# The maximum clicks allowed
	maxclicks = models.IntegerField()

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
	def get_bookmark_count_wrap(self, sess_id, t_id, task_id, user):
		request = HttpRequest()	
		request.POST=QueryDict('session_id='+str(sess_id)+'&topic_id='+str(t_id)+'&task_id='+str(task_id))
		return self.get_bookmark_count(request, user)

	def get_bookmark_count(self, request, user):
		sess_id=request.POST['session_id']
		topic_id=request.POST['topic_id']
		task_id = request.POST['task_id']
		bookmarks = Bookmark.objects.filter(topic_id=topic_id,session_id=sess_id,selected_state=1)

		task = Task.objects.get(task_id = task_id)
		clicksleft, maxclicks, relnum = UserScore.objects.get_score(user, task)
		userscore = {
			'clicksleft': clicksleft,
			'clicks_perc': float(clicksleft)/float(maxclicks)*100,
			'relnum': relnum,
			'rel_perc': float(relnum)/float(settings.NumDocs)*100,
			}

		return bookmarks.count(), userscore

	def training_feedback_bookmark(self, request):
		# only in training
		if "task-train" in request.META['HTTP_REFERER']:
			sess_id=request.POST['session_id']
			topic_id=request.POST['topic_id']
			doc_id=request.POST['doc_id'].strip("_bookmark")
			state = request.POST['selected_state']
			user_id = request.user.id
			task_id = request.POST['task_id']
			# only feedback if bookmarking not unbookmarking
			if state == "1":
				try: # did we bookmark a relevant doc, pos feedback
					Qrels.objects.get(topic_id=topic_id,doc_id=doc_id)
					us = UserScore.objects.click_rel(user_id, task_id, doc_id, True, True)
					return "positive_feedback"
				except Qrels.DoesNotExist: # otherwise neg feedback
					us = UserScore.objects.click_rel(user_id, task_id, doc_id, False, True)
					return "negative_feedback"
			if state == "0":
				try:
					# if a relevant doc is deleted from bookmark
					Qrels.objects.get(topic_id=topic_id,doc_id=doc_id)
					us = UserScore.objects.click_rel(user_id, task_id, doc_id, True, False)
				except Qrels.DoesNotExist:
					us = UserScore.objects.click_rel(user_id, task_id, doc_id, False, False)
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

class UserScoreManager(models.Manager):
	def create_userprofile(self, user, task):
		u = User.objects.get(id = user.id)
		us = UserScore(user=u, task=task, clickcount=0, score=0, numrel=0)		 
		us.save()
		return us

	def get_score(self, user, task):
		try:
			us = self.get(user=user, task=task)
		except UserScore.DoesNotExist:
			us = self.create_userprofile(user, task)
		clicksleft = task.maxclicks-us.clickcount
		return  clicksleft, task.maxclicks, us.numrel

	# select: true if it's selected, false if it's removed
	def click_rel(self, user_id, task_id, doc_id, relevance, select):
		us = self.get(user=user_id, task=task_id)
		us.clickcount += 1
		us.score = us.task.maxclicks - us.clickcount
		if us.reldocs == "":
			reldocs = []
		else:
			reldocs = js.loads(us.reldocs)
		# If adding/removing a relevant document, update the relnum
		if relevance:
			if select:
				reldocs.append(doc_id)
				reldocs = set(reldocs)
			else:
				reldocs = set(reldocs)-set([doc_id])
		us.reldocs = js.dumps(list(reldocs))
		us.numrel = len(reldocs)
		us.save()
		return us

	def add_click(self, request):
		us = self.get(user=request.user.id, task=request.POST['task_id'])
		us.clickcount += 1
		us.score = us.task.maxclicks - us.clickcount
		us.save()

	def get_highscores(self, user):
		# Get user score
		us = self.filter(user=user, numrel=10).order_by('task')
		if len(us) == 0:
			last_score = 0
			total_score = 0
		else:
			last_score = us[len(us)-1].score
			total_score = sum([s.score for s in us])
		# Get every one's score
		all_scores = self.filter(numrel=10).values('user').annotate(total_score=Sum('score'))	
		if len(all_scores) == 0:
			all_scores = []
		else:
			all_scores = [(User.objects.get(id=a['user']).username, a['total_score']) for a in all_scores]
			all_scores.sort(key=lambda x: x[1], reverse=True)
			all_scores = all_scores[0:10]	
		row = ["even", "odd"]
		highscores = [(row[i%2], i+1, all_scores[i][0], all_scores[i][1]) for i in range(len(all_scores))]
		has_score = True
		if total_score == 0:
			has_score = False
		return last_score, total_score, highscores, has_score

class UserScore(models.Model):
	user = models.ForeignKey(User)
	task = models.ForeignKey(Task)
	# number of clicks for this task so far
	clickcount = models.IntegerField() 
	# score of this task, i.e., task.maxclicks - clickcount
	score = models.IntegerField()	
	# number of relevant document found
	numrel = models.IntegerField()
	# relevant documents found, stored as json object
	reldocs = models.TextField()	
	objects = UserScoreManager()		


