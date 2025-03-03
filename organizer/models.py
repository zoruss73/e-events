from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.html import mark_safe
from decimal import Decimal
# Create your models here.

class Package(models.Model):
    PACKAGE_TYPES = [
        ('fixed', 'Fixed'),
        ('custom', 'Custom'),
    ]

    package_name = models.CharField(max_length=150, unique=True)
    package_type = models.CharField(max_length=10, choices=PACKAGE_TYPES, default='Fixed')
    package_price = models.DecimalField(max_digits=8, decimal_places=2)
    package_downpayment = models.DecimalField(max_digits=8, decimal_places=2)
    package_inclusion = ArrayField(models.CharField(max_length=150), null=True)
    
    def save(self, *args, **kwargs):
        if self.package_type == "Fixed":
            self.package_downpayment =  Decimal(self.package_price) * Decimal('0.2')
        
        super().save(*args, **kwargs)
        
        
    
    def __str__(self):
        return f"{self.package_name}"
    
    
class Hero(models.Model):
    hero_text = models.CharField(max_length=150)
    hero_description = models.TextField()

    def __str__(self):
        return self.hero_text
    

class About(models.Model):
    img = models.ImageField(upload_to="about_img/")
    description = models.TextField()
    
    def __str__(self):
        return self.description[:20]

    def image_tag(self):
        return mark_safe('<img src="%s" width="80" />' % (self.img.url))
    
class Project(models.Model):
    img = models.ImageField(upload_to="projects/")
    alt = models.CharField(default="project_img")

    def __str__(self):
        return self.alt
    
    def imga_tag(self):
        return mark_safe('<img src="%s" width="80" />' % (self.img.url))

    