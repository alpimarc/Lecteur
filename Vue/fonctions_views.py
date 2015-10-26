#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
Created on 28 Dec. 2010

@author: Alpimarc
'''

from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from Vue import fonctions
from Utilisateurs.models import FILE, Droit
from django.conf import settings

def filtreRequete(request, requete, id_file):
    import re
    if re.search("^select \* ",requete, flags=re.IGNORECASE):
        filtre_utilise = list(settings.FILTRE)
        entetes = ['"' + entete.replace('"','\"') + '"' for (_, entete, _, _, _, _) in fonctions.requeteSQL("Pragma table_info ('"+fonctions.getNomTable(requete)+"')", id_file).fetchall() if entete.lower() not in filtre_utilise]
        return re.sub("^select \* ", "SELECT " + ", ".join(entetes)+ " ", requete, flags=re.IGNORECASE)
    else:
        return requete

def filtreEntetesTypes(request, entetesTypes):
    filtre_utilise = list(settings.FILTRE)
    return [(entete, type) for (entete, type) in entetesTypes if entete.lower() not in filtre_utilise]

def recherche(request, requete_final, graphique=False):
    limit = ""
    nb_lignes_par_page=0
    num_page = 1
    if graphique:
        if "limit" in request.GET:
            limit += " LIMIT " + request.GET["limit"] + " "
            nb_lignes_par_page = int(request.GET["limit"])
            if "offset" in request.GET:
                limit += " OFFSET " + request.GET["offset"] + " "
                num_page = int((int(request.GET["offset"])-1)/nb_lignes_par_page + 1)
    else:
        if "rows" in request.GET:
            limit += " LIMIT " + request.GET["rows"] + " "
            nb_lignes_par_page=int(request.GET["rows"])
            if "page" in request.GET:
                limit += " OFFSET " + str((int(request.GET["page"])-1)*int(request.GET["rows"])) + " "
                num_page = int(request.GET["page"])
    tri = ""
    if 'sidx' in request.GET and request.GET['sidx'] != '' and 'sord' in request.GET:
        tri = " ORDER BY [" + request.GET['sidx'] + "] " + request.GET['sord']
    filtres = []
    filtre = ""
    operateurs_texte = {'eq': '[{}] =  "{}"',
                        'ne': '[{}] != "{}"',
                        'lt': '[{}] <  "{}"',
                        'le': '[{}] <= "{}"',
                        'gt': '[{}] >  "{}"',
                        'ge': '[{}] >= "{}"',
                        'bw': 'TRIM([{}]) LIKE "{}%"',
                        'bn': 'TRIM([{}]) NOT LIKE "{}%"',
                        'ew': 'TRIM([{}]) LIKE "%{}"',
                        'en': 'TRIM([{}]) NOT LIKE "%{}"',
                        'cn': '[{}] LIKE "%{}%"',
                        'nc': '[{}] NOT LIKE "%{}%"',
                        }
    operateurs_numerique = {'eq': '[{}] =  {}',
                            'ne': '[{}] != {}',
                            'lt': '[{}] <  {}',
                            'le': '[{}] <= {}',
                            'gt': '[{}] >  {}',
                            'ge': '[{}] >= {}',
                            'bw': 'TRIM([{}]) LIKE "{}%"',
                            'bn': 'TRIM([{}]) NOT LIKE "{}%"',
                            'ew': 'TRIM([{}]) LIKE "%{}"',
                            'en': 'TRIM([{}]) NOT LIKE "%{}"',
                            'cn': '[{}] LIKE "%{}%"',
                            'nc': '[{}] NOT LIKE "%{}%"',
                            }
    numeriques = ["montant", "total", "solde", "nb", "debit", "credit", "nombre"]
    if 'filters' in request.GET:
        d = {}
        exec("filters = "+request.GET['filters'], d)
        filters = d['filters']
        for i in filters['rules']:
            if i['data'] == "|":
                valeur = ""
            else:
                valeur = i['data']
            if all([i['field'].lower() not in numerique for numerique in numeriques]):
                filtres.append(operateurs_texte[i['op']].format(i['field'], valeur))
            else:
                filtres.append(operateurs_numerique[i['op']].format(i['field'], valeur))
        if len(filters['rules'])>0:
            if " WHERE " in requete_final.upper():
                filtre = " AND (" + (" " + filters["groupOp"] + " ").join(filtres) + ")"
            else:
                filtre = " WHERE " + (" " + filters["groupOp"] + " ").join(filtres)
    return filtre, tri, limit, nb_lignes_par_page, num_page
    
def sous_json(request, id_file, requete_final, nb="", url=""):
    requete_final = filtreRequete(request, requete_final, id_file)
    filtre, tri, limit, nb_lignes_par_page, _ = recherche(request, requete_final)
    requete=requete_final+filtre+tri+limit
    rows=fonctions.sql2json(requete, id_file)
    nb_pages, nb_lignes = determinePageEtLigne(id_file, requete_final, filtre, nb_lignes_par_page, nb)
    return render(request, 'json.html', {'nb_pages':nb_pages, 'nb_lignes': nb_lignes, 'curseur':rows, 'url':url})

def determinePageEtLigne(id_file, requete, filtre, nb_lignes_par_page, nb_lignes="", inverse=False):
    if filtre!="" or nb_lignes=="":
        import re
        reg=re.compile('^.*from ', re.IGNORECASE)
        requete="SELECT COUNT(*) FROM "+reg.sub("",requete, count=1)+filtre
        (nb_lignes,)=fonctions.requeteSQL(requete, id_file).fetchone()
    if nb_lignes_par_page:
        if int(nb_lignes/nb_lignes_par_page)==nb_lignes/nb_lignes_par_page:
            nb_pages = int(nb_lignes/nb_lignes_par_page)
        else:
            nb_pages = int(nb_lignes/nb_lignes_par_page)+1
    else:
        nb_pages = 1
    return nb_pages, nb_lignes

def filtreDrilldown(id_file, id_table, id_ligne, request):
    import re
    critere = ''
    champ_criteres = False
    if "graphique" in request.GET and "colonne" in request.GET:
        requete = "SELECT filtre_colonne FROM tablesGraphiques where id="+request.GET["graphique"]
        (filtre_colonne,) = fonctions.requeteSQL(requete, id_file).fetchone()
        filtre_colonne = eval(filtre_colonne)
        if request.GET["colonne"] in filtre_colonne:
            critere += "(" + filtre_colonne[request.GET["colonne"]] + ")"
            print(request.GET["colonne"], critere)
    if id_table == '0':
        tableResultat = "TableAvecSchemas"
        if critere == "()":
            critere == ""
        if critere != "":
            critere += " AND "
        critere += "t1.JournalCode = t2.JournalCode AND t1.EcritureNum = t2.EcritureNum"
        criteres = ""
    else:
        requete = "SELECT tableResultat, criteres FROM tablesResultats WHERE id="+id_table
        (tableResultat,criteres, ) = fonctions.requeteSQL(requete, id_file).fetchone()
        if criteres == "()":
            criteres = ""
        if criteres != "":
            criteres = " AND " + criteres
            listeChampsTableAvecSchemas = [entete for (_, entete, _, _, _, _) in fonctions.requeteSQL("Pragma table_info ('TableAvecSchemas')", id_file).fetchall()]
            for champ in listeChampsTableAvecSchemas:
                criteres = re.sub(champ, "t1."+champ, criteres, flags=re.IGNORECASE)
        
        entetesTypes = fonctions.getEntetesEtTypeFromTable(tableResultat, id_file)
        entetes=[]
        for i, _ in entetesTypes:
            entetes.append(i.lower())
        if critere == "()":
            critere = ""
        if critere != "":
            critere += " AND "
        if "journalcode" in entetes and "ecriturenum" in entetes:
            critere += "t1.JournalCode = t2.JournalCode AND t1.EcritureNum = t2.EcritureNum"
        elif "ecriturenum" in entetes:
            critere += "t1.EcritureNum = t2.EcritureNum"
        elif "comptenum" in entetes and "compauxnum" in entetes:
            critere += "t1.CompteNum = t2.CompteNum AND t1.CompAuxNum = t2.CompAuxNum"
        elif "comptenum" in entetes and "tiers" in entetes:
            critere += "t1.CompteNum = t2.CompteNum AND t1.CompAuxNum LIKE SPLITSQLITE(t2.tiers, ' - ')"
        elif "comptenum" in entetes:
            critere += "t1.CompteNum = t2.CompteNum"
        elif "compauxnum" in entetes and "pieceref" in entetes:
            critere += "t1.CompAuxNum = t2.CompAuxNum AND t1.PieceRef = t2.PieceRef"
        elif "compauxnum" in entetes:
            critere += "t1.CompAuxNum = t2.CompAuxNum"
        elif "tiers" in entetes:
            critere += "t1.CompAuxNum LIKE SPLITSQLITE(t2.tiers, ' - ')"
        elif "compte" in entetes:
            critere += "t1.CompteNum LIKE SPLITSQLITE(t2.Compte, ' ')"
        elif "journalcode" in entetes:
            critere += "t1.JournalCode = t2.JournalCode"
        elif "numero d ecriture precedent le trou de sequence" in entetes and "numero d ecriture suivant le trou de sequence" in entetes and "code Journal precedent" in entetes and "code Journal suivant" in entetes:
            critere += "((t1.JournalCode = t2.[Code Journal precedent] AND t1.EcritureNum = t2.[Numero d ecriture precedent le trou de sequence]) OR (t1.JournalCode = t2.[Code Journal suivant] AND t1.EcritureNum = t2.[Numero d ecriture suivant le trou de sequence]))"
        elif "numero d ecriture precedent le trou de sequence" in entetes and "numero d ecriture suivant le trou de sequence" in entetes:
            critere += "(t1.EcritureNum = t2.[Numero d ecriture precedent le trou de sequence] OR t1.EcritureNum = t2.[Numero d ecriture suivant le trou de sequence])"
        elif "criteres" in entetes:
            requete = "SELECT criteres FROM '" + tableResultat + "' WHERE id=" + id_ligne
            (crit,) = fonctions.requeteSQL(requete, id_file).fetchone()          
            if filtre_colonne[request.GET["colonne"]] == "":
                critere += "(" + crit + ")"
            
            champ_criteres = True
    requete = "SELECT t1.id, t1.JournalCode, t1.JournalLib, t1.EcritureNum, t1.EcritureDate, t1.CompteNum, t1.CompteLib, t1.CompAuxNum as compauxnum, t1.CompAuxLib as compauxlib, t1.PieceRef, t1.PieceDate, t1.EcritureLib, t1.Debit as debit, t1.Credit as credit, t1.EcritureLet, t1.DateLet, t1.ValidDate, t1.Montantdevise as montantdevise, t1.Idevise as idevise, t1.SchemaEcr as schemaecr, t1.SchemaSimplifie as schemasimplifie, t1.IntituleSchema as intituleschema, t1.TypeSchema as typeschema , t1.ListCompAuxNum as listcompauxnum FROM TableAvecSchemas t1"
    if id_ligne!='0':
        if champ_criteres:
            requete = requete.replace("t1","").replace(".","") + " WHERE ("+critere+") "
            requete = "SELECT id as id, CompteNum as comptenum, CompteLib as comptelib, Debit as debit, Credit as credit, Solde as solde FROM 'BalanceGenerale.csv' WHERE ("+critere+") "
        else:
            requete = requete + ", '{}' t2  WHERE t2.{} = {}".format(tableResultat, "id", id_ligne)+" AND ("+critere+")" + criteres
    print("requete", requete, criteres)
    return requete