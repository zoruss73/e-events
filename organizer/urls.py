from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = "organizer"

urlpatterns = [
    path('dashboard/', views.index, name="dashboard"),
    
    path('packages/', views.packages, name="packages"),
    path('services/', views.services, name="services"),
    path('update-service/<int:id>/', views.update_service, name="update-service"),
    path('delete-service/<int:id>/', views.delete_service, name="delete-service"),
    path('update-faq/<int:id>/', views.update_faq, name="update-faq"),
    path('delete-faq/<int:id>/', views.delete_faq, name="delete-faq"),
    
    
    path('bookings/', views.bookings, name="bookings"),
    path('bookings/<int:id>/', views.update_booking, name="update-booking"),
    path('confirm-payments/', views.confrim_payments, name="confirm-payments"),
    path('payment-history/', views.payment_history, name="payment-history"),
    path('clients/', views.manage_clients, name="clients"),
    path('suppliers/', views.manage_suppliers, name="suppliers"),
    
    path('system-settings/', views.system_settings, name="system-settings"),
    path('system-settings/update-hero', views.update_hero, name="update-hero"),
    path('system-settings/update-about', views.update_about, name="update-about"),
    path('system-settings/update-awards/<int:id>/', views.update_award, name="update-award"),
    path('system-settings/delete-awards/<int:id>/', views.delete_award, name="delete-award"),
    
    path('activity-logs/', views.activity_logs, name="activity-logs"),
    path('profile/', views.profile, name="profile"),
    path('profile/change-password/', views.change_password, name="change-password"),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
