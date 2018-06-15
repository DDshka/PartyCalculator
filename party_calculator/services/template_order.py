import decimal

from party_calculator.common.service import Service
from party_calculator.models import TemplateOrderedFood, TemplateParty, Food


class TemplateOrderService(Service):
    model = TemplateOrderedFood

    def get_by_party(self, party: model):
        return party.ordered_food.all()

    def create_or_update_order_item(self, party: TemplateParty, food: Food, quantity: int):
        ordered_food, _ = self.model.objects.get_or_create(party=party, food=food.name)
        ordered_food.price = food.price
        ordered_food.quantity += quantity
        ordered_food.save()
