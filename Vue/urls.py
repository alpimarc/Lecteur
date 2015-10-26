'''
Created on 28 Dec. 2010

@author: Alpimarc
'''

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('Vue',
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/$', 'views.rapport'),
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/rapport.json$', "views.rapport_json"),
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/rapport/$', 'views.rapport'),
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/rapport/rapport.json$', "views.rapport_json"),
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/drilldown/(?P<id_table>[0-9]+)_(?P<id_ligne>[0-9]*)$', "views.drilldown"),
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/sidebar.html/$', "views.sidebar"),
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/control/$', "views.control"),
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/control/(?P<id_test>\d+)/$', "views.control"), # Vue d'un test
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/csv/(?P<id_tableResultat>[0-9]+).csv$', "views.view_csv"), # Vue d'un csv
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/csv/export_(?P<id_table>[0-9]+)_(?P<id_ligne>[0-9]+).csv$', "views.view_csv_critere"), # Vue d'un csv
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/control/(?P<id_test>\d+)/data_(?P<id_tableResultat>[0-9]+).json$', "views.json"), # Vue d'un csv
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/drilldown/critere_json_(?P<id_table>[0-9]+)_(?P<id_ligne>[0-9]*)$', "views.critere_json"), # Vue d'un csv
    url(r'^(?P<id_file>[A-Za-z\d_.\-]+)/control/(?P<id_test>\d+)/graphique_(?P<id_tableGraphique>[0-9]+).json$', "views.graphique_json"), # Vue d'un csv
)
