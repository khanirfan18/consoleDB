import cloudinary.uploader
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Manufacturer(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    country = models.CharField(max_length=50)
    website = models.URLField(max_length=200, blank=True)
    description = models.TextField(max_length=500)
    founded_in = models.IntegerField(
        validators=[MinValueValidator(1972), MaxValueValidator(2100)]
    )
    logo = models.ImageField(upload_to="manufacturers/logos/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Console(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    release_year = models.IntegerField(
        validators=[MinValueValidator(1972), MaxValueValidator(2100)]
    )
    console_type = models.CharField(max_length=25)
    description = models.TextField(max_length=300)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.CASCADE, related_name="consoles"
    )
    generation = models.IntegerField(validators=[MinValueValidator(1)])
    image = models.ImageField(upload_to="consoles/", blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ConsoleImage(models.Model):
    console = models.ForeignKey(
        Console, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="consoles/gallery/")
    caption = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # only one image per console is marked as primary
        if self.is_primary:
            ConsoleImage.objects.filter(
                console=self.console, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.console.name} - Image {self.id}"


# Cloudinary Cleanup Signals 

@receiver(post_delete, sender=ConsoleImage)
def delete_console_image_from_cloudinary(sender, instance, **kwargs):
    if instance.image:
        cloudinary.uploader.destroy(instance.image.name)


@receiver(post_delete, sender=Manufacturer)
def delete_manufacturer_logo_from_cloudinary(sender, instance, **kwargs):
    if instance.logo:
        cloudinary.uploader.destroy(instance.logo.name)


@receiver(pre_save, sender=Manufacturer)
def replace_old_manufacturer_logo(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_logo = Manufacturer.objects.get(pk=instance.pk).logo
    except Manufacturer.DoesNotExist:
        return
    if old_logo and old_logo != instance.logo:
        cloudinary.uploader.destroy(old_logo.name)