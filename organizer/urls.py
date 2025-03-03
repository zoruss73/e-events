from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = "organizer"

urlpatterns = [
    path('dashboard/', views.index, name="dashboard"),
    path('packages/', views.packages, name="packages"),
    path('update-package/<int:id>/', views.update_package, name="update-package"),
    path('delete-package/<int:id>/', views.delete_package, name="delete-package"),
    path('bookings/', views.bookings, name="bookings"),
    path('confirm-payments/', views.confrim_payments, name="confirm-payments"),
    path('payment-history/', views.payment_history, name="payment-history"),
    path('clients/', views.manage_clients, name="clients"),
    path('suppliers/', views.manage_suppliers, name="suppliers"),
    
    path('system-settings/', views.system_settings, name="system-settings"),
    path('system-settings/update-hero', views.update_hero, name="update-hero"),
    path('system-settings/update-about', views.update_about, name="update-about"),
    
    
    path('activity-logs/', views.activity_logs, name="activity-logs"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
