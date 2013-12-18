# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth.models import User
from questionnaire.models import UserProfile
from fedtask.models import Session, Ranklist, Document, Bookmark, Experiment, Task
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.core.context_processors import csrf
from django.core.paginator import Paginator
from django.utils import simplejson
from django.core import serializers
import mimetypes
from django.core.servers.basehttp import FileWrapper
import os
from fw_userstudy import settings
import re
import itertools
import operator
import simplejson
import pdb;

# set required number of training tasks
REQ_TRAIN_TASKS=3

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
	expmnt_id = user_id%4
	expmnt_mngr = Experiment.objects
	expmnt = expmnt_mngr.find_experiment(expmnt_id)

	# load the tasks for this experiment
	tasks = simplejson.loads(expmnt.exp_tasks)
	if not sess: 
		# nosession means no prequestionnaire 
		pre_qstnr = 0

		# we have a within subject design so our stage is -1
		# within could have stage 0,1,2,3, for experiment 0,1,2,3
		stage = -1

		# set progress for task, new user so no progress
		task_prog = 0
		
		# check in experiment whether training is required otherwise
		# set to completed. 
		train_prog  = REQ_TRAIN_TASKS
		if expmnt.tutorial:
			train_prog = 0

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
						stage = stage,\
						training_progress = train_prog,\
						pre_qst_progress = pre_qst_prog,\
						post_qst_progress = post_qst_prog)
		sess.save()

	# now we are sure we have a session now we check for
	# pre questionnaire  progress
	# once preqst is finished we set the session flag 
	if not sess.pre_qst_progress:
		return redirect('%squestion/pre/'%settings.HOME_ROOT)	
	
	# training and training progress, user does 3 training tasks
	# for now: these are the first X tasks in the experiment task
	# list. Could make a separate field. Now we use progress as an
	# index into the task list. (HACKY)
	if sess.training_progress < REQ_TRAIN_TASKS:
		return redirect('%sstudy/task-train/'%settings.HOME_ROOT)
		
	# task and task progress, task progress + train progress is an
	# index in the experiment.exp_tasks list. 
	if sess.task_progress+sess.training_progress < len(tasks):
		return redirect('%sstudy/task-work/'%settings.HOME_ROOT)

	# When all tasks have been done we check whether a post
	# questionnaire is required
	if not sess.post_qst_progress:
		return redirect('%squestion/post/'%settings.HOME_ROOT)

	# finally we thank the user for participating
	return redirect('%squestion/done/'%settings.HOME_ROOT)	

def train(request):
	user = request.user
	# prepare contexts 
	c = {'user': user}	
	context = get_parameters(request)
	c.update(context)
	c.update(csrf(request))
	template = 'fedtask/task_ui%s_train.html'%c['ui_id']
	return render_to_response(template, c)

def test(request):
	c = {'user': request.user}	
	context = get_parameters(request)
	c.update(context)
	c.update(csrf(request))

	template = 'fedtask/task_ui%s_test.html'%c['ui_id']
	return render_to_response(template, c)

def get_parameters(request):
	current_session = Session.objects.get_session(request)
	session_id = current_session.session_id

	task = Task.objects.get_session_task(current_session)

	topic_id = task.topic.topic_id
	topic_text = task.topic.topic_text
	run_id = task.run_id
	ui_id = task.ui_id
	docs = Ranklist.objects.get_ranklist(topic_id, run_id, session_id)	
	paginator = Paginator(docs,10)
	bookmarks = Bookmark.objects.get_bookmark_count_wrap(session_id,topic_id)
	# Group docs by category
	category = process_category_info(docs)
	c = {	
		'num_docs': settings.NumDocs,
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
	}
	return c

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
	cates = [(d[1]['category'], d[0], d[1]['site']) for d in docs]
	cates.sort(key=operator.itemgetter(0))
	i = 0
	all_category = {
		"name": "All categories",
		"doc_count": len(docs),
		"doc_ranks": sorted([d[0] for d in docs]),
		"description": 'all documents are available', 
		"id": 'all',
		"active": 'active',
	}
	category = [all_category]
	for k, g in itertools.groupby(cates, lambda x: x[0]):
		gg = list(g)
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

def submit_complete_task(request):
	# is the user still training
	referer = request.META['HTTP_REFERER']
	if 'task-train' in referer:
		Task.objects.completed_train_task(request.user)	
	else:
		Task.objects.completed_test_task(request.user)
	return redirect("/")


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
	print "register bookmark"
	# TODO: only provide feedback for training, not in test
	# test whether URL contains "test" or "train"
	if request.is_ajax:
		data = {'done':False,'count':0,'feedback':"no_feedback"};
		if request.POST['ajax_event'] == 'bookmark_document':
			Bookmark.objects.update_bookmark(request)
			data['count'] = Bookmark.objects.get_bookmark_count(request)
			if data['count'] >= 10:
				data['done'] = True
			# give feedback on correct/incorrect bookmarked documents
			# in training fase
			data['feedback']=Bookmark.objects.training_feedback_bookmark(request)
		json_data = simplejson.dumps(data)		
		response = HttpResponse(json_data, mimetype="application/json")
	else:
		return render_to_response('errors/403.html')
	return response
