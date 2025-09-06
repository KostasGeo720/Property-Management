from django.contrib import admin
from .models import Property, Lease, Problem
# Register your models here.
admin.site.register(Property)
admin.site.register(Lease)
admin.site.register(Problem)