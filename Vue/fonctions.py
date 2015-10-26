#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
Created on 28 Dec. 2010

@author: Alpimarc
'''

from django.db import connections
from django.http import HttpResponse
from Utilisateurs.models import FILE, Droit
from django.contrib.auth.decorators import login_required
import re

# mon décorateur qui vérifie les autorisations d'accès à un FILE
def autorisation(fonction):
  @login_required
  def wrap(request, id_file, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
             return fonction(request, id_file, *args, **kwargs)
        else:
            try:
                droit = Droit.objects.get(file=FILE.objects.get(fichier=id_file), utilisateur_autorise=request.user)
            except FILE.DoesNotExist as err:
                return HttpResponse('FILE inexistant', status=404)
            except Droit.DoesNotExist as err:
                return HttpResponse('Page non autorisée', status=401)
            if 'id_test' in kwargs:
                control = requeteSQL("SELECT Control FROM rapport WHERE id={id_test}".format(id_test=kwargs['id_test']), id_file).fetchone()[0]
                if control[0] not in droit.profil:
                    return HttpResponse('Page non autorisée', status=401)
            elif 'id_table' in kwargs:
                id_rapport = requeteSQL("SELECT ID_rapport FROM tablesresultats WHERE id={id_table}".format(id_table=kwargs['id_table']), id_file)
                control = requeteSQL("SELECT Control FROM rapport WHERE id={id_rapport}".format(id_rapport=id_rapport), id_file)
                if control[0] not in droit.profil:
                    return HttpResponse('Page non autorisée', status=401)
            return fonction(request, id_file, *args, **kwargs)

  wrap.__doc__ = fonction.__doc__
  wrap.__name__ = fonction.__name__
  return wrap

# mon décorateur qui vérifie que l'utilisateur est un superuser
def superuser(fonction):
  @autorisation
  def wrap(request, id_file, *args, **kwargs):
        if request.user.is_superuser:
            return fonction(request, id_file, *args, **kwargs)
        else:
            return HttpResponse('Page non autorisée', status=401)
  wrap.__doc__ = fonction.__doc__
  wrap.__name__ = fonction.__name__
  return wrap
  
def sql2json(requete, id_file, addID=False):
    import collections,json
    curseur=requeteSQL(requete, id_file)
    rows=curseur.fetchall()
    entetes=getEntetes(curseur)
    l=[]
    ligne=1
    for row in rows:
        d=collections.OrderedDict()
        if addID and not "id" in entetes:
            d["id"]=ligne
            ligne+=1
        for i in range(len(row)):
            d[entetes[i]]=row[i]
        l.append(d)
    return json.dumps(l)

def splitSqlite(id_file):
    def split(expr, delimiteur):
        if expr.startswith(delimiteur):
            return ""
        else:
            return expr.lstrip().split(delimiteur)[0]+"%"
    connections[id_file].connection.create_function("SPLITSQLITE", 2, split)
    
def rmplregexpSqlite(id_file):
    def rmplregexp(item, matching_expr, rmpl_expr):
        reg = re.compile(matching_expr)
        return reg.sub(rmpl_expr, item)
    connections[id_file].connection.create_function("RMPLREGEXP", 3, rmplregexp)

def requeteSQL(requete, id_file):
    if "SPLITSQLITE" in requete.upper():
        splitSqlite(id_file)
    if "RMPLREGEXP" in requete.upper():
        rmplregexpSqlite(id_file)
    curseur = connections[id_file].cursor()
    return curseur.execute(requete)
    
def sql2curseur(requete, id_file, inverse=False, graphique=False, limit=""):
    curseur = requeteSQL(requete, id_file)
    entetes=getEntetes(curseur)
    if not graphique :
        entetesTypes = getEntetesEtTypeFromTable(requete, id_file)
    else:
        entetesTypes = []
        if inverse:
            curseur=curseur.fetchall()
            curseur.insert(0,entetes)
            curseur=[list(liste) for liste in zip(*curseur)]
            entetes=curseur[0]
            curseur=curseur[1:]
            if limit != "":
                if "OFFSET " in limit.upper():
                    monOffset=int(limit.upper().split("OFFSET ")[1].split(" ")[0])
                else:
                    monOffset=0
                if "LIMIT " in limit.upper():
                    maLimite=int(limit.upper().split("LIMIT ")[1].split(" ")[0])
                    curseur=curseur[monOffset:monOffset+maLimite]
                else:
                    curseur=curseur[monOffset:]
            else:
                curseur=curseur[offset:]
            
    return curseur, entetesTypes, entetes #curseur et entete

def getEntetes(curseur):
    return [field[0] for field in curseur.description]

def getNomTable(requete):
    for reg in [".*from '([a-zA-Z_.0-9\- éèà&]+)'.*", ".*from ([a-zA-Z0-9\-_&]+) .*", ".*from ([a-zA-Z0-9\-_&]+)"]:
        if re.search(reg, requete, flags=re.IGNORECASE):
            return re.sub(reg, "\\1", requete, flags=re.IGNORECASE)

def getEntetesEtTypeFromTable(table, id_file):
    requete = table
    if " FROM " in table.upper():
        table = getNomTable(table)
    curseur = requeteSQL("Pragma table_info ('"+table+"')", id_file)

    if " FROM " in requete.upper() and not "*" in requete:
        entetesTypestmp = {}
        for (_, entete, type, _, _, _) in curseur:
            monType = "text"
            if type.startswith("DEC"):
                monType = "float"
            elif type == "INT":
                monType = "checkbox"
            entetesTypestmp[entete.upper()] = monType
        reg1=re.compile(" FROM ", re.IGNORECASE)
        reg2=re.compile("SELECT ", re.IGNORECASE)
        reg2.split(reg1.split(requete)[0])[1]
        champs = reg2.split(reg1.split(requete)[0])[1].replace("t1.","").split(",")
        entetesTypes = []
        for champ in champs:
            reg = re.compile(" as ", re.IGNORECASE)
            tmp = reg.split(champ)
            if len(tmp)==2:
                entetesTypes.append((tmp[1].replace(" ","").replace('"',''), entetesTypestmp[tmp[0].replace(" ","").replace('"','').upper()]))
            else:
                entetesTypes.append((tmp[0].replace(" ","").replace('"',''), entetesTypestmp[tmp[0].replace(" ","").replace('"','').upper()]))
    else:
        entetesTypes = []
        for (_, entete, type, _, _, _) in curseur:
            monType = "text"
            if type.startswith("DEC"):
                monType = "float"
            elif type == "INT":
                monType = "checkbox"
            entetesTypes.append((entete, monType))
    return entetesTypes
    
def requete2liste(requete, id_file, inverse=False):
    curseur, entetesTypes, entetes = sql2curseur(requete, id_file, inverse)
    r = [[(entetes[i], value) for i, value in enumerate(row)] for row in curseur]
    return r, entetesTypes

def renderForceDownload(template, context):
    from django.http import HttpResponse
    from django.template import Context, loader
    
    t = loader.get_template(template)
    c = Context(context)
    return HttpResponse(t.render(c), content_type="application/force-download")
