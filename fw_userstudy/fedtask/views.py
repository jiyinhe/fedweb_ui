# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth.models import User
from questionnaire.models import UserProfile
from fedtask.models import Session, Ranklist, Document
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.utils import simplejson
from django.core import serializers
import mimetypes
from django.core.servers.basehttp import FileWrapper
import os
from fw_userstudy import settings
import re

session_id = 1
current_session = Session.objects.get_session(session_id)

# This is the single entry point after user login
def index(request):
	user = request.user
	print user
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

# This is currently not used. Results are sent when loading the page
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

  
def fetch_document(request):
	if request.is_ajax:
		data = {}
        	if request.POST['ajax_event'] == 'fetch_document':
			doc_id = request.POST['doc_id']
			# Get the document html location
			html_loc = Document.objects.get_html_location(doc_id)
			if html_loc == None:
				data = 'Sorry, the document is not available.'	
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

def clean_html(html):
	f = open('tmp', 'w')
	f.write(html)
	f.close()
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

	#print text_final
	return text_final




