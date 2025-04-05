from django.shortcuts import render,redirect
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from . import models
import re
from decimal import Decimal
from chat.models import Room, Message
from django.db.models import Sum
from .forms import *

# Logics
def separate_comma(to_array):
    return [item.strip() for item in re.split(r'[, \n]+', to_array) if item.strip()]

def separate_newline(to_array):
    return [item.strip() for item in to_array.split("\n")]

def getMessage(request):
    last_message = Message.objects.order_by('room', '-timestamp').distinct('room')[:3]
    result = []
    for message in last_message:
        room = Room.objects.get(id=message.room.id)
        receiver = room.user1 if request.user != room.user1 else room.user2
        result.append({
            'message':message,
            'receiver':receiver
        })
        
    return result
# Create your views here.
def index(request):
    chats = getMessage(request)
    print(chats)
    return render(request, 'organizer/index.html', {'chats':chats})

def packages(request):
    package = models.Package.objects.all().order_by('-id')
    all_service_price = models.Services.objects.aggregate(total=Sum('service_price'))['total']
    return render(request, 'organizer/packages.html', {'packages': package, 'service_price':all_service_price})

def services(request):
    return render(request, 'organizer/services.html')
    
def update_package(request, id):
    if request.method == 'POST':
        package = models.Package.objects.get(id=id)
        package.package_name = request.POST['update_package_name']
        package.package_price = Decimal(request.POST['update_package_price'])
        package.package_downpayment = package.package_price * Decimal('0.2')
        package.package_inclusion = separate_comma(request.POST['update_package_inclusion'])
        package.save()
        messages.success(request, "Package updated successfully!")
        
    else:
        pass
    return redirect('organizer:packages')

def delete_package(request, id):
    package = models.Package.objects.get(id=id)
    package.delete()
    messages.success(request, "Package deleted successfully!")
    return redirect('organizer:packages')

def bookings(requst):
    return render(requst, 'organizer/bookings.html')

def confrim_payments(request):
    return render(request, 'organizer/pending-payments.html')

def payment_history(request):
    return render(request, 'organizer/payment-history.html')

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
    
    if request.method == "POST":
        project_form = ProjectForm(request.POST, request.FILES) 
        award_form = AwardForm(request.POST, request.FILES)
        faq_form = FAQForm(request.POST)
        
        if 'save_project' in request.POST and project_form.is_valid():
            messages.success(request, "Project added succesfully.")
            project_form.save()
            return redirect('organizer:system-settings')
        
        if 'save_award' in request.POST and award_form.is_valid():
            messages.success(request, "Award added succesfully.")
            award_form.save()
            return redirect('organizer:system-settings')
        
        if 'save_faq' in request.POST and faq_form.is_valid():
            messages.success(request, "Faq Added succesfully.")        
            faq_form.save()
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
            messages.success(request, "Successfully updated about section." if not created else "About section created successfully.")

    return redirect('organizer:system-settings')

def activity_logs(request):
    return render(request, 'organizer/activity-logs.html')