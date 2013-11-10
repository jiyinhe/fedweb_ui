# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth.models import User
from questionnaire.models import UserProfile
from fedtask.models import Session, Ranklist
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.utils import simplejson
from django.core import serializers
import mimetypes
from django.core.servers.basehttp import FileWrapper
import os
from fw_userstudy import settings

session_id = 2
current_session = Session.objects.get_session(session_id)

# This is the single entry point after user login
def index(request):
	user = request.user
	# If not authenticated, redirect to login
	if not user.is_authenticated():
		return redirect('/accounts/login/')	
	
	# If the user hasn't done the pre-questionnaire
	# go to questionnaire
	# Otherwise go to the task page
	if UserProfile.objects.profile_exists(user.id):
		# Before go to a task page, 
		# Get a session_id,  training or testing?
		#session_id, session_type = Session.objects.get_current_session(user.id)
		return redirect('/study/task-train/')	
	else:
		return redirect('/question/pre/')	


def train(request):
	user = request.user
	# prepare contexts 
	c = {'user': user}	
	context = get_parameters()
	c.update(context)
	c.update(csrf(request))
	template = 'fedtask/task_ui%s_train.html'%c['ui_id']
	return render_to_response(template, c)


def test(request):
	c = {'user': request.user}	
	context = get_context()
	c.update(context)
	c.update(csrf(request))

	template = 'fedtask/task_ui%s_test.html'%c['ui_id']
	return render_to_response(template, c)


def get_parameters():
	task = current_session.task
	topic_id = task.topic.topic_id
	topic_text = task.topic.topic_text
	run_id = task.run_id
	ui_id = task.ui_id
	docs = Ranklist.objects.get_ranklist(topic_id, run_id)	
	c = {	
		'num_docs': settings.NumDocs,
		'topic_id': topic_id,
		'topic_text': topic_text,
		'run_id': run_id,
		'ui_id': ui_id,
		'docs': docs,
		'num_results': len(docs),
	}
	return c

def fetch_results(request):
	if request.is_ajax:
		data = {}
        	if request.POST['ajax_event'] == 'fetch_results':
			topic_id = request.POST['topic_id']
			run_id = request.POST['run_id']
			data = Ranklist.objects.get_ranklist(topic_id, run_id)	
		json_data = simplejson.dumps(data)		
		response = HttpResponse(json_data, mimetype="application/json")
	else:
                return render_to_response('errors/403.html')
        return response

  




