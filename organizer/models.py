from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.html import mark_safe
from decimal import Decimal
# Create your models here.

class Services(models.Model):
    service_name = models.CharField(max_length=150, unique=True)
    service_price = models.DecimalField(max_digits=8, decimal_places=2)

    
    def __str__(self):
        return f"{self.service_name}"

class Package(models.Model):
    PACKAGE_TYPES = [
        ('fixed', 'Fixed'),
        ('custom', 'Custom'),
    ]

    package_name = models.CharField(max_length=150, unique=True)
    package_type = models.CharField(max_length=10, choices=PACKAGE_TYPES, default='Fixed')
    services = models.ManyToManyField(Services, blank=True)
        
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
    project_name = models.CharField(max_length=150,)
    description = models.TextField(null=True, blank=True)
    img = models.ImageField(upload_to="projects/")
    # alt = models.CharField(default="project_img")

    def __str__(self):
        return self.project_name
    
    def image_tag(self):
        return mark_safe('<img src="%s" width="80" />' % (self.img.url))

class Awards(models.Model):
    award_name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    img = models.ImageField(upload_to="awards/")
    # alt = models.CharField(max_length=100)
    
    def __str__(self):
        return self.award_name
    
    def image_tag(self):
        return mark_safe('<img src="%s" width="80" />' % (self.img.url))

class Faq(models.Model):
    question = models.CharField(max_length=250)
    answer = models.TextField()

    def __str__(self):
        return self.question
    