from django.shortcuts import get_object_or_404

from party_calculator.models import Party, OrderedFood, Membership
from party_calculator.services.food import get_food_by_id
from party_calculator.services.profile import get_profile_by_request


def get_party_by_id(id: int) -> Party:
  return get_object_or_404(Party, id=id)


def get_party_members(party: Party):
  return party.membership_set.all()


def get_party_ordered_food(party: Party):
  return party.orderedfood_set.all()


def party_order_food(party_id, food_id, quantity):
  party = get_party_by_id(party_id)
  food = get_food_by_id(food_id)

  party_desired_food, created = OrderedFood.objects.get_or_create(party=party, food=food)
  party_desired_food.quantity += quantity
  party_desired_food.save()

def party_remove_from_order(party_id: int, order_item_id: int):
  party = get_party_by_id(party_id)
  order_item = get_order_item(order_item_id)

  party.ordered_food.remove(order_item)

def get_order(party: Party):
  return party.ordered_food.all()


def get_order_item(order_item_id: int) -> OrderedFood:
  return get_object_or_404(OrderedFood, id=order_item_id)


def get_member_by_request(request, party_id) -> Membership:
  profile = get_profile_by_request(request)
  party = get_party_by_id(party_id)

  return get_object_or_404(Membership, profile=profile, party=party)


def member_exclude_food(request, order_item_id: int):
  order_item = get_order_item(order_item_id)
  party_id = order_item.party.id

  member = get_member_by_request(request, party_id)
  member.excluded_food.add(order_item)


def member_include_food(request, order_item_id: int):
  order_item = get_order_item(order_item_id)
  party_id = order_item.party.id

  member = get_member_by_request(request, party_id)
  member.excluded_food.remove(order_item)

