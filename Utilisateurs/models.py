# -*-coding:utf-8 -*-
'''
Created on 28 Dec. 2010

@author: Alpimarc
'''

from django.contrib.auth.models import User
from django.db import models

class FILE(models.Model):

    fichier = models.CharField(max_length=100, 
                               null=False, 
                               blank=False)

    date_creation = models.DateTimeField(verbose_name="Date de création", #u"Date de création",
                                         auto_now=False,
                                         auto_now_add=True)

    utilisateurs_autorises = models.ManyToManyField(User, through='Droit')
    
    class Meta:
        unique_together = ('fichier', 'date_creation')

    def __unicode__(self):
        return u"%(fichier)s %(date_creation)s" % {'fichier': self.fichier, 
                                                   'date_creation': self.date_creation}

    def __str__(self): 
        return self.__unicode__()
        
class Droit(models.Model):
    
    profil = models.CharField(max_length=100, null=False, blank=False)
    
    file = models.ForeignKey(FILE)
    
    utilisateur_autorise = models.ForeignKey(User)

    class Meta:
        unique_together = ('file', 'utilisateur_autorise')
        
    def __unicode__(self):
        return u"%(file)s %(utilisateur_autorise)s" % {'file': self.file, 
                                                      'utilisateur_autorise': self.utilisateur_autorise}

    def __str__(self): 
        return self.__unicode__()