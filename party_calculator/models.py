from django.db import models
from django_celery_beat.models import CrontabSchedule

from party_calculator_auth.models import Profile


class AbstractParty(models.Model):
    class Meta:
        abstract = True

    ACTIVE = 'active'
    INACTIVE = 'inactive'

    states = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive')
    )

    name = models.CharField(max_length=1024, null=False, blank=False)
    created_by = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    state = models.CharField(max_length=512, choices=states, default=ACTIVE)
    duration = models.DurationField(null=True)

    def __str__(self):
        return self.name


class AbstractMembership(models.Model):
    class Meta:
        abstract = True
        ordering = ['-is_owner']

    profile = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    is_owner = models.BooleanField(null=False, default=False)


class AbstractOrderedFood(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=1024, null=False, blank=False)
    price = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    quantity = models.IntegerField(default=0)

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return self.name.__str__()


class Food(models.Model):
    name = models.CharField(max_length=1024, null=False, blank=False)
    price = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class OrderedFood(AbstractOrderedFood):
    party = models.ForeignKey("Party", on_delete=models.CASCADE)


class Membership(AbstractMembership):
    party = models.ForeignKey("Party", on_delete=models.CASCADE, related_name='memberships')
    excluded_food = models.ManyToManyField(OrderedFood)
    total_sponsored = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)

    def __str__(self):
        return self.party.__str__()


class Party(AbstractParty):
    members = models.ManyToManyField(Profile, through=Membership, related_name='member_of')
    ordered_food = models.ManyToManyField(OrderedFood, related_name='ordered_by')
    template = models.ForeignKey("TemplateParty", null=True, on_delete=models.SET_NULL, related_name='parties')

    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)


class Schedule(models.Model):
    name = models.CharField(max_length=1024, null=False, blank=False)
    minute = models.CharField(max_length=60 * 4, default='*')
    hour = models.CharField(max_length=24 * 4, default='*')
    day_of_week = models.CharField(max_length=64, default='*')
    day_of_month = models.CharField(max_length=31 * 4, default='*')
    month_of_year = models.CharField(max_length=64, default='*')

    def __str__(self):
        return self.name


class TemplateOrderedFood(AbstractOrderedFood):
    party = models.ForeignKey("TemplateParty", null=True, on_delete=models.SET_NULL, related_name='template_ordered_food')


class TemplateMembership(AbstractMembership):
    party = models.ForeignKey("TemplateParty", on_delete=models.CASCADE, related_name='template_memberships')
    excluded_food = models.ManyToManyField(TemplateOrderedFood)

    def __str__(self):
        return self.party.__str__()


class TemplateParty(AbstractParty):
    members = models.ManyToManyField(Profile, through=TemplateMembership, related_name='template_member_of')
    ordered_food = models.ManyToManyField(TemplateOrderedFood, related_name='template_order_of')
    schedule = models.ForeignKey(Schedule, null=True, on_delete=models.SET_NULL)
    state = models.CharField(max_length=512, choices=AbstractParty.states, default=AbstractParty.INACTIVE)


