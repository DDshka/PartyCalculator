import decimal
import time

from django.core.exceptions import PermissionDenied
from django.db import transaction

from PartyCalculator.settings import WEBSITE_URL, HOST
from party_calculator.common.service import Service
from party_calculator.exceptions import MemberAlreadyInPartyException, NoSuchPartyStateException
from party_calculator.models import Party, Food, Membership, OrderedFood, TemplateParty
from party_calculator.services.member import MemberService
from party_calculator.services.order import OrderService
from party_calculator.services.profile import ProfileService
from party_calculator_auth.models import Profile


class PartyService(Service):
    model = Party

    def __init__(self):
        self.member_service = MemberService()
        self.order_service = OrderService()
        self.profile_service = ProfileService()

    def create(self, name, creator, members=None) -> model:
        if not members:
            members = []

        party = super(PartyService, self).create(name=name, created_by=creator)

        self.member_service.create(profile=creator, party=party, is_owner=True)
        for member in members:
            self.member_service.create(profile=member, party=party)

        return party

    @transaction.atomic
    def create_from_template(self, template: TemplateParty) -> model:
        from party_calculator.services.template_party import TemplatePartyService
        template_name = template.name.replace(TemplatePartyService.TEMPLATE_PREFIX, '')
        party_name = '{0} | {1}'.format(
            template_name,
            time.strftime("%d.%m.%Y:%H:%M")
        )

        party = super(PartyService, self).create(name=party_name,
                                                 created_by=template.created_by,
                                                 template=template)

        party_food = {}
        for order_item in template.template_ordered_food.all():
            item = self.order_service.create(party=party,
                                             name=order_item.name,
                                             price=order_item.price,
                                             quantity=order_item.quantity)
            party_food[item.name] = item

        for template_member in template.template_memberships.all():
            is_owner = True if template_member.profile == party.created_by else False
            member = self.member_service.create(profile=template_member.profile,
                                                party=party,
                                                is_owner=is_owner)

            for template_excluded_food in template_member.excluded_food.all():
                food = party_food[template_excluded_food.name]
                member.excluded_food.add(food)

        return party

    def set_state(self, party: model, state):
        self.check_is_party_active(party)

        if state not in [x for (x, y) in self.model.states]:
            raise NoSuchPartyStateException()

        party.state = state
        party.save()

    def is_active(self, party: model):
        return True if party.state == self.model.ACTIVE else False

    def has_template(self, party: Party) -> bool:
        return True if party.template else False

    def get_party_members(self, party: model, excluding=None):
        if excluding:
            return party.memberships.exclude(**excluding)
        return party.memberships.all()

    def get_party_profiles(self, party: model, excluding=None):
        if excluding:
            return party.members.exclude(**excluding)
        return party.members.all()

    def get_party_ordered_food(self, party: model):
        return party.orderedfood_set.all()

    def add_member_to_party(self, party: model, profile: Profile):
        self.check_is_party_active(party)

        self.member_service.grant_membership(party, profile)

    def remove_member_from_party(self, member: Membership):
        self.check_is_party_active(member.party)

        self.member_service.revoke_membership(member)

    def order_food(self, party: model, food: Food, quantity: int):
        self.check_is_party_active(party)

        self.order_service.create_or_update_order_item(party,
                                                       food.name,
                                                       food.price,
                                                       quantity)

    def remove_from_order(self, order_item: OrderedFood):
        self.check_is_party_active(order_item.party)

        self.order_service.delete(order_item)

    def sponsor_party(self, member: Membership, amount: float):
        self.check_is_party_active(member.party)

        member.total_sponsored += decimal.Decimal(amount)
        member.save()

    def invite_member(self, party: model, info: str):
        self.check_is_party_active(party)

        profile = self.profile_service.get(username=info)

        if not profile:
            raise Profile.DoesNotExist()

        if self.member_service.is_party_member(profile, party):
            raise MemberAlreadyInPartyException(
                "User {0} (id={1}) is already in {2} (id={3})"
                .format(profile.username, profile.id, party.name, party.id)
            )

        join_url = '/party/invite/someID'
        from party_calculator.tasks import send_mail
        send_mail.delay("Party calculator: You are invited to {0}".format(party.name),
                        "Proceed this link to join the Party and start becoming drunk\n"
                        "{0}{1}".format(WEBSITE_URL, join_url),
                        "admin@{0}".format(HOST),
                        [profile.email])

        # We will add member without confirmation for now but check console for a message
        self.add_member_to_party(party, profile)

    def check_is_party_active(self, party: model):
        if not self.is_active(party):
            raise PermissionDenied("You cannot modify inactive party")
