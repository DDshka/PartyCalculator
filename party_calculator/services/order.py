import decimal

from party_calculator.common.service import Service
from party_calculator.models import OrderedFood, Party


class OrderService(Service):
    model = OrderedFood

    def get_by_party(self, party: Party):
        return party.ordered_food.all()

    def create_or_update_order_item(self, party: Party, name: str, price: decimal, quantity: int):
        ordered_food, created = OrderedFood.objects.get_or_create(party=party, name=name)
        ordered_food.price = price
        ordered_food.quantity += quantity
        ordered_food.save()