from django import forms
from django.contrib.auth.models import User
from .models import Property, Lease, Problem, Document, PropertyComplex

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
            'status'
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

class NewProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = [
            'description',
            'property'
            ]
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        if tenant:
            leases = Lease.objects.filter(tenant=tenant)
            self.fields['property'].queryset = Property.objects.filter(lease__in=leases).distinct()

        
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
