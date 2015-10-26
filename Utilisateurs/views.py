#-*- coding: utf-8 -*-
'''
Created on 22 June 2013

@author: Alpimarc
'''

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from Utilisateurs.forms import ConnexionForm
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from Utilisateurs.models import FILE, Droit
from django.conf import settings

@login_required
def Liste_FILE(request):
    for bdd in settings.DATABASES:
        if bdd != "default":
            file_test = FILE.objects.filter(fichier=bdd)
            if not file_test:
                file = FILE(fichier=bdd)
                file.save()
    for file in FILE.objects.all():
        if not file.fichier in settings.DATABASES:
            file.delete()
    if request.user.is_staff or request.user.is_superuser:
        liste = FILE.objects.all()
    else:
        liste = [d.file for d in Droit.objects.filter(utilisateur_autorise=request.user)]
    print(liste)
    return render(request, 'Liste_FILE.html', {'liste_file': liste})
