from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from patients.models import Patient
from patients.serializer import PatientSerializer
from utils.utils import perform_create


class PatientViewSet(viewsets.ModelViewSet):
  queryset = Patient.objects.all()
  serializer_class = PatientSerializer
  permission_classes = [IsAuthenticated]

  def perform_create(self, serializer):
    perform_create(serializer=serializer)

