import datetime

import pytz
from django import template

from PartyCalculator import settings
from party_calculator.models import Membership, OrderedFood

register = template.Library()


@register.filter('mul')
def mul(a, b):
    if a is None or b is None:
        return None

    return a * b


@register.filter('div')
def div(a, b):
    if a is None or b is None:
        return None

    return a / b


@register.filter('is_excluded')
def is_excluded(order_item: OrderedFood, member: Membership):
    return member.excluded_food.filter(id=order_item.id).exists()


@register.simple_tag(name='timestamp')
def timestamp():
    now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    return now.isoformat(timespec='milliseconds')

