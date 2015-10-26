#-*- coding: utf-8 -*-
'''
Created on 28 Dec. 2010

@author: Alpimarc
'''

from django import forms

class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)