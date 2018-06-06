from django.shortcuts import get_object_or_404

from party_calculator.models import Party
from party_calculator.services.food import FoodService
from party_calculator.services.order import OrderService


class PartyService:
  def get_by_id(self, id: int) -> Party:
    return get_object_or_404(Party, id=id)

  def get_party_members(self, party: Party):
    return party.membership_set.all()

  def get_party_ordered_food(self, party: Party):
    return party.orderedfood_set.all()

  def party_order_food(self, party_id: int, food_id: int, quantity: int):
    party = self.get_by_id(party_id)
    food = FoodService().get_by_id(food_id)
    OrderService().create_or_update_order_item(party, food, quantity)

  def party_remove_from_order(self, order_item_id: int):
    OrderService().delete_order_item_by_id(order_item_id)