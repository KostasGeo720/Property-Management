import uuid
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
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

class PropertyComplex(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    address = models.CharField(max_length=200)
    properties = models.ManyToManyField(Property, blank=True, related_name='complex')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address

class Lease(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ManyToManyField(User, blank=True, related_name='leases', limit_choices_to={'is_staff':False})  # Add a tennant field with a related name
    start_date = models.DateField()
    end_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    monthly_payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_payment_status = models.CharField(max_length=10, default='Pending', choices=[('pending', 'Pending'), ('paid', 'Paid')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def get_remaining_months(self):
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        delta = (self.end_date.year - today.year) * 12 + self.end_date.month - today.month
        # If the end day is before today, subtract one month
        if self.end_date.day < today.day:
            delta -= 1
        return max(delta, 0)

    def months_due(self):
        today = timezone.now().date()
        if today < self.start_date:
            return 0
        months_elapsed = (today.year - self.start_date.year) * 12 + today.month - self.start_date.month
        if today.day < self.start_date.day:
            months_elapsed -= 1
        total_due = months_elapsed * self.monthly_payment_amount
        months_due = int((total_due - self.amount_paid) // self.monthly_payment_amount)
        return max(months_due, 0)

    def notify_months_due(self):
        due = self.months_due()
        if due > 0:
            msg_content = f'Lease for {self.property.address} has {due} months due (€{due*self.monthly_payment_amount} remaining).'
            identical = Message.objects.filter(
                owner=self.property.owner,
                lease=self,
                property=self.property,
                content=msg_content
            )
            if not identical.exists():
                Message.objects.create(
                    owner=self.property.owner,
                    lease=self,
                    property=self.property,
                    content=msg_content
                )
                send_mail(
                    subject='Payment Due Notification',
                    message=msg_content,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[self.property.owner.email],
                    fail_silently=True,
                )
                for tenant in self.tenant.all():
                    Message.objects.create(
                        owner=tenant,
                        lease=self,
                        property=self.property,
                        content=msg_content
                    )
                    send_mail(
                        subject='Payment Due Notification',
                        message=msg_content,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[tenant.email],
                        fail_silently=True,
                    )
    def update_payment_status(self):
        # Update payment status based on months_due
        if self.months_due() > 0 and self.monthly_payment_status.lower() == 'paid':
            self.monthly_payment_status = 'pending'
            self.save()
        elif self.months_due() == 0 and self.monthly_payment_status.lower() == 'pending':
            self.monthly_payment_status = 'paid'
            self.save()
        self.notify_months_due()

    def pay(self, months=1):
        # Only allow payment if there are months due
        due = self.months_due()
        if due > 0 and months > 0:
            pay_months = min(months, due)
            self.amount_paid += self.monthly_payment_amount * pay_months
            self.save()
            self.update_payment_status()
            md = self.months_due()
            Message.objects.create(
                owner=self.property.owner,
                property=self.property,
                lease=self,
                content=f'Payment of €{self.monthly_payment_amount * pay_months} received. {md} months still due.'
            )
            send_mail(
                subject=f'Payment Received Regarding Your Property {self.property.address}',
                message=f'Payment of €{self.monthly_payment_amount * pay_months} received. {md} months still due.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[self.property.owner.email],
                fail_silently=False,
            )
            return True
        else:
            return False
        
class Problem(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)  
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.tenant}|{self.property}'

class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_messages')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_messages')
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='lease_messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Message regarding {self.property} at {self.timestamp}'
    
class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title if self.title else self.file.name
        
    


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