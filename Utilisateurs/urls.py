'''
Created on 28 Dec. 2010

@author: Alpimarc
'''

from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib.auth import views

urlpatterns = patterns('Utilisateurs',
    url('^$', views.login, {'template_name': 'connexion.html'}, name='connexion'),
    url('^Liste_FILE/$', "views.Liste_FILE"),
    url(r'^deconnexion/$', views.logout_then_login, name='deconnexion'),
)
