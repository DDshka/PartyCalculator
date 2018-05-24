from django.db import models

from authModule.models import Profile


class Food(models.Model):
  name = models.CharField(max_length=1024, null=False, blank=False)
  price = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)


class Party(models.Model):
  name = models.CharField(max_length=1024, null=False, blank=False)

  members = models.ManyToManyField(Profile, through='Membership')
  ordered_food = models.ManyToManyField(Food, through='PartyDesiredFood')
  created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='creator')


class Membership(models.Model):
  profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
  party = models.ForeignKey(Party, on_delete=models.CASCADE)
  excluded_food = models.ManyToManyField(Food, name='MemberExcludedFood')

  is_owner = models.BooleanField(null=False, default=False)
  total_sponsored = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)


class PartyDesiredFood(models.Model):
  party_id = models.ForeignKey(Party, on_delete=models.CASCADE)
  food_id = models.ForeignKey(Food, on_delete=models.CASCADE)
  quantity = models.IntegerField(default=1)
