from django.contrib import admin
from .models import Site, Shift, ShiftRequest

admin.site.register(Site)
admin.site.register(Shift)
admin.site.register(ShiftRequest)
