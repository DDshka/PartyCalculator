from django.core.mail import send_mail

from PartyCalculator.settings import WEBSITE_URL, HOST
from authModule.models import Profile
from party_calculator.common.service import Service
from party_calculator.models import Party, Food, Membership, OrderedFood
from party_calculator.services.member import MemberService
from party_calculator.services.order import OrderService
from party_calculator.services.profile import ProfileService


class PartyService(Service):

  model = Party

  def create(self, name, creator, members=[]) -> model:
    party = super(PartyService, self).create(name=name, created_by=creator)

    from party_calculator.services.member import MemberService
    ms = MemberService()
    ms.create(profile=creator, party=party, is_owner=True)
    for member in members:
      ms.create(profile=member, party=party)

    return party

  def set_inactive(self, party: Party):
    party.state = Party.INACTIVE
    party.save()

  def is_active(self, party: Party):
    return True if party.state == Party.ACTIVE else False

  def get_party_members(self, party: Party):
    return party.membership_set.all()

  def get_party_ordered_food(self, party: Party):
    return party.orderedfood_set.all()

  def add_member_to_party(self, party: Party, profile: Profile):
    MemberService().grant_membership(party, profile)

  def remove_member_from_party(self, member: Membership):
    MemberService().revoke_membership(member)

  def order_food(self, party: Party, food: Food, quantity: int):
    OrderService().create_or_update_order_item(party, food, quantity)

  def remove_from_order(self, order_item: OrderedFood):
    OrderService().delete(order_item)

  def invite_member(self, party: Party, info: str) -> str:
    if '@' in info:
      profile = ProfileService().get(email=info)
    else:
      profile = ProfileService().get(username=info)

    if not profile:
      return 'Such user does not exist'

    if MemberService().is_party_member(profile, party):
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

