# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth.models import User
from questionnaire.models import UserProfile
from judgement.models import Page, Result, Judgement  
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
	c = {'user': request.user}	
	context = get_parameters(request)
	c.update(context)
	c.update(csrf(request))

	template = 'judgement/judge.html'
	return render_to_response(template, c)

def get_parameters(request):
	c = {}
	return c

