from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics,viewsets,status
from consoles import models
from consoles.api import serializers,pagination,filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly



class ConsoleAV(generics.ListAPIView):
    queryset = models.Console.objects.all()
    serializer_class= serializers.ConsoleSerializer
    filterset_class = filters.ConsoleFilter
    pagination_class = pagination.CdbDefaultPagination
    ordering_fields = ['release_year']
    permission_classes = [IsAuthenticatedOrReadOnly]


class ConsoleDetailAV(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Console.objects.all()
    serializer_class = serializers.ConsoleSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]


class ManufacturerAV(generics.ListAPIView):
    queryset = models.Manufacturer.objects.all()
    serializer_class = serializers.ManufacturerSerializer
    filterset_fields = ['country']
    pagination_class = pagination.CdbDefaultPagination
    ordering_fields = ['founded_in']
    permission_classes = [IsAuthenticatedOrReadOnly]



class ManufacturerDetailAV(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Manufacturer.objects.all()
    serializer_class = serializers.ManufacturerSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
