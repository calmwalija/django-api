from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
  GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]

  user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
  first_name = models.CharField(max_length=128)
  last_name = models.CharField(max_length=128)
  date_of_birth = models.DateField()
  gender = models.CharField(max_length=16, choices=GENDER_CHOICES)
  phone_number = models.CharField(
    max_length=8,
    unique=True,
    validators=[RegexValidator(regex=r'^[89]\d{7}$', message='Phone number must be 8 digits starting with 8 or 9')],
  )
  address = models.CharField(max_length=128)
  medical_history = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def save(self, *args, **kwargs):
    self.gender = self.gender.upper()
    super().save(*args, **kwargs)

  class Meta:
    db_table = 'patient'
