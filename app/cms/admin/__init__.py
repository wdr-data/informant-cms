from django.contrib import admin
from .report import *
from .push import *
from .genre import *
from .attachment import *
from .faq import *
from .wiki import *
from .tag import *
from .profile import *

admin.site.site_header = 'Informant'
admin.site.site_title = 'Informant'
admin.site.index_title = 'Home'
