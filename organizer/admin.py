from django.contrib import admin
from . import models
# Register your models here.

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'service_price')
admin.site.register(models.Services, ServiceAdmin)

class PackageAdmin(admin.ModelAdmin):
    list_display = ('package_name', )
admin.site.register(models.Package, PackageAdmin)

class HeroAdmin(admin.ModelAdmin):
    list_display = ('hero_text',)
admin.site.register(models.Hero, HeroAdmin)

class AboutAdmin(admin.ModelAdmin):
    list_display = ('description', 'image_tag')
admin.site.register(models.About, AboutAdmin)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('img', 'alt')
admin.site.register(models.Project, ProjectAdmin)