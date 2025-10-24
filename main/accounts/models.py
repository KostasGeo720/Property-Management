from django.db import models
from django.contrib.auth.models import User

class Landlord(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_profile')

    def __str__(self):
        return f"Landlord: {self.user.username}"

class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    landlord = models.ForeignKey(Landlord, related_name='tenants', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Tenant: {self.user.username}"