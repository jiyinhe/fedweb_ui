# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User 
from questionnaire.models import UserProfile
from fedtask.models import Session
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.utils import simplejson

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
	print "store preqst"
	print request.POST
	user_id = User.objects.get(username=request.user).id
	print user_id
	up = UserProfile(user_id=user_id,
					IP="11121212",
					gender=request.POST['gender'],
					year_of_birth=request.POST['age'],
					computer_exp=request.POST['computer'],
					english_exp=request.POST['english'],
					search_exp=request.POST['search'],
					education=request.POST['education'],
					consent=request.POST['consent'])
	up.save()
	sess = Session.objects.get(session_id=user_id)	
	print sess.user_id, sess.pre_qst_progress
	sess.pre_qst_progress = 1
	print sess.user_id, sess.pre_qst_progress
	sess.save()
	#json_data = simplejson.dumps(data)		
	#response = HttpResponse(json_data, mimetype="application/json")
	#else:
	#		return render_to_response('errors/403.html')
	return redirect('/')


def prequestion(request):
	c = {'user': request.user,
		'ageoptions': range(18,100),
		'likertscale': range(1,6)}
	c.update(csrf(request))

	template = 'questionnaire/pre-question.html'
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
