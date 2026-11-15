from django.contrib import admin
from django.utils.html import format_html
from consoles import models


class ConsoleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "manufacturer", "release_year", "generation", "image_preview"]
    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        if obj.image:
            thumb = obj.image.url.replace("/upload/", "/upload/w_100,h_75,c_fill,f_auto/")
            return format_html('<img src="{}" style="border-radius: 6px;" />', thumb)
        return "No image"


        

class ManufacturerAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "country", "founded_in", "logo_preview"]
    readonly_fields = ["logo_preview"]

    def logo_preview(self, obj):
        if obj.logo:
            thumb = obj.logo.url.replace("/upload/", "/upload/h_40,f_auto/")
            return format_html('<img src="{}" />', thumb)
        return "No logo"


admin.site.register(models.Console, ConsoleAdmin)
admin.site.register(models.Manufacturer, ManufacturerAdmin)