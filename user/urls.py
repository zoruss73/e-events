from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "user"

urlpatterns = [
    path('', views.landing_page, name="landingpage"),
    path('login/', views.log_in, name="login"),
    path('logout/', views.log_out, name="logout"),
    path('register/', views.register, name="register"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('forgot_password', views.forgot_password, name="forgotpassword"),
    path('confirm_otp', views.confirm_otp, name="confirmotp"),
    path('new_password/', views.new_password, name="newpassword"),
    path('user/dashboard/', views.dashboard, name="dashboard"),

    path('user/booking/', views.booking, name="booking"),
    path('user/booking/create-booking/', views.create_booking, name="create-booking"),
    path('user/booking/create-booking/proceed-to-payment', views.proceed_to_payment, name="proceed-to-payment"),
    path('user/booking-confirmation/', views.booking_confirmed, name='booking-confirmation'),
    
    path('user/payment-history', views.payment_history, name="payment-history"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
