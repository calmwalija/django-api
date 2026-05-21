import random
from datetime import datetime

from django.contrib.auth.models import User


def perform_create(serializer):
  first_name = serializer.validated_data["first_name"].strip()
  last_name = serializer.validated_data["last_name"].strip()

  salt = random.randint(1910, 31000)
  new_user_id = datetime.now().microsecond + salt
  username = f"{first_name}.{last_name}.{new_user_id}".lower()

  user = User.objects.create_user(username=username)
  serializer.save(user=user)
