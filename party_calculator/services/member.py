import decimal

from django.shortcuts import get_object_or_404

from authModule.models import Profile
from party_calculator.common.service import Service
from party_calculator.models import Membership, Party, OrderedFood

class MemberService(Service):

  model = Membership

  def grant_membership(self, party: Party, profile: Profile):
    Membership.objects.create(profile=profile, party=party)

  def revoke_membership(self, member: Membership):
    member.delete()

  def is_party_member(self, profile: Profile, party: Party) -> bool:
    return Membership.objects.filter(profile=profile, party=party).exists()

  def is_party_admin(self, profile: Profile, party: Party) -> bool:
    return Membership.objects.filter(profile=profile, party=party, is_owner=True).exists() \
           or party.created_by == profile

  def member_exclude_food(self, profile: Profile, order_item: OrderedFood):
    party = order_item.party
    member = self.get(profile=profile, party=party)

    member.excluded_food.add(order_item)

  def member_include_food(self, profile: Profile, order_item: OrderedFood):
    party = order_item.party
    member = self.get(profile=profile, party=party)

    member.excluded_food.remove(order_item)

  def sponsor_party(self, member: Membership, amount: float):
    member.total_sponsored += decimal.Decimal(amount)
    member.save()

