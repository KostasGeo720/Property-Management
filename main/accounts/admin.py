from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import Landlord, Tenant
from .forms import LandlordCreationForm, TenantCreationForm

class LandlordAdmin(admin.ModelAdmin):
    add_form = LandlordCreationForm
    list_display = ['user']
    search_fields = ['user__username']
    ordering = ['user__username']

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return self.add_form
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            form.save()
        else:
            super().save_model(request, obj, form, change)

class TenantAdmin(admin.ModelAdmin):
    add_form = TenantCreationForm
    list_display = ['user', 'landlord']
    search_fields = ['user__username']
    ordering = ['user__username']

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return self.add_form
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            form.save()
        else:
            super().save_model(request, obj, form, change)

admin.site.register(Landlord, LandlordAdmin)
admin.site.register(Tenant, TenantAdmin)