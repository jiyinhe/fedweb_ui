# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect 
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
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


def prequestion(request):
	c = {'user': request.user}
	c.update(csrf(request))

	template = 'questionnaire/pre-question.html'
	return render_to_response(template, c)
