from django.db import models, connection
from django.contrib.auth.models import User
from django.db.models import Max, Count,Sum,Q
from django.http import HttpRequest, QueryDict
from whoosh.highlight import highlight, Highlighter, WholeFragmenter, HtmlFormatter
from whoosh.analysis import FancyAnalyzer
import simplejson as js
import operator
from fw_userstudy import settings 

# util function to highlight queries in a snippet
def get_highlighted_summary(summary,query, analyzer,frag,format):
	summary = unicode(summary.replace('\n', ' '))
	if len(summary) > 350:
		summary = unicode(summary.replace('\n', ' '))[0:350]+'...'
	hl = highlight(summary,query,analyzer,frag,format)
	if hl:
		return hl
	else:
		return summary

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
		# get the docids, and the relevance of the bookmarks
		bookmarks = [(b.doc_id.strip("_bookmark"),b.selected_state) for b in bookmarks]
		bookmarks = dict(bookmarks) # faster lookup

		# get the query for highlighting
		query = [q.text for q in analyzer(Topic.objects.get(topic_id=topic_id).topic_text)]

		ids = [(d.summary, d.doc_id) for d in docs]	
		docs = [[id_ranklist[d.doc_id], 
			{
				'id':d.doc_id, 
				'title': '.' if d.title=='' else d.title, 
				'url': d.url if len(d.url)<=80 else d.url[0:80]+'...', 
				'summary':get_highlighted_summary(d.summary,query,analyzer,frag,format),
				'site': d.site.site_name,
				'category': d.site.category.split(","),
				'bookmarked': bookmarks[d.doc_id] if d.doc_id in bookmarks else 0,
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
		task_index = sess.task_progress
		expmnt = Experiment.objects.get(experiment_id=sess.experiment_id)
		tasks = js.loads(expmnt.exp_tasks)
		# we get the task_id using the task list and index
		task_id = tasks[task_index]
		task = Task.objects.get(task_id=task_id)
		return task

	def completed_task(self, user):
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
	
	# get user session
	def get_session_stage(self, user_id):
		qryset = self.filter(user_id=user_id)
		if qryset:
			return qryset[0]
		else:
			return 0
		
	def get_session(self, request):
		user_id = request.user.id #User.objects.get(username=request.user).id
		sess = self.get(session_id=user_id)
		return sess

	def completed_pre_qst(self, request):
		user_id = User.objects.get(username=request.user).id
		sess = self.get(session_id=user_id)
		sess.consent_progress=1
		sess.save()

class Session(models.Model):
	session_id = models.IntegerField(primary_key=True)
	experiment = models.ForeignKey(Experiment)

	# progress indicates whether a user has completed this step
	# a zero is not complete, a 1 or higher is complete
	consent_progress = models.IntegerField() 
	task_progress = models.IntegerField()
	user = models.ForeignKey(User)
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
			'rel_to_reach': settings.NumDocs-relnum,
			}

		return bookmarks.count(), userscore

	def get_feedback_bookmark(self, request):
		topic_id=request.POST['topic_id']
		doc_id=request.POST['doc_id'].strip("_bookmark")
		state = request.POST['selected_state']
		user_id = request.user.id
		task_id = request.POST['task_id']
		# if bookmarking
		if state == "1":
			try: # did we bookmark a relevant doc, pos feedback
				Qrels.objects.get(topic_id=topic_id,doc_id=doc_id)
				us = UserScore.objects.click_rel(user_id, task_id, doc_id, True, True)
				return 1
			except Qrels.DoesNotExist: # otherwise neg feedback
				us = UserScore.objects.click_rel(user_id, task_id, doc_id, False, True)
				return -1
		# if unbookmarking
		if state == "0":
			try:
				# if a relevant doc is deleted from bookmark
				Qrels.objects.get(topic_id=topic_id,doc_id=doc_id)
				us = UserScore.objects.click_rel(user_id, task_id, doc_id, True, False)
			except Qrels.DoesNotExist:
				us = UserScore.objects.click_rel(user_id, task_id, doc_id, False, False)
		return 0

	def update_bookmark(self, request, feedback):
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
							selected_state=feedback)
				b.delete()
			except Exception,e: #Bookmark.MultipleObjectsReturned:
				print e
				print "removing all entries of the bookmarks"
				b = Bookmark.objects.filter(\
							doc_id=d_id,\
							session_id=s_id,\
							topic_id=t_id,\
							selected_state=feedback)
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
					selected_state=feedback)
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


	# Scoring rule:
	# - only count completed tasks
	# - a task is completed if the user has found requested number of relevant docs
	#   or has used up his clicks
	# - a task is incomplete if the user gives up 
	# In both cases: give up or use up clicks, it's 0 score

	def get_highscores_restrict(self, user):
		# Get every one's score, only counts completed job
		# failed job would get 0 points.
		all_scores = self.filter(Q(clickcount=settings.MaxClicks)|Q(numrel=settings.NumDocs)).values('user').annotate(total_score=Sum('score'), num_tasks=Count('score'))	

		if len(all_scores) == 0:
			all_scores = []
		else:
			all_scores = [(User.objects.get(id=a['user']).username, a['total_score'], a['num_tasks']) for a in all_scores]
			all_scores.sort(key=lambda x: x[1], reverse=True)
			# Get top 10
			all_scores = all_scores[0:10]	

		row = ["even", "odd"]
		highscores = [(row[i%2], i+1, all_scores[i][0], all_scores[i][1], all_scores[i][2]) for i in range(len(all_scores))]


		# Get current user's scores after the last round
		us = self.filter(user=user).order_by('id')
		# Check if the user has done anything
		total_clicks = sum([u.clickcount for u in us])
		# also get the total score, only include finished runs
		total_score = sum([s.score for s in self.filter(Q(clickcount=settings.MaxClicks)|Q(numrel=settings.NumDocs)).filter(user=user)])	
		
		if len(us) == 0:
			last_round_clicks = 0
			last_round_relfound = 0
			last_round_score = 0
			giveup = 0
		else:
			last_round = us[len(us)-1]
			last_round_clicks = last_round.clickcount
			last_round_relfound = last_round.numrel
			last_round_score = last_round.score
			giveup = last_round.giveup
		# Check user status
		has_score = True
		completed = False
		fail = False
 
		# If he hasn't click anything, nothing is done
		if total_clicks  == 0:
			has_score = False

		# If something has been done, check how far it is
		else:
			# check if a task is finished (get 10 rel/no clicks left)
			if last_round_relfound == settings.NumDocs:
			#success
				completed = True
				fail = False

			# fail: used up clicks or given up 
			elif last_round_clicks == settings.MaxClicks or giveup == 1: 
					fail = True
					completed = True	
			
			# otherwise, it's an uncompleted job	
			# fail = False, completed = False
		return last_round_score, total_score, highscores, has_score, completed, fail

	def register_giveup(self, user):
		sess_id = user.id
		sess = Session.objects.get(session_id=sess_id)
		task = Task.objects.get_session_task(sess)		 
		us = self.get(user=user, task=task)
		us.giveup = 1
		us.save()

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
	# whether user has given up
	giveup = models.IntegerField(default=0)
	objects = UserScoreManager()		
		


class ExampleManager(models.Manager):

	def get_examples(self,topic_id,run_id,session_id): 
		pos_obj = self.filter(topic_id=topic_id,judgement=1)[0]
		neg_obj = self.filter(topic_id=topic_id,judgement=-1)[0]
		pos_id = pos_obj.doc_id;
		neg_id = neg_obj.doc_id;
	
		print topic_id
		# get a description and narrative, can be taken from either
		# positive or negative example
		field_names = [f.name for f in Example._meta.fields]
		desc = pos_obj.description;
		nar = pos_obj.narrative;
		#docs = Ranklist.objects.get_ranklist(topic_id, run_id, session_id)

		# setup highlighting
		frag = WholeFragmenter()
		analyzer = FancyAnalyzer()
		format = HtmlFormatter(tagname="b")
		# get the query for highlighting
		query = [q.text for q in analyzer(Topic.objects.get(topic_id=topic_id).topic_text)]

		pd = Document.objects.get(doc_id=pos_id)
		nd = Document.objects.get(doc_id=neg_id)
		pd =[0,{'id':'example_'+pd.doc_id, 
				'title': '.' if pd.title=='' else pd.title, 
				'url': pd.url if len(pd.url)<=80 else pd.url[0:80]+'...', 
				'summary':get_highlighted_summary(pd.summary,query,analyzer,frag,format),
				'site': pd.site.site_name,
				'category': pd.site.category.split(","),
				'bookmarked': 1,
			}]
		nd =[1,{'id':'example_'+nd.doc_id, 
				'title': '.' if nd.title=='' else nd.title, 
				'url': nd.url if len(nd.url)<=80 else nd.url[0:80]+'...', 
				'summary':get_highlighted_summary(nd.summary,query,analyzer,frag,format),
				'site': nd.site.site_name,
				'category': nd.site.category.split(","),
				'bookmarked': -1,
			}]
		return [pd,nd],desc,nar

class Example(models.Model):
    topic = models.ForeignKey(Topic)
    doc = models.ForeignKey(Document)
# one of {-1,1} indicating relevant non relevant
    judgement = models.IntegerField()
# one of {0,1,3,7} indicating relevance level 0 lowest and 7 highest
    relevance = models.IntegerField()
    description = models.CharField(max_length=500)
    narrative = models.CharField(max_length=500)
    objects = ExampleManager()		
