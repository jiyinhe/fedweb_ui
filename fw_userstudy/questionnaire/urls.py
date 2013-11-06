from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('questionnaire.views',
    (r'^pre/$', 'prequestion'),
)
