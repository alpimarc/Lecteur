'''
Created on 24 June 2011

@author: Alpimarc
'''

from django.conf import settings
from django.db import connections
from Vue import fonctions

def global_var(request):
    '''
    A context processor
    '''
    try:
        id_file="FILE_"+request.META['PATH_INFO'].split("/Vue/FILE_")[1].split(".db3/")[0]+".db3"
    except:
        id_file=""
    return {'id_file':id_file}

def ListeTables2(id_file):
	requete="SELECT Type, control, nb, id FROM rapport, (select SUBSTR(control,1,1) as type, COUNT(1) as nb FROM rapport where result!='NA' AND result!='OK' group by substr(control,1,1)) WHERE type=substr(rapport.control,1,1) and Result!='NA' AND result!='OK'"
	return fonctions.requeteSQL(requete, id_file)
	
def ListeTables(id_file):
	requete="SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
	listeTables=fonctions.requeteSQL(requete, id_file).fetchall()
	listeTables2=[]
	for (table,) in listeTables:
		if not table.endswith('_filtre') and table!="Rapport":
			listeTables2.append(table)
	return listeTables2
	
	