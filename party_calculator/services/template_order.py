import decimal

from party_calculator.common.service import Service
from party_calculator.models import TemplateOrderedFood, TemplateParty


class TemplateOrderService(Service):
    model = TemplateOrderedFood

    def get_by_party(self, party: model):
        return party.ordered_food.all()

    def create_or_update_order_item(self, party: TemplateParty, name: str, price: decimal, quantity: int):
        ordered_food, _ = self.model.objects.get_or_create(party=party, name=name)
        ordered_food.price = price
        ordered_food.quantity += quantity
        ordered_food.save()
