from django.contrib import admin
from consoles import models
# Register your models here.

class ConsoleAdmin(admin.ModelAdmin):
     prepopulated_fields = {"slug":("name",)}
admin.site.register(models.Console, ConsoleAdmin)


class ManufacturerAdmin(admin.ModelAdmin):
     prepopulated_fields = {"slug":("name",)}
admin.site.register(models.Manufacturer, ManufacturerAdmin)


