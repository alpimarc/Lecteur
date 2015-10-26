'''
Created on 28 Dec. 2010

@author: Alpimarc
'''

#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from Vue import fonctions
from Vue.fonctions_views import filtreRequete, filtreEntetesTypes, recherche, sous_json, determinePageEtLigne, filtreDrilldown
from Utilisateurs.models import FILE, Droit
from django.conf import settings

@fonctions.autorisation
@cache_page(60*settings.DELAI_DU_CACHE)
def json(request, id_file, id_test, id_tableResultat):
    requete="SELECT tableresultat, nb FROM tablesresultats where id_rapport='"+id_test+"' AND id='"+id_tableResultat+"'"
    (tableResultat,nb,)=fonctions.requeteSQL(requete, id_file).fetchone()
    requete="SELECT * FROM '"+tableResultat+"'"
    return sous_json(request, id_file, requete, nb, url="&"+"?".join(request.get_full_path().split("?")[1:]))

@fonctions.autorisation
@cache_page(60*settings.DELAI_DU_CACHE)
def rapport_json(request, id_file):
    if request.user.is_staff or request.user.is_superuser:
        profil = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    else:
        profil = Droit.objects.get(file=FILE.objects.get(fichier=id_file), utilisateur_autorise=request.user).profil
    requete="SELECT * FROM Rapport WHERE Result!='NA' AND result!='OK' AND SUBSTR(Control,1,1) IN ('" + "', '".join(list(profil)) +"')"
    return sous_json(request, id_file, requete)

@fonctions.autorisation
@cache_page(60*settings.DELAI_DU_CACHE)
def critere_json(request, id_file, id_table, id_ligne):
    requete = filtreDrilldown(id_file, id_table, id_ligne, request) 
    return sous_json(request, id_file, requete)
  
@fonctions.autorisation
@cache_page(60*settings.DELAI_DU_CACHE)
def rapport(request, id_file):
    _, entetesTypes=fonctions.requete2liste("SELECT * FROM Rapport LIMIT 1", id_file, False)
    entetesTypes = filtreEntetesTypes(request, entetesTypes)
    if request.user.is_staff or request.user.is_superuser:
        profil = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    else:
        profil = Droit.objects.get(file=FILE.objects.get(fichier=id_file), utilisateur_autorise=request.user).profil
    requete="SELECT COUNT(*) FROM Rapport WHERE Result!='NA' AND result!='OK' AND SUBSTR(Control,1,1) IN ('" + "', '".join(list(profil)) +"')"
    (nb_lignes,) = fonctions.requeteSQL(requete, id_file).fetchone()
    return render(request, 'rapport.html',{'entetesTypes':entetesTypes, 'nb_lignes_par_page':nb_lignes})

@fonctions.autorisation
@cache_page(60*settings.DELAI_DU_CACHE)
def control(request, id_file, id_test=0):
    requete="SELECT control, comment, result, risque, description, typologie, loi FROM rapport where id='"+id_test+"' AND Result!='NA' AND result!='OK'"
    try:
        (control, comment, result, risque, description, typologie, loi)=fonctions.requeteSQL(requete, id_file).fetchone()
    except:
        return HttpResponse('Control inexistant', status=404)
    requete="SELECT id, type, inverse, titre, requete, nb_lignes FROM tablesgraphiques where id_rapport='"+id_test+"'"
    tablesGraphiques=[]
    for (id, type, inverse, titre, requeteGraphique, nb_lignes,) in fonctions.requeteSQL(requete, id_file):
        nb_pages, _ = determinePageEtLigne(id_file, requete, "", settings.NB_LIGNES_PAR_PAGE_GRAPHIQUE, nb_lignes, inverse=inverse)
        tablesGraphiques.append((id, type, titre, nb_pages, inverse))

    requete="SELECT id, tableresultat FROM tablesresultats where id_rapport='"+id_test+"'"
    tablesResultats=[]
    for (id, tableResultat,) in fonctions.requeteSQL(requete, id_file):
        entetesTypes=filtreEntetesTypes(request, fonctions.getEntetesEtTypeFromTable(tableResultat, id_file))
        tablesResultats.append((id, tableResultat, entetesTypes))
        
    return render(request, 'control.html', {'id_test':id_test, 'control':control, 'tablesResultats':tablesResultats, 'tablesGraphiques':tablesGraphiques, 'comment':comment, 'result':result, 'risque':risque, 'description':description, 'typologie':typologie, 'loi':loi, 'nb_lignes_par_page':settings.NB_LIGNES_PAR_PAGE_TABLE, 'nb_items_par_page':settings.NB_LIGNES_PAR_PAGE_GRAPHIQUE})

@fonctions.autorisation
@cache_page(60*settings.DELAI_DU_CACHE)
def sidebar(request, id_file):
    if request.user.is_staff or request.user.is_superuser:
        profil = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    else:
        profil = Droit.objects.get(file=FILE.objects.get(fichier=id_file), utilisateur_autorise=request.user).profil
    requete="SELECT Type, control, nb, id FROM rapport, (select SUBSTR(control,1,1) as type, COUNT(1) as nb FROM rapport where result!='NA' AND result!='OK' AND SUBSTR(Control,1,1) IN ('" + "', '".join(list(profil)) + "') group by substr(control,1,1)) WHERE type=substr(rapport.control,1,1) and Result!='NA' AND result!='OK'"
    listeTables = fonctions.requeteSQL(requete, id_file)
    return render(request, 'sidebar.html', {'listeTables': listeTables})

@fonctions.autorisation
@cache_page(60*settings.DELAI_DU_CACHE)
def graphique_json(request, id_file, id_test, id_tableGraphique):
    requete = "SELECT requete, inverse, nb_lignes FROM tablesGraphiques where id_rapport='"+id_test+"' AND id='"+id_tableGraphique+"'"
    import re
    (requete, inverse, nb_lignes) = fonctions.requeteSQL(requete, id_file).fetchone()
    requete = re.sub(", ",", id, ", requete, 1, re.IGNORECASE)
    filtre, tri, limit, nb_lignes_par_page, num_page = recherche(request, requete, graphique=True)
    if inverse:
        nb_pages, _ = determinePageEtLigne(id_file, requete, filtre, nb_lignes_par_page, nb_lignes=nb_lignes)
    else:
        nb_pages, _ = determinePageEtLigne(id_file, requete, filtre, nb_lignes_par_page, nb_lignes="")
    if inverse:
        requete=requete+filtre+tri
    else:
        requete=requete+filtre+tri+limit
    curseur, entetesTypes, entetes = fonctions.sql2curseur(requete, id_file, inverse, graphique=True, limit=limit)
    return render(request, 'graphique_json.html', {'curseur':curseur, 'entetes': entetes, 'nb_pages':nb_pages, 'num_page':num_page})

@fonctions.autorisation
@cache_page(60*settings.DELAI_DU_CACHE)
def view_csv(request, id_file, id_tableResultat):
    requete="SELECT tableResultat FROM tablesResultats WHERE id="+id_tableResultat
    (tableResultat,)=fonctions.requeteSQL(requete, id_file).fetchone()

    inverse=True
    if not (tableResultat.endswith("AvecEtSansTVAEnNB") or tableResultat.endswith("AvecEtSansTVAEnMontant") or tableResultat.endswith("MvtAvecEtSansTVAEnMontant") or tableResultat.endswith("MvtAvecEtSansTVAEnNB")):
        inverse=False

    requete = filtreRequete(request, "SELECT * FROM '"+tableResultat+"'", id_file)
    print("r", requete)
    filtre, tri, limit, nb_lignes_par_page, _ = recherche(request, requete)
    curseur, entetesTypes, entete=fonctions.sql2curseur(requete+filtre+tri, id_file, inverse)

    return fonctions.renderForceDownload('export.csv', {'curseur':curseur, 'entete':entete})

@fonctions.autorisation
@cache_page(60*settings.DELAI_DU_CACHE)
def view_csv_critere(request, id_file, id_table, id_ligne):
    requete = filtreDrilldown(id_file, id_table, id_ligne, request)

    filtre, tri, limit, nb_lignes_par_page, _ = recherche(request, requete)
    curseur, entetesTypes, entete=fonctions.sql2curseur(requete+filtre+tri, id_file)

    return fonctions.renderForceDownload('export.csv', {'curseur':curseur, 'entete':entete})

@fonctions.autorisation
@cache_page(60*settings.DELAI_DU_CACHE)
def drilldown(request, id_file, id_table, id_ligne):
    print(id_ligne)
    if "graphique" in request.GET and "colonne" in request.GET:
        graphique = request.GET["graphique"]
        colonne = request.GET["colonne"]
    else:
        graphique = 0
        colonne = ""
    id_table_retour = '0'
    if id_table != '0':
        requete = "SELECT tableResultat FROM tablesResultats WHERE id="+id_table
        (tableResultat,) = fonctions.requeteSQL(requete, id_file).fetchone()
        entetes = fonctions.requeteSQL("Pragma table_info ('"+tableResultat+"')", id_file).fetchall()
        if "criteres" in [entete.lower() for (_, entete, _, _, _, _) in entetes]:
            curseur, entetesTypes = fonctions.requete2liste("SELECT id as id, CompteNum, CompteLib, Debit, Credit, Solde FROM 'BalanceGenerale.csv' LIMIT 1", id_file, False)
            
            (id_table_retour,) = fonctions.requeteSQL("SELECT id FROM tablesResultats WHERE tableResultat='BalanceGenerale.csv'", id_file).fetchone()
        else:
            curseur, entetesTypes = fonctions.requete2liste("SELECT id, JournalCode, JournalLib, EcritureNum, EcritureDate, CompteNum, CompteLib, CompAuxNum, CompAuxLib, PieceRef, PieceDate, EcritureLib, Debit, Credit, EcritureLet, DateLet, ValidDate, Montantdevise, Idevise, SchemaEcr, SchemaSimplifie, IntituleSchema, TypeSchema, ListCompAuxNum FROM TableAvecSchemas LIMIT 1", id_file, False)
    else:
        curseur, entetesTypes = fonctions.requete2liste("SELECT id, JournalCode, JournalLib, EcritureNum, EcritureDate, CompteNum, CompteLib, CompAuxNum, CompAuxLib, PieceRef, PieceDate, EcritureLib, Debit, Credit, EcritureLet, DateLet, ValidDate, Montantdevise, Idevise, SchemaEcr, SchemaSimplifie, IntituleSchema, TypeSchema, ListCompAuxNum FROM TableAvecSchemas LIMIT 1", id_file, False)
    entetesTypes = filtreEntetesTypes(request, entetesTypes)
    return render(request, 'drilldown.html',{'entetesTypes':entetesTypes, 'id_table': id_table, 'id_table_retour': id_table_retour, 'id_ligne': id_ligne, 'nb_lignes_par_page':50, "graphique":graphique, "colonne":colonne})