from django.shortcuts import render,redirect
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from . import models
import re
from decimal import Decimal

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
    if request.method == "POST":
        package_name = request.POST.get('package_name')
        package_price = request.POST.get('package_price')
        package_inclusion = separate_comma(request.POST.get('package_inclusion'))
        
        package = models.Package(package_name=package_name, package_price=package_price, package_inclusion=package_inclusion)
        package.save()
        messages.success(request, "Package addedd successfully!")
        
        return redirect('organizer:packages')
    else:
        return render(request, 'organizer/packages.html', {'packages': package})
    
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

def update_hero(request):
    hero = models.Hero.objects.first()
    
    if request.method == "POST":
        hero_text = request.POST.get('hero_text')
        hero_description = request.POST.get('hero_description')
        
        if hero_text == hero.hero_text and hero_description == hero.hero_description:
            messages.info(request, "No changes detected")
        else:
            messages.success(request, "Successfully updated hero section.")
            hero.hero_text = hero_text
            hero.hero_description = hero_description
            hero.save()
        
    return redirect('organizer:system-settings')

def update_about(request):
    about = models.About.objects.first()
    
    if request.method == "POST":
        description = request.POST.get('about_description')
        img = request.FILES.get('image_input')
        print(img)
        if description == about.description and (img is None or img == about.img):
            messages.info(request, "No changes detected")
        else:
            messages.success(request, "Successfully updated about section.")
            if img:
                about.img = img
            about.description = description
            about.save()
    return redirect('organizer:system-settings')

def activity_logs(request):
    return render(request, 'organizer/activity-logs.html')