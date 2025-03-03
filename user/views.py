from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.contrib.auth import login, logout, authenticate, get_user_model
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
from organizer.models import Hero, About, Project
from django.contrib.auth.hashers import make_password
from organizer.models import Package
from .models import Booking, Payment
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

# Paypal
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid

# Create your views here.

def notifyOrganizer(request):
    organizer_user = User.objects.filter(is_staff=True, is_superuser=False).first()

    mail_subject = f"You received a new booking!"
    message = render_to_string("template_organizer_message.html", {
        'client': request.user,
        'organizer': organizer_user,
    })
    email = EmailMessage(mail_subject, message, to=[organizer_user.email])
    if email.send():
        messages.success(request, 'Booking confirmed successfully!')
    
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
        
        messages.success(request, 'Your email has been verified. You can now log in to your account.')
        return redirect('user:login')
    else:
        messages.error(request, 'Activation link is invalid')
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
    return render(request, 'user/landing_page.html', {'hero':hero, 'about':about, 'projects':projects, 'packages':package})

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
        bookings = Booking.objects.filter(user=request.user, payment_status="pending").first()
        bookings_count = Booking.objects.filter(user=request.user).count()
        
        print(bookings)
        return render(request, 'user/dashboard.html', {'bookings': bookings, 'bookings_count':bookings_count})
    return redirect('user:landingpage')


def booking(request):
    if request.user.is_authenticated:
        
        bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
        return render(request, 'user/booking.html',{'bookings':bookings} )
        
        
    return redirect('user:landingpage')

def create_booking(request):
    if request.user.is_authenticated:
        booked_dates = [date.strftime("%Y-%m-%d") for date in Booking.objects.values_list('wedding_date', flat=True)]
        print("Booked dates: ",booked_dates)
        if request.method == "POST":
            form = BookingForm(request.POST)
            
            if form.is_valid():
                booking_data = form.cleaned_data
                package = booking_data['package']
                booking_data['username'] = request.user.username
                booking_data['wedding_date'] = booking_data['wedding_date'].strftime("%Y-%m-%d")
                booking_data['package'] = {
                    'id': package.id,
                    'package_price': float(package.package_price),
                    'package_name' : package.package_name,
                    'package_downpayment': float(package.package_downpayment)
                }
                request.session['booking_data'] = booking_data
                return redirect('user:proceed-to-payment')
        else:
            form = BookingForm()
        return render(request, 'user/create_booking.html', {'form':form, 'booked_dates':booked_dates})

    return redirect('user:landingpage')

def proceed_to_payment(request):
    booking_data = request.session.get('booking_data')
    print(booking_data)
    host = request.get_host()
    print(booking_data['package']['package_name'])
    invoice_id = uuid.uuid4()
    booking_id = uuid.uuid4()
    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': booking_data['package']['package_downpayment'],
        'package_name':booking_data['package']['package_name'],
        'invoice': invoice_id,
        'currency_code': 'PHP',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('user:booking-confirmation')}?booking_id={booking_id}&tx={invoice_id}",
        'cancel_url': f"http://{host}{reverse('user:dashboard')}",
        
    }
    
    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
    
    return render(request, 'user/proceed_to_payment.html', {'booking_data': booking_data, 'paypal':paypal_payment})

def booking_confirmed(request):
    booking_id = request.GET.get('booking_id')
    txn_id = request.GET.get('tx')
    
    if not booking_id or not txn_id:
        return redirect('user:dashboard')
    
    booking_data = request.session.get('booking_data')
    print(booking_data, "booking id: ", booking_id, "txn_id: ", txn_id)
    
    if booking_data:
        try:
            package = Package.objects.get(id=booking_data['package']['id'])

            booking = Booking.objects.create(
                booking_id=booking_id,
                user=request.user, 
                wedding_date=booking_data['wedding_date'],
                package=package,
                package_price=booking_data['package']['package_price'],
                payment_status = "pending",
                remaining_balance = Decimal(booking_data['package']['package_price']) - Decimal(booking_data['package']['package_downpayment'])
            )
            booking.save()
            
            payment = Payment.objects.create(
                booking = booking,
                user = request.user,
                transaction_id = txn_id,
                amount_paid = booking_data['package']['package_downpayment'],
                status = "successful",
                payment_date = now()
            )
            payment.save()


            notifyOrganizer(request)
            del request.session['booking_data']

        except Exception as e:
            messages.error(request, f"Error saving booking: {str(e)}")
            return redirect('user:dashboard')
    else:
        messages.error(request, "araw ko po")
        
    
    return redirect('user:booking')

def payment_history(request):
    payment = Payment.objects.filter(user=request.user)
    return render(request, 'user/payment_history.html', {'payments':payment})
