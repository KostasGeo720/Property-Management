from django import forms
from django.contrib.auth.models import User
from .models import Property, Lease, Problem, Document, PropertyComplex, Unit, Expense
from accounts.models import Landlord, Tenant

class NewPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'address',
            'property_type',
            'property_size',
            'bedrooms',
            'bathrooms',
            'parking_spaces',
            'amenities',
            'description',
            ]
        
class NewUnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = [
            'floor',
            'number',
            'nickname',
            'property_type',
            'property_size',
            'bedrooms',
            'bathrooms',
            'parking_spaces',
            'amenities',
            'description',
            ]

class NewPropertyComplexForm(forms.ModelForm):
    class Meta:
        model = PropertyComplex
        fields = [
            'address'
            ]

class NewLeaseForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = [
            'tenant',
            'start_date',
            'end_date',
            'monthly_payment_amount'
        ]
        widgets = {
            'tenant': forms.CheckboxSelectMultiple(),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'})
        }
    
    def __init__(self, *args, **kwargs):
        landlord_user = kwargs.pop('landlord_user', None)
        super().__init__(*args, **kwargs)
        
        if landlord_user:
            # Get the landlord profile for the current user
            try:
                landlord = Landlord.objects.get(user=landlord_user)
                # Filter tenants to only show those assigned to this landlord
                tenant_users = User.objects.filter(
                    tenant_profile__landlord=landlord,
                    is_staff=False
                )
                self.fields['tenant'].queryset = tenant_users
            except Landlord.DoesNotExist:
                # If user is not a landlord, show no tenants
                self.fields['tenant'].queryset = User.objects.none()
        else:
            # Fallback to original behavior if no landlord_user provided
            self.fields['tenant'].queryset = User.objects.filter(is_staff=False)

class NewProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = [
            'description',
            'property',
            'unit'
            ]
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            leases = Lease.objects.filter(tenant=tenant)
            self.fields['property'].queryset = Property.objects.filter(lease__in=leases).distinct()
            self.fields['unit'].queryset = Unit.objects.filter(lease__in=leases).distinct()

        
class AddTenantForm(forms.ModelForm):
    tennant = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_staff=False),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = Lease
        fields = ['tennant']

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'accept': 'application/pdf'}),
        }

        
    def clean_file(self):
        file = self.cleaned_data['file']
        if file.content_type != 'application/pdf':
            raise forms.ValidationError("Only PDF files are allowed.")
        return file

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'category',
            'amount',
            'date',
            'receipt',
            'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }