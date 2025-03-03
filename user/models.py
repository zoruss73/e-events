from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from organizer.models import Package
import  uuid
from django.utils.timezone import now
# Create your models here.



class Booking(models.Model):
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
    ]
    
    booking_id = models.CharField(max_length=100, unique=True, editable=False, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    wedding_date = models.DateField()
    is_confirmed = models.BooleanField(default=False)
    booking_date = models.DateTimeField(default=now)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    package_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'),('paid', 'Paid')], default="pending")
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)
    is_cancelled = models.BooleanField(default=False)
    
    def update_balance(self):
        total_paid = Payment.objects.filter(booking=self, status='successful').aggregate(models.Sum('amount_paid'))['amount_paid__sum'] or 0
        self.remaining_balance = Decimal(self.package_price) - Decimal(total_paid)
        self.payment_status = 'paid' if self.remaining_balance <= 0 else 'pending'
        self.save()
    

    def __str__(self):
        return f"{self.booking_id} - {self.user.username}"
    
    
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('successful', 'Successful')])
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateField(null=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'successful':
            self.booking.update_balance()
    
    def __str__(self):
        return f"{self.user.first_name} {self.status} - {self.amount_paid}"