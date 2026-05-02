from django.contrib import admin
from .models import Staff, Operator, Availability

admin.site.register(Staff)
admin.site.register(Operator)
admin.site.register(Availability)
