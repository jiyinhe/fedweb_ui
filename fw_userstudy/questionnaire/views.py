# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.utils import simplejson
from django.core import serializers
import mimetypes
from django.core.servers.basehttp import FileWrapper
import os

# Register the user, and go to the pre-questionnaire page
def register(request):
	c = {}
	template = 'questionnaire/pre-question.html'
	return render_to_response(template, c)	

def prequestion(request):
	c = {}
	tmplate = 'questionnaire/pre-question.html'
	return render_to_response(template, c)
