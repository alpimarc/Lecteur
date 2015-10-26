'''
Created on 13 Jan. 2011

@author: Alpimarc
'''

from django import template

register = template.Library()

@register.filter(name='nombre')
def nombre(values):
    values=list(values)[1:]
    for i in range(len(values)):
        values[i]=sous_nombre(values[i])
    return values

@register.filter(name='sous_nombre')
def sous_nombre(value):
    import decimal
    if isinstance(value, float) or isinstance(value,decimal.Decimal):
        value=str(value).replace('.',',')
    if value is None:
        value = ""
    if isinstance(value, str) and "<b>" in value:
        value=value.replace("<b>","").replace("</b>","")
    return value

@register.filter(name='sous_nombre_inverse')
def sous_nombre_inverse(value):
    import decimal
    if isinstance(value, float) or isinstance(value,decimal.Decimal):
        value=str(value).replace(',','.')
    return value

@register.filter(name='texte')
def texte(values):
    import decimal
    values=list(values)
    for i in range(len(values)):
        values[i]=sous_texte(values[i])
    return values
	
@register.filter(name='sous_texte')
def sous_texte(value):
    import decimal
    if isinstance(value, str):
        value='"'+value.replace('"',"'")+'"'
    return value

@register.filter(name='sous_formatRapport')
def sous_formatRapport(value):
    import decimal
    if value is None:
        value='"N/A"'
    elif isinstance(value, str):
        value=value.replace('"',"'").replace("\n","</br>").replace("\\","\\\\")
        if len(value)<2:
            value='"'+value[1:-1]+'"'
        elif value[0]=="'" and value[-1]=="'":
            value='"'+value[1:-1]+'"'
        elif value[0]!='"' or value[-1]!='"':
            value='"'+value+'"'
    return value

@register.filter(name='formatRapport')
def formatRapport(values):
    import decimal
    values=list(values)
    for i in range(len(values)):
        values[i]=sous_formatRapport(values[i])
    return values