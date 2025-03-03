from django.contrib import admin
from . import models
# Register your models here.

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user',)
admin.site.register(models.Booking, BookingAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'status', 'amount_paid')
admin.site.register(models.Payment, PaymentAdmin)