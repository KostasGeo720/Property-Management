from django import forms
from .models import Property, Lease, Problem

class NewPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'address',
            'property_type',
            'property_size',
            'price',
            'price_status',
            'rent_price',
            'rent_price_status',
            'bedrooms',
            'bathrooms',
            'parking_spaces',
            'amenities',
            'description',
            'status'
            ]
        
class NewLeaseForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = [
            'property',
            'tenant',
            'start_date',
            'end_date',
            'monthly_payment_amount'
            ]

class NewProblemForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))
    end_date = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))
    class Meta:
        model = Problem
        fields = [
            'property',
            'description'
            ]