from django.conf.urls.defaults import patterns, include, url

# These urls starts with /study/
urlpatterns = patterns('judgement.views',
    (r'^$', 'judgement'),
    (r'^load_results/$', 'load_results'),
    (r'^save_judge/$', 'save_judge'),
    (r'^doc_content/', 'fetch_document'),
    (r'^duplicate_submit', 'duplicate_submit'),
    (r'^duplicate_delete', 'duplicate_delete'),
#    (r'^bookmark/', 'register_bookmark'),
#    (r'^submit_complete_task/', 'submit_complete_task'),
)
