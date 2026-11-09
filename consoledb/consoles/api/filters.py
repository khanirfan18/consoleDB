import django_filters
from consoles import models


class ConsoleFilter(django_filters.FilterSet):
     console_type = django_filters.CharFilter(
          field_name='console_type',
          lookup_expr='iexact'
     )
     class Meta:
          model = models.Console
          fields = ['generation', 'console_type', 'is_active']