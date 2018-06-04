from django.contrib.auth.models import User
from django.db import models


class Profile(User):
  GENDERS = (
    ('male', 'Male'),
    ('female', 'Female')
  )

  age = models.IntegerField(null=True, blank=False)
  gender = models.CharField(max_length=128, choices=GENDERS, null=True, blank=False)
  legacy_id = models.IntegerField(null=True, blank=False)