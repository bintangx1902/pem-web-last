from django.contrib.admin import site
from .models import *

site.register(UserProfile)
site.register(Tools)
site.register(TechnicianJob)
site.register(GroundReport)
