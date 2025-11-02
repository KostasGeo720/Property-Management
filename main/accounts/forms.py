from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Landlord, Tenant

class LandlordCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Όνομα χρήστη',
            'email': 'Ηλεκτρονικό ταχυδρομείο',
            'password1': 'Κωδικός',
            'password2': 'Επιβεβαίωση Κωδικού',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = True  # mark as landlord
        if commit:
            user.save()
            Landlord.objects.create(user=user)
        return user

class TenantCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    landlord = forms.ModelChoiceField(queryset=Landlord.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'landlord']
        labels = {
            'username': 'Όνομα χρήστη',
            'email': 'Ηλεκτρονικό ταχυδρομείο',
            'password1': 'Κωδικός',
            'password2': 'Επιβεβαίωση Κωδικού',
            'landlord': 'Ιδιοκτήτης',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = False
        if commit:
            user.save()
            Tenant.objects.create(user=user, landlord=self.cleaned_data['landlord'])
        return user