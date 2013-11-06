from django.conf.urls import patterns, include, url
from fw_userstudy import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fw_userstudy.views.home', name='home'),
    # url(r'^fw_userstudy/', include('fw_userstudy.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # Registration	

   # Overwrite the default registration 	
    url(r'^accounts/', include('registration.backends.simple.urls')),

    # Task
#    url(r'^study/', include('fedtask.urls')),

    # Questionnaire
    url(r'^question/', include('questionnaire.urls')),

)

#in devlopement mode, serving the static files
if settings.DEBUG:
	urlpatterns += patterns ('',
		url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
	)	

