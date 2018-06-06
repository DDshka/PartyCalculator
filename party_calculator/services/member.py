from django.shortcuts import get_object_or_404

from party_calculator.models import Membership
from party_calculator.services.order import OrderService
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService


class MemberService:
  def get_by_user_id(self, user_id: int, party_id: int) -> Membership:
    profile = ProfileService().get_by_id(user_id)
    party = PartyService().get_by_id(party_id)

    return get_object_or_404(Membership, profile=profile, party=party)

  def is_party_member(self, user_id: int, party_id: int) -> bool:
    profile = ProfileService().get_by_id(user_id)
    party = PartyService().get_by_id(party_id)
    return Membership.objects.filter(profile=profile, party=party).exists()

  def is_party_admin(self, user_id: int, party_id: int) -> bool:
    profile = ProfileService().get_by_id(user_id)
    party = PartyService().get_by_id(party_id)
    return Membership.objects.filter(profile=profile, party=party, is_owner=True).exists() or party.created_by == profile

  def member_exclude_food(self, user_id: int, order_item_id: int):
    order_item = OrderService().get_order_item_by_id(order_item_id)
    party_id = order_item.party.id

    member = self.get_by_user_id(user_id, party_id)
    member.excluded_food.add(order_item)

  def member_include_food(self, user_id: int, order_item_id: int):
    order_item = OrderService().get_order_item_by_id(order_item_id)
    party_id = order_item.party.id

    member = self.get_by_user_id(user_id, party_id)
    member.excluded_food.remove(order_item)

