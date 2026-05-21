import random
from datetime import datetime

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth.models import User

from patients.models import Patient
from patients.serializer import PatientSerializer


# Create your views here.

def create_django_user(username: str):
  return User.objects.create_user(username=username)


def create_patient(request: Request):
  serialized_data = PatientSerializer(data=request.data)
  if serialized_data.is_valid(raise_exception=True):
    salt = random.randint(1910, 31000)
    new_user_id = datetime.now().microsecond + salt
    username = f"{request.data['first_name'].strip()}.{request.data['last_name'].strip()}.{new_user_id}".lower()
    create_django_user(username)
    serialized_data.save()
    return JsonResponse(data=serialized_data.data, status=status.HTTP_201_CREATED)
  return Response(data=serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)


def get_patients(_: Request, id: int = None):
  if id is None:
    patients = Patient.objects.all()
    serialized_patients = PatientSerializer(patients, many=True)
    return JsonResponse(data=serialized_patients.data, safe=False, status=status.HTTP_200_OK)
  try:
    patient = Patient.objects.get(pk=id)
    serializer = PatientSerializer(patient)
    return Response(serializer.data, status=status.HTTP_200_OK)
  except Patient.DoesNotExist:
    return Response(status=status.HTTP_404_NOT_FOUND)


def update_patient(request: Request, id: int):
  try:

    patient: Patient = Patient.objects.get(pk=id)
    serializer: PatientSerializer = PatientSerializer(patient, data=request.data)

    if serializer.is_valid(raise_exception=True):
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)

  except Patient.DoesNotExist:
    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT'])
def patient_detail(request: Request, id: int):
  if request.method == 'GET':
    return get_patients(request, id=id)
  elif request.method == 'PUT':
    return update_patient(request, id)
  return None


@api_view(['GET', 'POST'])
def patient_list(request: Request):
  if request.method == 'POST':
    return create_patient(request)
  elif request.method == 'GET':
    return get_patients(request)
  return None
