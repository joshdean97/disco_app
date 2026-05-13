from django.contrib import admin
from .models import Site, Shift, ShiftRequest, Skill

admin.site.register(Site)
admin.site.register(Shift)
admin.site.register(ShiftRequest)
admin.site.register(Skill)
