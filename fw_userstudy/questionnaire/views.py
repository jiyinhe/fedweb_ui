# Create your views here.
from pprint import pprint
from django.db import connection
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User 
from questionnaire.models import UserProfile
from fedtask.models import Session
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.utils import simplejson
from fw_userstudy import settings

# Register the user, and go to the pre-questionnaire page
def register_user(request):
	if request.is_ajax:
		data = {}
		if request.POST['ajax_event'] == 'register':
			data['status'] = True 
			data['errmsg'] = None
			username = request.POST['user']
			email = request.POST['email']
			passwd = request.POST['pass']
			try:
				u = User.objects.get(username__exact=username)
				data['errmsg'] = 'This username already exists'
				data['status'] = False
			except User.DoesNotExist:
				# Now we can  create the user
				user = User.objects.create_user(username, email, passwd)
		json_data = simplejson.dumps(data)		
		response = HttpResponse(json_data, mimetype="application/json")
        else:
                return render_to_response('errors/403.html')
        return response

# store the pre questionnaire data, and go to index
def store_preqst(request):
	# store the userprofile
	UserProfile.objects.store_profile(request)
	# update the session, that we finished the prequestionnaire
	Session.objects.completed_pre_qst(request)
	return redirect('%s'%settings.HOME_ROOT)


def prequestion(request):
	c = {'user': request.user,
		'ageoptions': [(1, '18-30'), (2, '31-40'), (3, '41-50'), (4, '51-60'), (5, '61-')],
		'likertscale': range(1,6)}
	c.update(csrf(request))

	template = 'questionnaire/pre-question-simple.html'
	return render_to_response(template, c)

def postquestion(request):
	c = {'user': request.user}
	c.update(csrf(request))

	template = 'questionnaire/post-question.html'
	return render_to_response(template, c)

def doneexperiment(request):
	c = {'user': request.user}
	c.update(csrf(request))

	template = 'questionnaire/done-experiment.html'
	return render_to_response(template, c)
