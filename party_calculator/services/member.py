from party_calculator.common.service import Service
from party_calculator.models import Membership, Party, OrderedFood
from party_calculator_auth.models import Profile


class MemberService(Service):
    model = Membership

    def grant_membership(self, party: Party, profile: Profile):
        self.model.objects.create(profile=profile, party=party)

    def revoke_membership(self, member: model):
        member.delete()

    def set_owner(self, member: Membership, is_owner: bool):
        member.is_owner = is_owner
        member.save()

    def is_party_member(self, profile: Profile, party: Party) -> bool:
        return self.model.objects.filter(profile=profile, party=party).exists()

    def is_party_admin(self, profile: Profile, party: Party) -> bool:
        return self.model.objects.filter(profile=profile, party=party, is_owner=True).exists() \
               or party.created_by == profile

    def member_exclude_food(self, profile: Profile, order_item: OrderedFood):
        party = order_item.party
        member = self.get(profile=profile, party=party)

        member.excluded_food.add(order_item)

    def member_include_food(self, profile: Profile, order_item: OrderedFood):
        party = order_item.party
        member = self.get(profile=profile, party=party)

        member.excluded_food.remove(order_item)
