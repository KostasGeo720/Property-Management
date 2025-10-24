import uuid
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
REGULAR_CHOICES = [
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
]
COMPLEX_CHOICES = [
    ('apartment', 'Apartment'),
    ('studio', 'Studio'),
    ('co-op', 'Co-op'),
]
# Create your models here.

class BaseProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    address = models.CharField(max_length=200)
    property_size = models.CharField(max_length=50)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    parking_spaces = models.IntegerField()
    amenities = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=9, choices=[('available', 'Available'), ('rented', 'Rented')], default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Property(BaseProperty):
    property_type = models.CharField(max_length=30, choices=REGULAR_CHOICES)
    
    def __str__(self):
        return self.address
    
class PropertyComplex(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    address = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address
    
class Unit(BaseProperty):
    property_type = models.CharField(max_length=30, choices=COMPLEX_CHOICES)
    floor = models.IntegerField()
    number = models.IntegerField()
    complex = models.ForeignKey(PropertyComplex, on_delete=models.CASCADE, related_name='units', null=True, blank=True)
    nickname = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.nickname} - {self.complex.address}'

class Lease(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    property = models.ForeignKey(Property, null=True, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    tenant = models.ManyToManyField(User, blank=True, related_name='leases', limit_choices_to={'is_staff':False})
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
            x = self.property if self.property else self.unit
            msg_content = f'Lease for {x.address} has {due} months due (€{due*self.monthly_payment_amount} remaining).'
            identical = Message.objects.filter(
                owner=x.owner,
                lease=self,
                property=self.property,
                unit=self.unit,
                content=msg_content
            )
            if not identical.exists():
                Message.objects.create(
                    owner=x.owner,
                    lease=self,
                    property=self.property,
                    unit=self.unit,
                    content=msg_content
                )
                send_mail(
                    subject='Payment Due Notification',
                    message=msg_content,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[x.owner.email],
                    fail_silently=True,
                )
                for tenant in self.tenant.all():
                    Message.objects.create(
                        owner=tenant,
                        lease=self,
                        property=self.property,
                        unit=self.unit,
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
            x = self.property if self.property else self.unit
            Message.objects.create(
                owner=x.owner,
                property=self.property,
                unit=self.unit,
                lease=self,
                content=f'Payment of €{self.monthly_payment_amount * pay_months} received. {md} months still due.'
            )
            send_mail(
                subject=f'Payment Received Regarding Your Property {x.address}',
                message=f'Payment of €{self.monthly_payment_amount * pay_months} received. {md} months still due.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[x.owner.email],
                fail_silently=False,
            )
            return True
        else:
            return False
        
class Problem(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)  
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def delete(self, *args, **kwargs):
        Message.objects.create(
            owner=self.tenant,
            property=self.property,
            unit=self.unit,
            content=f'Problem described as: \n{self.description} \nhas been resolved.'
        )
        send_mail(
            subject='Problem Resolved Notification',
            message=f'Problem described as: \n{self.description} \nhas been resolved.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.tenant.email],
            fail_silently=True,
        )
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return f'{self.tenant}|{self.property}'

class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_messages')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, related_name='property_messages')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='unit_messages', null=True, blank=True)
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
    status = models.CharField(max_length=10, choices=[('verified', 'Verified'), ('unverified', 'Unverified')], default='verified')
    
    def verify(self):
        self.status = 'verified'
        for tenant in self.lease.tenant.all():
            Message.objects.create(
                owner=tenant,
                property=self.lease.property,
                unit=self.lease.unit,
                content=f'Document "{self.title}" has been verified.'
            )
            send_mail(
                subject='Document Verified Notification',
                message=f'Document "{self.title}" has been verified.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[tenant.email],
                fail_silently=True,
            )

    def __str__(self):
        return self.title if self.title else self.file.name

class Expense(models.Model):
    EXPENSE_CATEGORIES = [
        ('maintenance', 'Maintenance'),
        ('utilities', 'Utilities'),
        ('insurance', 'Insurance'),
        ('taxes', 'Property Taxes'),
        ('repairs', 'Repairs'),
        ('management', 'Property Management'),
        ('legal', 'Legal Fees'),
        ('advertising', 'Advertising'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name='expenses')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True, related_name='expenses')
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    receipt = models.FileField(upload_to='expense_receipts/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        location = self.property.address if self.property else f"{self.unit.nickname} - {self.unit.complex.address}"
        return f"{self.category.title()} - {location}: €{self.amount}"
    
    def get_owner(self):
        return self.property.owner if self.property else self.unit.owner