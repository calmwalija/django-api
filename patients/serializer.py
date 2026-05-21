from rest_framework import serializers

from patients.models import Patient


class PatientSerializer(serializers.ModelSerializer):

  def to_internal_value(self, data):
    if "gender" in data:
      data["gender"] = data["gender"].upper()
    return super().to_internal_value(data)

  class Meta:
    model = Patient
    fields = [
      'id',
      'first_name',
      'last_name',
      'date_of_birth',
      'gender',
      'phone_number',
      'address',
      'medical_history',
      'created_at',
      'updated_at'
    ]
    read_only_fields = ['created_at', 'updated_at']
