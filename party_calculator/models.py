from django.db import models

from authModule.models import Profile


class Food(models.Model):
  name = models.CharField(max_length=1024, null=False, blank=False)
  price = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)

  def __str__(self):
    return self.name


class Party(models.Model):
  name = models.CharField(max_length=1024, null=False, blank=False)

  members = models.ManyToManyField(Profile, through='Membership', related_name='memberships')
  ordered_food = models.ManyToManyField('OrderedFood', related_name='ordered_by')
  created_by = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name='creator')

  def __str__(self):
    return self.name


class Membership(models.Model):
  profile = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
  party = models.ForeignKey(Party, on_delete=models.CASCADE)
  excluded_food = models.ManyToManyField('OrderedFood')

  is_owner = models.BooleanField(null=False, default=False)
  total_sponsored = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)

  def __str__(self):
    return self.party.__str__()


class OrderedFood(models.Model):
  party = models.ForeignKey(Party, on_delete=models.CASCADE)
  food = models.CharField(max_length=1024, null=False, blank=False)
  price = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
  quantity = models.IntegerField(default=0)

  @property
  def total(self):
    return self.price * self.quantity

  def __str__(self):
    return self.food.__str__()
