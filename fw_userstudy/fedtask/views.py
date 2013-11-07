# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth.models import User
from questionnaire.models import UserProfile
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.utils import simplejson
from django.core import serializers
import mimetypes
from django.core.servers.basehttp import FileWrapper
import os

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
		return redirect('/study/task-train/')	
	else:
		return redirect('/question/pre/')	

def train(request):
	c = {'user': request.user}	
	c.update(csrf(request))
	template = 'fedtask/task_ui1_train.html'
	return render_to_response(template, c)


def test(request):
	c = {'user': request.user}	
	c.update(csrf(request))
	template = 'fedtask/task_ui1_test.html'
	return render_to_response(template, c)


			
