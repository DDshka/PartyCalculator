import uuid

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
    verification = models.OneToOneField('Code', null=True, on_delete=models.SET_NULL)


class Code(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    code = models.UUIDField(default=uuid.uuid4)


# class PseudoBigModel(models.Model):
#     some_date_var = models.DateTimeField(auto_now=True)
#     some_int_var = models.IntegerField(null=True)
#     some_bool_var = models.BooleanField(default=False)
#     some_important_info = models.CharField(max_length=1024, null=False, blank=False)

class PseudoSmallModel_Two(models.Model):
    some_date_var = models.DateTimeField(auto_now=True)
    some_int_var = models.IntegerField(null=True)
    some_bool_var = models.BooleanField(default=False)

class PseudoSmallModel_One(models.Model):
    psm_two = models.OneToOneField(PseudoSmallModel_Two, on_delete=models.CASCADE)
    some_important_info = models.CharField(max_length=1024, null=False, blank=False)

