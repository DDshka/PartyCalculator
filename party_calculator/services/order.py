from party_calculator.common.service import Service
from party_calculator.models import OrderedFood, Party, Food


class OrderService(Service):
    model = OrderedFood

    def get_by_party(self, party: Party):
        return party.ordered_food.all()

    def create_or_update_order_item(self, party: Party, food: Food, quantity: int):
        ordered_food, created = OrderedFood.objects.get_or_create(party=party, food=food.name)
        ordered_food.price = food.price
        ordered_food.quantity += quantity
        ordered_food.save()
