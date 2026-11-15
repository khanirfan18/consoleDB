from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from consoles import models


class ConsoleSerializer(ModelSerializer):
    manufacturer = serializers.SlugRelatedField(
        queryset=models.Manufacturer.objects.all(),
        slug_field="slug"
    )
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Console
        exclude = ["slug"]

    def get_thumbnail_url(self, obj):
        if obj.image:
            return obj.image.url.replace("/upload/", "/upload/f_auto,q_auto,w_400/")
        return None


class ManufacturerSerializer(ModelSerializer):
    consoles = serializers.StringRelatedField(many=True, read_only=True)
    logo_thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Manufacturer
        fields = "__all__"

    def get_logo_thumbnail_url(self, obj):
        if obj.logo:
            return obj.logo.url.replace("/upload/", "/upload/f_auto,q_auto,h_100/")
        return None