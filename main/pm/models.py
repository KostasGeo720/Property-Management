from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Property(models.Model):
    address = models.CharField(max_length=200)
    property_type = models.CharField(max_length=30, choices=[
        ('condo', 'Condo'),
        ('apartment', 'Apartment'),
        ('studio', 'Studio'),
        ('house', 'House'),
        ('townhouse', 'Townhouse'),
        ('bungalow', 'Bungalow'),
        ('co-op', 'Co-op'),
        ('loft', 'Loft'),
        ('barn', 'Barn'),
        ('shack', 'Shack'),
        ('cottage', 'Cottage'),
        ('parking' ,'Parking')
        ])
    property_size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_status = models.CharField(max_length=10, choices=[('negotiable', 'Negotiable'), ('fixed', 'Fixed')])
    rent_price = models.DecimalField(max_digits=10, decimal_places=2)
    rent_price_status = models.CharField(max_length=10, choices=[('negotiable', 'Negotiable'), ('fixed', 'Fixed')])
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    parking_spaces = models.IntegerField()
    amenities = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    tennant = models.ForeignKey(User, default=None, on_delete=models.CASCADE, related_name='rental_tennant')  # Add a tennant field with a related name
    status = models.CharField(max_length=50, default='Available', choices=[('available', 'Available'), ('sold', 'Sold'), ('rented', 'Rented')])  # Add a status field with choices
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def rent(self, tennant):
        if self.status == 'available':
            self.tennant = tennant
            self.status = 'rented'
            self.save()
            return True
        else:
            return False
        
class Lease(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    monthly_payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_payment_status = models.CharField(max_length=10, default='Pending', choices=[('pending', 'Pending'), ('paid', 'Paid')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def pay(self):
        if self.monthly_payment_status == 'pending':
            self.amount_paid += self.monthly_payment_amount
            self.monthly_payment_status = 'paid'
            self.save()
            return True
        else:
            return False
        
class Problem(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)