from django.shortcuts import get_object_or_404

from party_calculator.models import OrderedFood, Party, Food


class OrderService:
  def get_by_party(self, party: Party):
    return party.ordered_food.all()

  def get_order_item_by_id(self, order_item_id: int) -> OrderedFood:
    return get_object_or_404(OrderedFood, id=order_item_id)

  def delete_order_item_by_id(self, order_item_id: int):
    self.get_order_item_by_id(order_item_id).delete()

  def create_or_update_order_item(self, party: Party, food: Food, quantity: int):
    ordered_food, created = OrderedFood.objects.get_or_create(party=party, food=food.name)
    ordered_food.price = food.price
    ordered_food.quantity += quantity
    ordered_food.save()