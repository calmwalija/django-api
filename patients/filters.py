import django_filters

from patients.models import Patient


class PatientFilter(django_filters.FilterSet):
  class Meta:
    model = Patient
    fields = {
      'gender': ['exact'],
      'first_name': ['icontains', 'exact'],
      'last_name': ['icontains', 'exact'],
      'phone_number': ['exact'],
      'date_of_birth': ['exact', 'gte', 'lte'],
    }
