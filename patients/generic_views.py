from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from patients.models import Patient
from patients.serializer import PatientSerializer
from utils.utils import perform_create


class PatientGenericView(generics.ListCreateAPIView):
  serializer_class = PatientSerializer
  permission_classes = [IsAuthenticated]
  queryset = Patient.objects.all()

  def perform_create(self, serializer):
    perform_create(serializer=serializer)


class PatientRetrieveView(generics.RetrieveAPIView):
  queryset = Patient.objects.all()
  serializer_class = PatientSerializer
  permission_classes = [IsAuthenticated]
  lookup_field = "id"
