from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from PartyCalculator.settings import WEBSITE_URL, HOST
from authModule.models import Profile
from party_calculator.models import Party
from party_calculator.services.food import FoodService
from party_calculator.services.order import OrderService
from party_calculator.services.profile import ProfileService


class PartyService:
  def get_by_id(self, id: int) -> Party:
    return get_object_or_404(Party, id=id)

  def get_party_members(self, party: Party):
    return party.membership_set.all()

  def get_party_ordered_food(self, party: Party):
    return party.orderedfood_set.all()

  def add_member_to_party(self, party: Party, profile: Profile):
    from party_calculator.services.member import MemberService
    MemberService().grant_membership(party, profile)

  def remove_member_from_party(self, member_id: int):
    from party_calculator.services.member import MemberService
    MemberService().revoke_membership(member_id)

  def party_order_food(self, party_id: int, food_id: int, quantity: int):
    party = self.get_by_id(party_id)
    food = FoodService().get_by_id(food_id)
    OrderService().create_or_update_order_item(party, food, quantity)

  def remove_from_order(self, order_item_id: int):
    OrderService().delete_order_item_by_id(order_item_id)

  def invite_member(self, party_id: int, info: str) -> str:
    if '@' in info:
      profile = ProfileService().get_by_email(info)
    else:
      profile = ProfileService().get_by_username(info)

    if not profile:
      return 'Such user does not exist'

    party = PartyService().get_by_id(party_id)
    from party_calculator.services.member import MemberService # I`ve got import error with global import, so I`ve just made it local
    if MemberService().is_party_member_by_profile_and_party(profile, party):
      return 'User is already in this party'

    if not profile.email:
      return "We cannot invite user without email"

    join_url = '/party/invite/someID'
    send_mail("Party calculator: You are invited to {0}".format(party.name),
              "Proceed this link to join the Party and start becoming drunk\n"
              "{0}{1}".format(WEBSITE_URL, join_url),
              "admin@{0}".format(HOST),
              [profile.email])

    # We will add member without confirmation for now but check console for a message
    self.add_member_to_party(party, profile)

    return 'Successfully invited'

