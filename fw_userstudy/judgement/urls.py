from django.conf.urls.defaults import patterns, include, url

# These urls starts with /study/
urlpatterns = patterns('judgement.views',
    (r'^$', 'judgement'),
    (r'^load_results/$', 'load_results'),
#    (r'^doc_content/', 'fetch_document'),
#    (r'^bookmark/', 'register_bookmark'),
#    (r'^submit_complete_task/', 'submit_complete_task'),
)
