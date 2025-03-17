from django.shortcuts import render,redirect
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from . import models
import re
from decimal import Decimal
from django.db.models import Sum

# Logics
def separate_comma(to_array):
    return [item.strip() for item in re.split(r'[, \n]+', to_array) if item.strip()]

def separate_newline(to_array):
    return [item.strip() for item in to_array.split("\n")]
    
    
# Create your views here.
def index(request):
    return render(request, 'organizer/index.html')

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
    return render(request, 'organizer/system_settings.html', {'hero':hero, 'about':about, 'projects':projects})

from django.shortcuts import redirect
from django.contrib import messages
from . import models

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