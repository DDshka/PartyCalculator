from django import template

from party_calculator.models import Membership, OrderedFood
from party_calculator_auth.models import Profile

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
def is_excluded(order_item: OrderedFood, request):
    profile = Profile.objects.get(id=request.user.id)
    membership = Membership.objects.get(party=order_item.party, profile=profile)

    return membership.excluded_food.filter(id=order_item.id).exists()

