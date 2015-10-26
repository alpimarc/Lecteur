'''
Created on 28 Dec. 2010

@author: Alpimarc
'''

from django.contrib import admin
from Utilisateurs.models import FILE, Droit

admin.site.register(FILE)
admin.site.register(Droit)
