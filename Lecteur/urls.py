'''
Created on 22 June 2013

@author: Alpimarc
'''

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', RedirectView.as_view(url='Login/Liste_FILE', permanent='True')),
	url(r'^Vue/', include('Vue.urls')),
    url(r'^Login/', include('Utilisateurs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^password/', include('password_policies.urls')),
    url(r'^tracking/', include('tracking.urls')),
)
