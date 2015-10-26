'''
Created on 28 Dec. 2010

@author: Alpimarc
'''

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_BDD = [r"c:\bdd"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'Phrase à générer'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# paramètres vue
NB_LIGNES_PAR_PAGE_TABLE = 50
NB_LIGNES_PAR_PAGE_GRAPHIQUE = 10
DELAI_DU_CACHE = 0
FILTRE = ["criteres", "risque", "description", "typologie", "loi", "criticite", "selection", "ponderation"] # supprimé des requetes


# Application definition

INSTALLED_APPS=(
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'password_policies',
    'Vue',
    'Utilisateurs',
    'tracking', # à mettre à la fin pour que le template base ne soit pas utiliser
)

# pour password_policies
SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer'
PASSWORD_USE_HISTORY = True
PASSWORD_HISTORY_COUNT = 10
PASSWORD_DURATION_SECONDS = 90 * 24 * 60**2 # 90 days

# pour tracking
GOOGLE_MAPS_KEY = None
TRACKING_USE_GEOIP = False

MIDDLEWARE_CLASSES = (
    'tracking.middleware.BannedIPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'password_policies.middleware.PasswordChangeMiddleware',
    'tracking.middleware.VisitorTrackingMiddleware',
)

ROOT_URLCONF = 'Lecteur.urls'

WSGI_APPLICATION = 'Lecteur.wsgi.application'


# Database
BASE_BDD = [base for base in BASE_BDD if os.path.isdir(base)]
DATABASES = {}
for base in BASE_BDD:
    listeBDD = [fichier for fichier in os.listdir(base) if fichier.endswith(".db3")]
    DATABASES.update({bdd:{'ENGINE':'django.db.backends.sqlite3', 'NAME': os.path.join(base, bdd)} for bdd in listeBDD})
DATABASES['default']= {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'sqlite.bdd'),
    }

TEMPLATE_CONTEXT_PROCESSORS = (
    "Vue.context.context_processors.global_var",
    'django.contrib.auth.context_processors.auth',
    'password_policies.context_processors.password_status',
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = (
  os.path.join(BASE_DIR, 'templates'),
)

APPEND_SLASH = True  # Ajoute un slash en fin d'URL

# Internationalization
LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'


# Additional locations of static files
STATICFILES_DIRS = ( BASE_DIR+"/static", )

CACHES = { 'default': { 'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache', 'LOCATION': BASE_DIR+"/Cache"}}

LOGIN_URL = '/Login/'
LOGIN_REDIRECT_URL = '/Login/'
