from django.db import models
from django.core.validators import MinValueValidator
# Create your models here.

class Manufacturer(models.Model):
     name = models.CharField(max_length=50)
     slug = models.CharField(unique=True,blank=True)
     country = models.CharField(max_length=50)
     website = models.CharField(max_length=50)
     description = models.TextField(max_length=500)
     def __str__(self):
          return f"{self.name}"


class Console(models.Model):
     name = models.CharField(max_length=50)
     slug = models.CharField(unique=True,blank=True)
     release_date= models.DateTimeField(auto_now=True)
     console_type = models.CharField(max_length=25)
     description = models.TextField(max_length=300)
     is_active = models.BooleanField(default=True)
     updated_at = models.DateTimeField(auto_now=True)
     manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE,related_name='consoles')
     generation = models.IntegerField(validators=[MinValueValidator(1)])
     
     def __str__(self):
          return f"{self.name}"
     
     