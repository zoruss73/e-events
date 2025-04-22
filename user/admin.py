from django.contrib import admin
from . import models
# Register your models here.

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user',)
admin.site.register(models.Booking, BookingAdmin)

class BookedServicesAdmin(admin.ModelAdmin):
    list_display = ('booking',)
admin.site.register(models.BookedService, BookedServicesAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'status', 'amount_paid')
admin.site.register(models.Payment, PaymentAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'is_read', 'created_at')
admin.site.register(models.Notification, NotificationAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_img')
admin.site.register(models.UserProfile, UserProfileAdmin)