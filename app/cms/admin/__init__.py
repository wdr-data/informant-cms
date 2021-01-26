from django.contrib import admin
from .report import *
from .push_compact import *
from .genre import *
from .attachment import *
from .faq import *
from .wiki import *
from .tag import *
from .profile import *
from .subtype import *

admin.site.site_header = "STAGING | Django WDR aktuell"
admin.site.site_title = "STAGING | Django WDR aktuell"
admin.site.index_title = "Home"
