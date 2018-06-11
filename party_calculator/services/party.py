import decimal

from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail

from PartyCalculator.settings import WEBSITE_URL, HOST
from party_calculator_auth.models import Profile
from party_calculator.common.service import Service
from party_calculator.exceptions import MemberAlreadyInParty
from party_calculator.models import Party, Food, Membership, OrderedFood
from party_calculator.services.member import MemberService
from party_calculator.services.order import OrderService
from party_calculator.services.profile import ProfileService


class PartyService(Service):
    model = Party

    def create(self, name, creator, members=None) -> Party:
        if not members:
            members = []

        party = super(PartyService, self).create(name=name, created_by=creator)

        ms = MemberService()
        ms.create(profile=creator, party=party, is_owner=True)
        for member in members:
            ms.create(profile=member, party=party)

        return party

    def set_inactive(self, party: Party):
        self.check_is_party_active(party)

        party.state = Party.INACTIVE
        party.save()

    def is_active(self, party: Party):
        return True if party.state == Party.ACTIVE else False

    def get_party_members(self, party: Party):
        return party.membership_set.all()

    def get_party_profiles(self, party: Party, excluding=None):
        if excluding:
            return party.members.exclude(**excluding)
        return party.members.all()

    def get_party_ordered_food(self, party: Party):
        return party.orderedfood_set.all()

    def add_member_to_party(self, party: Party, profile: Profile):
        self.check_is_party_active(party)

        MemberService().grant_membership(party, profile)

    def remove_member_from_party(self, member: Membership):
        self.check_is_party_active(member.party)

        MemberService().revoke_membership(member)

    def order_food(self, party: Party, food: Food, quantity: int):
        self.check_is_party_active(party)

        OrderService().create_or_update_order_item(party, food, quantity)

    def remove_from_order(self, order_item: OrderedFood):
        self.check_is_party_active(order_item.party)

        OrderService().delete(order_item)

    def sponsor_party(self, member: Membership, amount: float):
        self.check_is_party_active(member.party)

        member.total_sponsored += decimal.Decimal(amount)
        member.save()

    def invite_member(self, party: Party, info: str):
        self.check_is_party_active(party)

        profile = ProfileService().get(username=info)

        if not profile:
            raise Profile.DoesNotExist()

        if MemberService().is_party_member(profile, party):
            raise MemberAlreadyInParty(
                "User {0} (id={1}) is already in {2} (id={3})"
                .format(profile.username, profile.id, party.name, party.id)
            )

        join_url = '/party/invite/someID'
        send_mail("Party calculator: You are invited to {0}".format(party.name),
                  "Proceed this link to join the Party and start becoming drunk\n"
                  "{0}{1}".format(WEBSITE_URL, join_url),
                  "admin@{0}".format(HOST),
                  [profile.email])

        # We will add member without confirmation for now but check console for a message
        self.add_member_to_party(party, profile)

    def check_is_party_active(self, party: Party):
        if not self.is_active(party):
            raise PermissionDenied("You cannot modify inactive party")
