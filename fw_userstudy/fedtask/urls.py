from django.conf.urls.defaults import patterns, include, url

# These urls starts with /study/
urlpatterns = patterns('fedtask.views',
    (r'^task-train/$', 'train'),
    (r'^task-work/$', 'test'),	
    #(r'^results/$', 'fetch_results'),
    (r'^doc_content/', 'fetch_document'),
    (r'^bookmark/', 'register_bookmark'),
)
