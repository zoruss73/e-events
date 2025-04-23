from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.contrib.auth import login, logout, authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import check_password
#Email activation link imports
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
# end of email
from .forms import RegistrationForm, LoginForm, BookingForm
from django.contrib import messages
from .tokens import account_activation_token
from django.urls import reverse
from django.contrib.auth.models import User
import random, json
from datetime import date
from decimal import Decimal
from organizer.models import Hero, About, Project, Awards, Faq
from django.contrib.auth.hashers import make_password
from organizer.models import Package, Services
from .models import Booking, Payment, BookedService, UserProfile
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
# Paypal
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from chat.models import Room, Message
from django.db.models import Count
from django.utils import timezone
from django.db.models import Prefetch
# Create your views here.

def notifyOrganizer(request, booking):
    organizer_user = User.objects.filter(is_staff=True, is_superuser=False).first()
    
    if organizer_user:
        message = f"You received a new booking from {request.user.username}!"

        # Send email notification (optional)
        mail_subject_user = "Booking Confirmed"
        email_message_user = render_to_string("template_user_message.html", {
            "client": request.user,
            "booking": booking,
        })

        mail_subject = "You received a new booking!"
        email_message = render_to_string("template_organizer_message.html", {
            "client": request.user,
            "organizer": organizer_user,
        })
        email_user = EmailMessage(mail_subject_user, email_message_user, to=[request.user.email])
        email = EmailMessage(mail_subject, email_message, to=[organizer_user.email])
        if email.send() and email_user.send():
            messages.success(request, "Booking confirmed successfully!")
        else:
            messages.success(request, "Booking email did not send")
            
def getMessage(request):
    room = Room.objects.get(user1=request.user)
    if room:
        message = Message.objects.filter(room=room).order_by('-timestamp').first()    
        if message:
            receiver = room.user2 if request.user == room.user1 else room.user1
            if receiver:
                return {'message':message, 'receiver':receiver} 
    
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        
        staff_user = User.objects.filter(is_staff=True, is_superuser=False).first()
        
        if staff_user:
            room_exists = Room.objects.filter(user1=user, user2=staff_user).exists() or \
                          Room.objects.filter(user1=staff_user, user2=user).exists()
                          
            if not room_exists:
                Room.objects.create(user1=user, user2=staff_user)
        
        messages.success(request, 'Your email has been verified. You can now log in to your account.')
        return redirect('user:login')
    else:
        messages.error(request, 'Activation link is invalid or already expired.')
    return redirect('user:login')

def activateEmail(request, user):
    mail_subject = "Activate your user account"
    message = render_to_string("template_activate_account.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    if email.send():
        messages.success(request, 'Please check your email and click the activation link to activate your account.')
    else:
        messages.error(request, 'Error sending email, please check you email inputted if you typed it correctly.')
        
def sendOTPEmail(request, user_email):
    otp = str(random.randint(100000, 999999))
    request.session['otp'] = otp
    request.session['email'] = user_email
    request.session.set_expiry(300)

    mail_subject = "This is your OTP Code to reset your password"
    message = f"""
        Your One-Time Password (OTP) is {otp}
        OTP will expire in 5 minutes.
        Do not share it with anyone.
        If you did not request this, please disregard this email.
    """
    
    email = EmailMessage(mail_subject, message, to=[user_email])

    if email.send():
        messages.success(request, 'OTP has been sent successfully.')
    
def landing_page(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('organizer:dashboard')
    elif request.user.is_authenticated:
        return redirect('user:dashboard')
    hero = Hero.objects.first()
    about = About.objects.first()
    projects = Project.objects.order_by('-id')
    package = Package.objects.all()
    awards = Awards.objects.order_by('-id')
    faq = Faq.objects.order_by('-id')
    
    context = {
        'hero':hero, 
        'about':about, 
        'projects':projects, 
        'packages':package,
        'awards':awards,
        'faqs':faq
        }
    return render(request, 'user/landing_page.html', context)

def log_in(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('organizer:dashboard')
        else:
            return redirect('user:dashboard')
    
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            try:
                user = User.objects.get(email=email)

                if not user.is_active:
                    # ✅ Send activation email if the user exists but is inactive
                    print("skibidi")
                    activateEmail(request, user)
                    messages.info(request, "Your account is not yet activated. A new activation link has been sent to your email.")
                    return redirect("user:login")  # Redirect to prevent resending on refresh

                authenticated_user = authenticate(username=user.username, password=password)
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    request.session.set_expiry(1209600)

                    if authenticated_user.is_staff:
                        return redirect(reverse("organizer:dashboard"))
                    else:
                        return redirect("user:dashboard")

            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
                return redirect("user:login")  # Redirect to prevent resending on refresh

        for error in form.errors.values():
            for message in error:
                messages.error(request, message)

    else:
        form = LoginForm()

    return render(request, "user/log_in.html", {"form": form})

def log_out(request):
    logout(request)
    return redirect('user:landingpage')

def register(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('organizer:dashboard')
        else:
            return redirect('user:dashboard')
    
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user)
            return redirect('user:login')
    else:
        form = RegistrationForm()
    return render(request, 'user/register.html', {'form': form})

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("user_email")

        if User.objects.filter(email=email).exists():
            sendOTPEmail(request, email)
            return redirect('user:confirmotp')
        else:
            messages.error(request, "Invalid email or not registered on the website.")
    
    return render (request, 'user/forgot_password.html')

def confirm_otp (request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp_number')
        stored_otp = request.session.get('otp')
        user_email = request.session.get('email')
        if stored_otp and entered_otp:
            if stored_otp == entered_otp:
                del request.session['otp']
                messages.success(request, 'OTP match')
                request.session['verified_email'] = user_email
                return redirect('user:newpassword')
            else:
                messages.error(request, "Invalid OTP.")
    return render(request, 'user/confirm_otp.html')

def new_password(request):
    verified_email = request.session.get('verified_email')
    
    if not verified_email:
        messages.error(request, "Sorry! You don't have access here.")
        return redirect('user:landingpage')
    
    user_obj = User.objects.get(email=verified_email)

    if request.method == "POST":
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")

        if pass1 == pass2:
            user_obj.password = make_password(pass1)
            user_obj.save()
            messages.success(request, "Password reset successfully. You can login now.")
            return redirect('user:login')
        else:
            messages.error(request, "Passwords do not match")

    return render(request,'user/new_password.html')

def dashboard(request):
    if request.user.is_authenticated:
        today = timezone.now().date()
        bookings = Booking.objects.filter(user=request.user, payment_status="pending").first()
        bookings_count = Booking.objects.filter(user=request.user).count()
        services_count = Services.objects.all().count()
        upcoming_event = Booking.objects.filter(wedding_date__gte=today, user=request.user).order_by('wedding_date').first()
        booked_service_counts = BookedService.objects.values('service_name').annotate(total_booked=Count('id'))
        chats = getMessage(request)
        days_left = (upcoming_event.wedding_date - today).days if upcoming_event else None
        print(days_left, "days left.")
        
        context = {
            'bookings': bookings, 
            'bookings_count':bookings_count, 
            'message': chats,
            'services_count': services_count,
            'service_stats': json.dumps(list(booked_service_counts)),
            'days_left': days_left
            }
        return render(request, 'user/dashboard.html', context)
    return redirect('user:landingpage')

def booking(request):
    if request.user.is_authenticated:
        chats = getMessage(request)
        bookings = Booking.objects.filter(user=request.user).prefetch_related(
            Prefetch('booked_services', queryset=BookedService.objects.all())
        ).order_by('-booking_date')

        print(bookings)
        return render(request, 'user/booking.html',{'bookings':bookings, 'message': chats} )
        
        
    return redirect('user:landingpage')

def create_booking(request):
    if request.user.is_authenticated:
        booked_dates = [date.strftime("%Y-%m-%d") for date in Booking.objects.values_list('wedding_date', flat=True)]
        services = Services.objects.all()   
        print("Booked dates: ",booked_dates)
        chats = getMessage(request)
        if request.method == "POST":
            form = BookingForm(request.POST)
            if form.is_valid():
                booking_data = form.cleaned_data       
                print(booking_data)
                package = booking_data['package']
                services = booking_data['services']
                print(package.package_name.lower())
                if package.package_name.lower() == "all-in-one package":
                    services = Services.objects.all()
                
                booking_data['package'] = package.package_name
                booking_data['username'] = request.user.username
                booking_data['wedding_date'] = booking_data['wedding_date'].strftime("%Y-%m-%d")
                booking_data['services'] = [(service.service_name) for service in services]
                booking_data['service_price'] = float(sum(service.service_price for service in services))
                booking_data['booking_downpayment'] = float(booking_data['service_price'] * 0.2)
                print(booking_data)
                request.session['booking_data'] = booking_data
                return redirect('user:proceed-to-payment')
        else:
            form = BookingForm()
        return render(request, 'user/create_booking.html', {'form':form, 'booked_dates':booked_dates, 'services':services, 'message': chats})

    return redirect('user:landingpage')

def proceed_to_payment(request):
    chats = getMessage(request)
    booking_data = request.session.get('booking_data')
    print(booking_data)
    host = request.get_host()
    print(booking_data['package'])
    invoice_id = uuid.uuid4()
    booking_id = uuid.uuid4()
    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': booking_data['booking_downpayment'],
        'package_name':booking_data['package'],
        'invoice': invoice_id,
        'currency_code': 'PHP',
        'notify_url': f"https://{host}{reverse('paypal-ipn')}",
        'return_url': f"https://{host}{reverse('user:booking-confirmation')}?booking_id={booking_id}&tx={invoice_id}",
        'cancel_url': f"https://{host}{reverse('user:dashboard')}",
        
    }
    
    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
    
    return render(request, 'user/proceed_to_payment.html', {'booking_data': booking_data, 'paypal':paypal_payment, 'message': chats})

def booking_confirmed(request):
    booking_id = request.GET.get('booking_id')
    txn_id = request.GET.get('tx')
    
    if not booking_id or not txn_id:
        return redirect('user:dashboard')
    
    booking_data = request.session.get('booking_data')
    print(booking_data, "booking id: ", booking_id, "txn_id: ", txn_id)
    
    if booking_data:
        try:
            package = Package.objects.get(package_name=booking_data['package'])
            services = Services.objects.filter(service_name__in=booking_data['services'])
            
            booking = Booking.objects.create(
                booking_id=booking_id,
                user=request.user, 
                wedding_date=booking_data['wedding_date'],
                is_confirmed = True,
                package=package,
                package_price=booking_data['service_price'],
                payment_status = "pending",
                remaining_balance = booking_data['service_price'] - booking_data['booking_downpayment']
            )
            
            for service in services:
                BookedService.objects.create(
                    booking=booking,
                    service_name=service.service_name,
                    service_price=service.service_price
            )
             
            payment = Payment.objects.create(
                    booking=booking,
                    user=request.user,
                    transaction_id=txn_id,
                    status="successful",
                    amount_paid=booking_data['booking_downpayment'],
            )
            payment.save()

            notifyOrganizer(request, booking)
            del request.session['booking_data']

        except Exception as e:
            messages.error(request, f"Error saving booking: {str(e)}")
            return redirect('user:dashboard')
    else:
        messages.error(request, "araw ko po")
        
    
    return redirect('user:booking')

def payment_history(request):
    payment = Payment.objects.filter(user=request.user)
    chats = getMessage(request)
    
    return render(request, 'user/payment_history.html', {'payments':payment, 'message': chats})

def accounts_settings(request):
    user = request.user
    chats = getMessage(request)
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        image = request.FILES.get('image_input_1')
        
        user.first_name = first_name
        user.last_name = last_name
        

        user_profile, created = UserProfile.objects.get_or_create(user=user)
        if image:
            user_profile.profile_img = image
            user_profile.save()
            
        user.save()
        messages.success(request, "Account updated succesfully.")
        return redirect('user:account-settings')
        
    return render(request, 'user/account_settings.html', {'message':chats})

def user_change_password(request):
    user = request.user
    error_old_password = None
    error_new_password = None
    error_confirm_password = None
    chats = getMessage(request)
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not check_password(old_password, user.password):
            error_old_password = "Your old password was entered incorrectly. Please enter it again."
        elif confirm_password !=  new_password:
            error_confirm_password = "Password does not match"
        else:
            try:
                validate_password(new_password, user)
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated succesfully.")
                return redirect('user:account-settings')
            except ValidationError as e:
                error_new_password = e.messages
    
    print(error_new_password, error_old_password)
    
    context = {
        'error_old_password':error_old_password, 
        'error_new_password':error_new_password,
        'error_confirm_password':error_confirm_password,
        'message':chats,
        }
    return render(request, 'user/change_password.html', context)
            



