# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth.models import User
from questionnaire.models import UserProfile
from judgement.models import Page, Result, Judgement, Query, Crawl, UserProgress
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.core.context_processors import csrf
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
import pdb
import utils


# This is the single entry point after user login
def index(request):
	user = request.user
	user_id = user.id
	# If not authenticated, redirect to login
	if not user.is_authenticated():
        	return redirect('%saccounts/login/'%settings.LOGIN_REDIRECT_URL)
	
	return redirect('%sjudge/'%settings.LOGIN_REDIRECT_URL)	


def judgement(request):
	# Get current crawl, and query
	c = {'user': request.user}	
	context = get_parameters(request)
	c.update(context)
	c.update(csrf(request))

	template = 'judgement/judge.html'
	return render_to_response(template, c)

def get_parameters(request):
	#crawl_ids = Crawl.objects.get_crawl_ids() 
	# Get a task	
	current_qid = request.POST.get('query', -1)
	if current_qid == -1:
		#current_qid, current_crawl = UserProgress.objects.assign_task(request.user.id)  	
		current_qid = UserProgress.objects.assign_task(request.user.id)
	#else:
		#current_crawl = 1

	topicnum, topictext = Query.objects.get_query(current_qid) 
	all_queries = Query.objects.get_all_queries()

	c = {
		'topic_num': topicnum,
		'topic_text': topictext,
		'qid': current_qid,
		#'crawls': crawl_ids,
		#'current_crawl': current_crawl,
		'current_query': current_qid,
		'all_queries': all_queries,
		}
	return c

def load_results(request):
	if request.is_ajax:
		#crawl_id = request.POST['current_crawl']
		qid = request.POST['current_query']

		data = {}
		#data = Result.objects.get_results(crawl_id, qid, request.user.id)
		data['docs'] = Judgement.objects.get_results_to_judge(qid, request.user.id)
		data['judged_s'] = sum([int(d['judge']['relevance_snippet']>0) for d in data['docs']])
		data['judged_p'] = sum([int(d['judge']['relevance_doc']>0) for d in data['docs']])


		json_data = simplejson.dumps(data)		
		response = HttpResponse(json_data, mimetype="application/json")
	else:
		return render_to_response('errors/403.html')
	return response

def save_judge(request):
	if request.is_ajax:
		#result_id = request.POST['result_id']
		qid = request.POST['current_query']
		page_id = request.POST['page_id']
		judge_value = request.POST['judge']
		judge_type = request.POST['judge_type']
		#progress = (request.POST['total_docs'], request.POST['s_count'], request.POST['p_count'])
		total_docs = request.POST['total_docs']
	
		#data = Judgement.objects.save_judgement(request.user.id, result_id, judge_value, judge_type, progress)
		data = Judgement.objects.save_judgement(request.user.id, qid, page_id, judge_value, judge_type, total_docs)
		#print data
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
			#print doc_id
			html_loc, img_loc = Page.objects.get_html_location(doc_id)
			#print html_loc
			if html_loc == None or html_loc == '':
				data = 'Sorry, this document is not available.'	
			else:
				if img_loc == None: 
					loc = '%s/%s'%(settings.DATA_ROOT, html_loc)
					f = open(loc)
					data = utils.clean_html(f.read())
					f.close()
				else:
					loc = '%s/%s'%(settings.DATA_ROOT, img_loc)
					tmp = '<img href="%s" />'%loc
					data = tmp
		json_data = simplejson.dumps(data)		
		response = HttpResponse(json_data, mimetype="application/json")
	else:
                return render_to_response('errors/403.html')
        return response


