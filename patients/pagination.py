from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class PatientPagination(PageNumberPagination):
  page_size = getattr(settings, 'PATIENT_PAGE_SIZE', 10)
  page_size_query_param = 'page_size'
  max_page_size = getattr(settings, 'PATIENT_MAX_PAGE_SIZE', 100)
