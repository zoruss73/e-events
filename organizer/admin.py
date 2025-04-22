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
    list_display = ('project_name', 'image_tag')
admin.site.register(models.Project, ProjectAdmin)

class AwardsAdmin(admin.ModelAdmin):
    list_display = ('award_name', 'image_tag')
admin.site.register(models.Awards, AwardsAdmin)

class FaqAdmin(admin.ModelAdmin):
    list_display = ('question', )
admin.site.register(models.Faq, FaqAdmin)

class ActivityLogsAdmin(admin.ModelAdmin):
    list_display = ('activity', 'created_at')
admin.site.register(models.ActivityLogs, ActivityLogsAdmin)