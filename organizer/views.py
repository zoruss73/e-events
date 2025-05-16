from calendar import month_name
from django.forms import ValidationError
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages 
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.db.models.functions import TruncMonth
from django.db.models import Prefetch
from . import models
import re
from decimal import Decimal
from chat.models import Room, Message
from django.utils.timezone import now
from django.db.models import Sum
from .forms import *
from user.models import Booking, Payment, UserProfile, BookedService
from django.db.models import Count
import json
from django.core.paginator import Paginator
from django.db.models import Max
from django.contrib.auth.models import User
import datetime
# Logics
def separate_comma(to_array):
    return [item.strip() for item in re.split(r'[, \n]+', to_array) if item.strip()]

def separate_newline(to_array):
    return [item.strip() for item in to_array.split("\n")]

def activity_logs_view(request, activity, description):
    models.ActivityLogs.objects.create(
        user=request.user,
        activity=activity,
        description=description
    )

def getMessage(request):
   
    latest_messages_per_room = (
        Message.objects.values('room')
        .annotate(latest_timestamp=Max('timestamp'))
        .order_by('-latest_timestamp')[:3]  # Top 3 latest rooms
    )

    result = []

    for item in latest_messages_per_room:
        
        message = Message.objects.get(room_id=item['room'], timestamp=item['latest_timestamp'])
        room = message.room
        receiver = room.user1 if request.user != room.user1 else room.user2

        result.append({
            'message': message,
            'receiver': receiver
        })

    return result

def index(request):
    chats = getMessage(request)
    current_year = now().year
    logs = models.ActivityLogs.objects.all().order_by('-id')[:10]
    bookings = Booking.objects.filter(wedding_date__gte=now().date())
    bookings_count = Booking.objects.all().count()
    services_count = models.Services.objects.all().count()
    user_count = User.objects.filter(is_staff=False, is_superuser=False).count()
    booked_service_counts = BookedService.objects.values('service_name').annotate(total_booked=Count('id'))
    weddings = (Booking.objects
        .filter(wedding_date__year=current_year)
        .annotate(month=TruncMonth('wedding_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    wedding_dict = {entry['month'].strftime('%B'): entry['count'] for entry in weddings}
    year = now().year
    months = [month_name[m] for m in range(1, 13)]
    filled_wedding_stats = [
        {
            "month": f"{month} {year}",
            "count": wedding_dict.get(month, 0)
        }
        for month in months
    ]
    events = []
    for booking in bookings:
        events.append({
            "title": f"Wedding: {booking.user.get_full_name()}",
            "start": booking.wedding_date.isoformat(),
            "allDay": True,
            "id": booking.booking_id,
        })
        
    context = {
        'chats':chats, 
        'logs':logs,
        'events': json.dumps(events),
        'bookings_count': bookings_count,
        'services_count':services_count,
        'user_count':user_count,
        'service_stats': json.dumps(list(booked_service_counts)),
        'wedding_stats':json.dumps(filled_wedding_stats)
        }
    return render(request, 'organizer/index.html',context )

def packages(request):
    package = models.Package.objects.all().order_by('-id')
    all_service_price = models.Services.objects.aggregate(total=Sum('service_price'))['total']
    return render(request, 'organizer/packages.html', {'packages': package, 'service_price':all_service_price})

def services(request):
    services = models.Services.objects.order_by('-id')
    chats = getMessage(request)
    if request.method == "POST":
        service_form = ServiceForm(request.POST)
        if service_form.is_valid():
            service_form.save()
            activity_logs_view(request, "Add", "Added new service.")
            messages.success(request, "Service added succesfully.")
            return redirect('organizer:services')
    else:
        service_form = ServiceForm()
        
    context = {
        'serviceform':service_form,
        'services':services,
        'chats':chats,
    }
    return render(request, 'organizer/services.html', context)

def update_service(request, id):
    service = get_object_or_404(models.Services, id=id)
    
    if request.method == "POST":
        service_form = ServiceForm(request.POST, instance=service)
        if service_form.is_valid():
            service_form.save()
            activity_logs_view(request, "Update", f"Updated {service.service_name}")
            
            messages.success(request, "Service updated succesfully.")
            return redirect('organizer:services')
    
def delete_service(request, id):
    service = models.Services.objects.get(id=id)
    service_name = service.service_name
    if service.delete():
        messages.success(request, "Service deleted succesfully.")
        activity_logs_view(request, "Delete", f"Deleted {service_name}")
        
    else:
        messages.error(request, "Failed to delete service.")
    
    return redirect('organizer:services')

def bookings(request):
    bookings = Booking.objects.filter(is_completed=False).prefetch_related(
        Prefetch('booked_services', queryset=BookedService.objects.all())
    ).order_by('-booking_date')
    today = datetime.date.today()
    print(today)
    return render(request, 'organizer/bookings.html',{"bookings":bookings, 'today':today})

def update_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    booking.is_completed = True
    booking.save()
    messages.success(request, "Updated successfully")
    return redirect('organizer:bookings')

def confrim_payments(request):
    return render(request, 'organizer/pending-payments.html')

def payment_history(request):
    payments = Payment.objects.all().order_by('-id')
    chats = getMessage(request)
    return render(request, 'organizer/payment-history.html', {'payments':payments, 'chats':chats})

def manage_clients(request):
    return render(request, 'organizer/clients.html')

def manage_suppliers(request):
    return render(request, 'organizer/suppliers.html')

def system_settings(request):
    hero = models.Hero.objects.first()
    about = models.About.objects.first()
    projects = models.Project.objects.order_by('-id')
    awards = models.Awards.objects.order_by('-id')
    faqs = models.Faq.objects.order_by('-id')
    chats = getMessage(request)
    if request.method == "POST":
        project_form = ProjectForm(request.POST, request.FILES) 
        award_form = AwardForm(request.POST, request.FILES)
        faq_form = FAQForm(request.POST)
        
        if 'save_project' in request.POST and project_form.is_valid():
            messages.success(request, "Project added succesfully.")
            if project_form.save():
                activity_logs_view(request, "Add", "Added new project.")
                return redirect('organizer:system-settings')
        
        if 'save_award' in request.POST and award_form.is_valid():
            messages.success(request, "Award added succesfully.")
            if award_form.save():
                activity_logs_view(request, "Add", "Added new award.")
            return redirect('organizer:system-settings')
        
        if 'save_faq' in request.POST and faq_form.is_valid():
            messages.success(request, "Faq Added succesfully.")        
            if faq_form.save():
                activity_logs_view(request, "Add", "Added new faq.")
            return redirect('organizer:system-settings')
            
    else:
        project_form = ProjectForm()
        award_form = AwardForm()
        faq_form = FAQForm()
    
    context = {
        'hero':hero, 
        'about':about, 
        'projects':projects,
        'awards': awards,
        'faqs':faqs,
        'faqform':faq_form,
        'awardform': award_form,
        'projectform':project_form,
        'chats':chats,
    }
    return render(request, 'organizer/system_settings.html', context)

def update_hero(request):
    hero, created = models.Hero.objects.get_or_create(id=1)

    if request.method == "POST":
        hero_text = request.POST.get('hero_text', '').strip()
        hero_description = request.POST.get('hero_description', '').strip()

        if not created and hero_text == hero.hero_text and hero_description == hero.hero_description:
            messages.info(request, "No changes detected.")
        else:
            hero.hero_text = hero_text
            hero.hero_description = hero_description
            activity_logs_view(request, "Update", "Update hero section.")
            hero.save()
            messages.success(request, "Successfully updated hero section." if not created else "Hero section created successfully.")

    return redirect('organizer:system-settings')

def update_about(request):
    about, created = models.About.objects.get_or_create(id=1)

    if request.method == "POST":
        description = request.POST.get('about_description', '').strip()
        img = request.FILES.get('image_input')

        if not created and description == about.description and (img is None or img == about.img):
            messages.info(request, "No changes detected.")
        else:
            if img:
                about.img = img
            about.description = description
            about.save()
            activity_logs_view(request, "Update", "Update about section.")
            messages.success(request, "Successfully updated about section." if not created else "About section created successfully.")

    return redirect('organizer:system-settings')

def update_award(request, id):
    award = get_object_or_404(models.Awards, id=id)
    if request.method == "POST":
        form  = AwardForm(request.POST, request.FILES, instance=award)
        if form.is_valid():
            if form.save():
                 activity_logs_view(request, "Update", f"Updated {award.award_name}")
            messages.success(request, "Award updated succesfully!")
    return redirect('organizer:system-settings')

def delete_award(request, id):
    award = models.Awards.objects.get(id=id)
    
    award_name = award.award_name
    if award.delete():
        activity_logs_view(request, "Delete", f"Deleted {award_name}")      
        messages.success(request, "Award deleted succesfully!")
    else:
        messages.error(request, "Failed to delete award")
        
    return redirect('organizer:system-settings')

def update_faq(request, id):
    faq = get_object_or_404(models.Faq, id=id)
    if request.method == "POST":
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            if form.save():
                activity_logs_view(request, "Update", f"Updated {faq.question}")      
                messages.success(request, "FAQ updated succesfully!")
        else:
            messages.error(request, "failed")
            
    return redirect('organizer:system-settings')

def delete_faq(request, id):
    faq = models.Faq.objects.get(id=id)
    faq_question = faq.question
    if faq.delete():
        activity_logs_view(request, "Delete", f"Deleted {faq_question}")      
        messages.success(request, "FAQ deleted succesfully!")
    else:
        messages.error(request, "Failed to delete FAQ")
    
    return redirect('organizer:system-settings')

def activity_logs(request):
    activity_logs = models.ActivityLogs.objects.all().order_by('-created_at')
    paginator = Paginator(activity_logs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    chats = getMessage(request)
    
    return render(request, 'organizer/activity-logs.html', {'page_obj': page_obj, 'chats':chats})

def profile(request):
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
        activity_logs_view(request, "Update", f"Updated the organizer details")
        messages.success(request, "Account updated succesfully.")
        return redirect('organizer:profile')
    
    return render(request, 'organizer/profile.html', {'chats':chats})

def change_password(request):
    chats = getMessage(request)
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
                activity_logs_view(request, "Update", f"Updated the organizer password")
                return redirect('organizer:profile')
            except ValidationError as e:
                error_new_password = e.messages
    
    print(error_new_password, error_old_password)
    
    context = {
        'error_old_password':error_old_password, 
        'error_new_password':error_new_password,
        'error_confirm_password':error_confirm_password,
        'chats':chats,
        }
    return render(request, 'organizer/change_password.html', context)