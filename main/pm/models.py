from django.db import models
from django.utils import timezone
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
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    parking_spaces = models.IntegerField()
    amenities = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=9, choices=[('available', 'Available'), ('rented', 'Rented')])  # Add a status field with choices
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
        
    def __str__(self):
        return f'{self.address}'
        
class Lease(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ManyToManyField(User, blank=True, related_name='leases', limit_choices_to={'is_staff':False})  # Add a tennant field with a related name
    start_date = models.DateField()
    end_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    monthly_payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_payment_status = models.CharField(max_length=10, default='Pending', choices=[('pending', 'Pending'), ('paid', 'Paid')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    months_due = 0
    remaining_months = 0

    def calculate_remaining_months(self):
        today = timezone.now().date()
        delta = (self.end_date.year - today.year) * 12 + self.end_date.month - today.month
        self.remaining_months = delta
        self.save()
        return self.remaining_months
    
    def update_payment_status(self):
        
        self.calculate_remaining_months()
        
        if self.remaining_months*self.monthly_payment_amount <= self.amount_paid:
            self.monthly_payment_status = 'paid'
            self.months_due = 0
            self.save()
            return True
        
        if timezone.now().day > int(self.start_date.day):
            if self.monthly_payment_status=='paid':
                self.monthly_payment_status = 'pending'
                self.save()
            else:
                self.months_due += 1
                Message.objects.create(
                    owner=self.property.owner,
                    property=self.property,
                    content=f'Monthly payment of ${self.monthly_payment_amount} is overdue ({self.months_due} months due). Please take action.'
                )
                self.save()
        elif timezone.now().day == int(self.start_date.day):
            if self.monthly_payment_status == 'pending' and self.months_due > 0:
                Message.objects.create(
                    owner=self.property.owner,
                    property=self.property,
                    content=f'Monthly payment of ${self.monthly_payment_amount} is still overdue ({self.months_due} months due). Please take action.'
                )
                self.save()
                
    
    def pay(self):
        if self.monthly_payment_status == 'pending':
            self.amount_paid += self.monthly_payment_amount
            self.monthly_payment_status = 'paid'
            if self.months_due > 0:
                self.months_due -= 1
            Message.objects.create(
                owner=self.property.owner,
                property=self.property,
                content=f'Payment of ${self.monthly_payment_amount} received. {self.months_due} months still due.')
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
    
    def __str__(self):
        return f'{self.tenant}|{self.property}'

class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_messages')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Message regarding {self.property} at {self.timestamp}'

class Payment(models.Model):
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=32, choices=[
        ('stripe', 'Stripe'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ])
    payment_reference = models.CharField(max_length=255, blank=True)
    receipt_url = models.URLField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payment for Lease {self.lease.id}: {self.amount}"