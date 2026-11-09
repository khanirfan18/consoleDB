from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from consoles import models

     
class ConsoleSerializer(ModelSerializer):
     manufacturer = serializers.SlugRelatedField(
          queryset=models.Manufacturer.objects.all(),
          slug_field="slug"
     )

     
     class Meta:
          exclude = ['slug']
          model = models.Console 
           
class ManufacturerSerializer(ModelSerializer):
     consoles = serializers.StringRelatedField(many=True, read_only=True)
     class Meta:
          fields = "__all__"
          model = models.Manufacturer
   
