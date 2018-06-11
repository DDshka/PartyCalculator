from django.test import TestCase

from party_calculator.models import OrderedFood
from party_calculator.services.food import FoodService
from party_calculator.services.member import MemberService
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService


class PartyTestCase(TestCase):
    test_food = {
        'Beer': 125.50,
        'Pizza': 290,
        'BigPizza': 475.50,
        'Meat': 170
    }

    test_users = (
        'Boskin',
        'Kuzya',
        'Sashka',
        'Hakka',
        'Mason',
    )

    test_party_name = 'test_party'

    def setUp(self):
        for key in self.test_food:
            FoodService().create(name=key, price=self.test_food[key])

        members = []

        for name in self.test_users:
            members.append(ProfileService().create(username=name))

        PartyService().create(creator=members[0], name=self.test_party_name)

    def test_add_members_to_party(self):
        ps = ProfileService()
        users = [ps.get(username=user) for user in self.test_users[1:]]

        party = PartyService().get(name=self.test_party_name)
        members = []
        ms = MemberService()
        for user in users:
            members.append(ms.create(profile=user, party=party))

        # Check parties names
        self.assertEqual(
            party.name,
            self.test_party_name
        )

        # check membership
        self.assertIn(
            MemberService().get(id=members[0].id),
            PartyService().get_party_members(party),
        )

        # check owner
        self.assertEqual(
            PartyService().get(name=self.test_party_name).created_by,
            ProfileService().get(username=self.test_users[0])
        )

    def test_add_food_to_party(self):
        ps = PartyService()

        party = ps.get(name=self.test_party_name)
        for food in FoodService().get(name='Beer'):
            ordered_food, created = OrderedFood.objects.get_or_create(party=party, food=food.name)
            ordered_food.price = food.price
            ordered_food.quantity += 1
            ordered_food.save()

        ps.order_food(party, food, quantity=3)
