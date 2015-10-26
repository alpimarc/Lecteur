Licence :

Ce logiciel est sous licence CeCILL-B

Pré-requis :
- Django,
- Django-password-policies
- Pygeoip
- Django-tracking (django tracking nécessite une version compilée de GeoIP. 
  Sous windows, pour simplifier, suivre les modifications ci-dessous)
      
Si GeoIP n'est pas trouvé lors de la création des bases :
- modifier dans PythonX.X\Lib\site-packages\django_tracking-X.egg\tracking\models.py:
       from django.contrib.gis.geoip import GeoIP, GeoIPException
  en (2 lignes) :
       from pygeoip import GeoIP
       from pygeoip import GeoIPError as GeoIPException
- modifier dans PythonX.X\Lib\site-packages\django_tracking-X.egg\tracking\middleware.py :
       ligne 63 :
		   user_agent = unicode(request.META.get('HTTP_USER_AGENT', '')[:255], errors='ignore')
       en :
	       user_agent = request.META.get('HTTP_USER_AGENT', '')[:255].encode("utf-8", errors='ignore')
