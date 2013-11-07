from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('fedtask.views',
    (r'^$', 'index'),
)
