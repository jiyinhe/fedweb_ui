from django.conf.urls.defaults import patterns, include, url

# These urls starts with /qusetion/

urlpatterns = patterns('questionnaire.views',
    (r'^register_user/$', 'register_user'),	
    (r'^store_preqst/$', 'store_preqst'),	
    (r'^pre/$', 'prequestion'),
    (r'^post/$', 'postquestion'),
    (r'^done/$', 'doneexperiment'),
)
