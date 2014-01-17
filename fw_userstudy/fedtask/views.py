# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth.models import User
from questionnaire.models import UserProfile
from fedtask.models import Session, Ranklist, Document, Bookmark, Experiment, Task, UserScore, Example
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.core.context_processors import csrf
from django.core.paginator import Paginator
from django.utils import simplejson
from django.core import serializers
import mimetypes
from django.core.servers.basehttp import FileWrapper
import os
from fw_userstudy import settings
import re,sys
import itertools
import operator
import simplejson
import pdb;

# This is the single entry point after user login
# basic user life cycle:
# 	register -> assign user_id -> assign session -> prequestionnaire
#	-> assign to experiment ->
#	-> redirected to task -> update session with finished task
#	-> start next task -> update session with finished task -> logout

#	login -> check session for prequestionnaire, experiment 
#	-> if not completed redirect to current task
#	-> if completed assign new task

def index(request):
	user = request.user
	user_id = user.id
	# If not authenticated, redirect to login
	if not user.is_authenticated():
		return redirect('%saccounts/login/'%settings.HOME_ROOT)	
	
	sess_mngr = Session.objects
	# get_session() may be 0 if no session is available
	sess = sess_mngr.get_session_stage(user_id)

	# we need some logic here for different types of experiments,
	# e.g., within and between subject.
	# between subject design, 4 conditions, assign based on
	# user_id. So mod 4 gives us experiments 0,1,2,3
	expmnt_id = user_id%2
	expmnt_mngr = Experiment.objects
	expmnt = expmnt_mngr.find_experiment(expmnt_id)
	# load the tasks for this experiment
	tasks = simplejson.loads(expmnt.exp_tasks)
	if not sess: 
		# set progress for task, new user so no progress
		task_prog = 0
		
		# Look in the experiment whether a questionnaire is required
		# otherwise set progress to completed
		pre_qst_prog  = 1
		if expmnt.pre_qst:
			pre_qst_prog = 0
		post_qst_prog  = 1
		if expmnt.pre_qst:
			post_qst_prog = 0

		# create the session
		sess = Session(session_id=user_id,\
						experiment_id=expmnt.experiment_id,\
						user_id = user_id,\
						task_progress = task_prog,\
						consent_progress = pre_qst_prog)
		sess.save()

	# now we are sure we have a session now we check
	# if the user has signed the consent
	# once consent is finished we set the session flag 
	if not sess.consent_progress:
		return redirect('%squestion/pre/'%settings.HOME_ROOT)	

	
	# redirect user to play the game 
	#
	return redirect('%sstudy/task/'%settings.HOME_ROOT)

def play(request):
	user = request.user
	# If not authenticated, redirect to login
	if not user.is_authenticated():
		return redirect('%saccounts/login/'%settings.HOME_ROOT)	
	# prepare contexts 
	c = {'user': user}	
	context = get_parameters(request)
	c.update(context)
	c.update(csrf(request))
	template = 'fedtask/task_ui%s_play.html'%c['ui_id']
	return render_to_response(template, c)

def instructions(request):
	user = request.user
	# If not authenticated, redirect to login
	if not user.is_authenticated():
		return redirect('%saccounts/login/'%settings.HOME_ROOT)	
	c = {'user': user}
	context = get_parameters(request)
	c.update(context)
	c.update(csrf(request))
	ui = c['ui_id']
	template = 'fedtask/instructions%s.html'%ui
	return render_to_response(template, c)

def highscores(request):
	user = request.user
	# If not authenticated, redirect to login
	if not user.is_authenticated():
		return redirect('%saccounts/login/'%settings.HOME_ROOT)	
	last_score, total_score, highscores, has_score, completed, fail = UserScore.objects.get_highscores_restrict(user)
	c = {'user': user, 
		'highscores': highscores, 
		'last_score':last_score, 
		'total_score': total_score,
		'has_score': has_score,
		'completed': completed,
		'fail': fail}
	context = get_parameters(request)
	c.update(context)
	c.update(csrf(request))
	template = 'fedtask/highscores.html'
	return render_to_response(template, c)

def get_parameters(request):
	current_session = Session.objects.get_session(request)
	session_id = current_session.session_id

	task = Task.objects.get_session_task(current_session)
	# get current user performance in terms of clicks
	clicksleft, maxclicks, relnum = UserScore.objects.get_score(request.user, task)	

	topic_id = task.topic.topic_id
	topic_text = task.topic.topic_text
	run_id = task.run_id
	ui_id = task.ui_id
	docs = Ranklist.objects.get_ranklist(topic_id, run_id, session_id)	
	paginator = Paginator(docs,10)
	bookmarks = Bookmark.objects.get_bookmark_count_wrap(session_id, topic_id, task.task_id, request.user)
	# Group docs by category
	category = process_category_info(docs)
	
	# Get a positive and a negative example for the current topic
	examples = Example.objects.get_examples(topic_id, run_id, session_id)
	description = 'This is a description'
	narrative = 'This is a narrative'

	# The give up threhs set in settings.py is when users have at least 
	# clicked X times. Here we convert it to the left clicks allowed
	give_up_thresh = settings.MaxClicks-settings.GiveUpThresh

	c = {	
		'num_docs': settings.NumDocs,
		'task_progress': current_session.task_progress,
		'task_id': task.task_id,	
		'session_id': session_id,
		'topic_id': topic_id,
		'topic_text': topic_text,
		'run_id': run_id,
		'ui_id': ui_id,
		'docs': docs,
		'paginator':paginator.page(1), # deliver 1st page
		'bookmark_count': bookmarks,
		'total_num_docs': len(docs),
		'category': category,
		'cate_json': simplejson.dumps(category),
		'clicksleft': clicksleft,
		'relnum': relnum,
		'rel_to_reach': settings.NumDocs-relnum,
		'rel_perc': float(relnum)/float(settings.NumDocs)*100,
		'maxclicks': maxclicks,
		'clicks_perc': float(clicksleft)/float(maxclicks)*100,
		'examples': simplejson.dumps(examples),
		'topic_description': description,
		'topic_narrative': narrative,
		'give_up_thresh': give_up_thresh,
		'give_up_hidden': '' if clicksleft < give_up_thresh else 'hidden',
	}
	return c

# Is this function actually used?
def fetch_results(request):
	current_session = Session.objects.get_session(request)
	session_id = current_session.session_id
	topic_id = request.POST['topic_id']
	run_id = request.POST['run_id']
	docs = Ranklist.objects.get_ranklist(topic_id, run_id, session_id)	
	if 'category' in request.POST:
		cat = request.POST['category'].replace("category_",'')
		if cat != 'all':
			category = process_category_info(docs)
			docs = [docs[i] for i in category[int(cat)+1]['doc_ranks']]
	json_data = simplejson.dumps(docs)
	response = HttpResponse(json_data, mimetype="application/json")
	return response

  
def fetch_document(request):
	if request.is_ajax:
		data = {}
		if request.POST['ajax_event'] == 'fetch_document':
			doc_id = request.POST['doc_id']
			# Get the document html location
			html_loc = Document.objects.get_html_location(doc_id)
			if html_loc == None or html_loc == '':
				data = 'Sorry, this document is not available.'	
			else:
				loc = '%s/%s'%(settings.DATA_ROOT, html_loc)
				f = open(loc)
				data = clean_html(f.read())
				f.close()
		json_data = simplejson.dumps(data)		
		response = HttpResponse(json_data, mimetype="application/json")
	else:
                return render_to_response('errors/403.html')
        return response


# Input: ranked document objects [(doc_object, rank)...]
def process_category_info(docs):
	# nested list comprehension:
	# d[1]['categories'] is a list of categories (c)
	# for each c we add a rank (d[0]) and the site (d[1]['site'])
	# eg: d=(12,{'site':'http://url.com','category':['News','Blogs']})
	# result: [('News',12,'http://url.com'),('Blogs',12,'http://url.com')]
	cates = [(c, d[0], d[1]['site']) for d in docs for c in d[1]['category'] ]
	cates.sort(key=operator.itemgetter(0))
	i = 0
	all_category = {
		"name": "All categories",
		"doc_count": len(docs),
	# doc_ranks uses original docs list so no double documents here as
	# we would have when using cates
		"doc_ranks": sorted([d[0] for d in docs]),
		"description": 'all documents are available', 
		"id": 'all',
		"active": 'active',
	}
	category = [all_category]
	for k, g in itertools.groupby(cates, lambda x: x[0]):
		gg = list(g)
		# here we group by category so double documents each go into
		# their own category.
		desc = ', '.join(sorted(list(set([d[2] for d in gg]))))
		item = {
			"name": k,
			"doc_count": len(gg),
			"doc_ranks": sorted([d[1] for d in gg]),
			"description": 'Search results from %s'%desc, 
			"id": i,
			"active": '',
		}
		category.append(item)
		i += 1
	return category 

# Submitted from a give up click
def submit_uncomplete_task(request):
	user = request.user
	# If not authenticated, redirect to login
	if not user.is_authenticated():
		return redirect('%saccounts/login/'%settings.HOME_ROOT)	
	UserScore.objects.register_giveup(request.user)	
	Task.objects.completed_task(request.user)
	
	return redirect("%sstudy/highscores"%settings.HOME_ROOT)

def submit_complete_task(request):
	user = request.user
	# If not authenticated, redirect to login
	if not user.is_authenticated():
		return redirect('%saccounts/login/'%settings.HOME_ROOT)	
	Task.objects.completed_task(request.user)
	return redirect("%sstudy/highscores"%settings.HOME_ROOT)


def clean_html(html):
#	f = open('tmp', 'w')
#	f.write(html)
#	f.close()
	# Only keep body part
	reg_body = re.compile('<body.*?>.+?</body>', re.MULTILINE|re.DOTALL)
	body = reg_body.findall(html)
	if body == []:
		text = html
	else:
		text = body[0] 	
	# clean javascriptsscripts
	reg_s = re.compile('<script.*?>.+?</script>', re.MULTILINE|re.DOTALL)
	text = reg_s.sub('', text)

	# clean inputs 
	reg_f = re.compile('<input.+?>')
	text = reg_f.sub('', text)
	reg_b = re.compile('<button.*?>.*?</button>')
	text = reg_b.sub('', text)
	reg_t = re.compile('<textarea.*?>*?</textarea>')
	text = reg_t.sub('', text)
	text = re.sub(r'<form .+?>', '', text)
	text = re.sub('</form>', '', text)

	#clean class style
	reg_c = re.compile('class=".+?"') 
	text = reg_c.sub('', text)
	
	# disable links 
	text_clean = re.sub(r'href=".+?"', '', text)

	# disable images if it's a relative path
	reg_img = re.compile('<img.*?/*>', re.MULTILINE|re.DOTALL)
	reg_src = re.compile('src=".+?"')	
	imgs = reg_img.findall(text_clean)
	for img in imgs:
		src = reg_src.findall(img)
		if len(src)>0:
			if not src[0].split('"')[1].startswith('http'):
				text_clean = text_clean.replace(img, '')
	# clean empty lists
	text_clean = re.sub(r'<li.*?></li>', '', text_clean)
	# remove 'body' tag
	text_final =  re.sub(r'<.*?body.*?>', '', text_clean)

	if text_final.strip() == '':
		text_final =  'Sorry, the content of the document is not available.'

	return text_final

def register_bookmark(request):
	if request.is_ajax:
		# feedback = 0 for unbookmark
		# feedback = 1 for bookmark of relevant doc
		# feedback = -1 for bookmark of unrelevant doc
		data = {'done':False,'count':0,'feedback':0};
		if request.POST['ajax_event'] == 'bookmark_document':
			# give feedback on correct/incorrect bookmarked documents
			data['feedback']=Bookmark.objects.get_feedback_bookmark(request)
			Bookmark.objects.update_bookmark(request, data['feedback'])
			# Get bookmark count, and user scores
			data['count'], data['userscore'] = Bookmark.objects.get_bookmark_count(request, request.user)
			if data['userscore']['relnum'] >= 10 or data['userscore']['clicksleft']<=0:
				data['done'] = True
		json_data = simplejson.dumps(data)		
		response = HttpResponse(json_data, mimetype="application/json")
		return response
	else:
		return render_to_response('errors/403.html')


def add_click(request):
	# add click to user score
	if request.is_ajax:
		UserScore.objects.add_click(request)
		task = Task.objects.get(task_id=request.POST['task_id'])
		clicksleft, maxclicks, numrel = UserScore.objects.get_score(request.user.id, task)
		data = {}
		data['userscore'] = {
			'clicksleft': clicksleft,
			'clicks_perc': float(clicksleft)/float(maxclicks)*100,
			'relnum': numrel,
			'rel_perc': float(numrel)/float(settings.NumDocs)*100,
			'rel_to_reach': settings.NumDocs-numrel,
			}		
		if data['userscore']['relnum'] >= 10 or data['userscore']['clicksleft']<=0:
			data['done'] = True
		json_data = simplejson.dumps(data)		
		response = HttpResponse(json_data, mimetype="application/json")
	else:
		return render_to_response('errors/403.html')
	return response
