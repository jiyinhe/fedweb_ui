# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth.models import User
from questionnaire.models import UserProfile
from judgement.models import Page, Result, Judgement, Query, Crawl
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
import pdb;


# This is the single entry point after user login
def index(request):
	user = request.user
	user_id = user.id
	# If not authenticated, redirect to login
	if not user.is_authenticated():
		return redirect('/accounts/login/')	
	
	return redirect('/judge/')	


def judgement(request):
	# Get current crawl, and query
	crawl_id = current_crawl
	qid = current_qid
	c = {'user': request.user}	
	context = get_parameters(request)
	c.update(context)
	c.update(csrf(request))

	template = 'judgement/judge.html'
	return render_to_response(template, c)

def get_parameters(request):
	topicnum, topictext = Query.objects.get_query(current_qid) 
	crawl_ids = Crawl.objects.get_crawl_ids() 
	current_qid, current_crawl = Judgement.assign_task(request.user.id)  	
	c = {
		'topic_num': topicnum,
		'topic_text': topictext,
		'qid': current_qid,
		'crawls': crawl_ids,
		'current_crawl': current_crawl,
		'current_query': current_qid,
		}
	return c

def load_results(request):
	if request.is_ajax:
		crawl_id = request.POST['current_crawl']
		qid = request.POST['current_query']

		data = {}
		data = Result.objects.get_results(crawl_id, qid, request.user.id)

		json_data = simplejson.dumps(data)		
		response = HttpResponse(json_data, mimetype="application/json")
	else:
		return render_to_response('errors/403.html')
	return response

def save_judge(request):
	if request.is_ajax:
		result_id = request.POST['result_id']
		judge_value = request.POST['judge']
		judge_type = request.POST['judge_type']
		
		data = Judgement.objects.save_judgement(request.user.id, result_id, judge_value, judge_type)

		json_data = simplejson.dumps(data)		
		response = HttpResponse(json_data, mimetype="application/json")
	else:
		return render_to_response('errors/403.html')
	return response

	