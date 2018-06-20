from django.db import transaction

from party_calculator.common.service import Service
from party_calculator.exceptions import MemberAlreadyInParty, \
    NoSuchTemplatePartyState
from party_calculator.models import TemplateParty, Membership, OrderedFood, Food, Party
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService
from party_calculator.services.schedule import ScheduleService
from party_calculator.services.template_member import TemplateMemberService
from party_calculator.services.template_order import TemplateOrderService
from party_calculator_auth.models import Profile


class TemplatePartyService(Service):
    model = TemplateParty

    TEMPLATE_PREFIX = 'Template'

    @transaction.atomic()
    def create(self, name, creator, members=None, food=None):
        if not members:
            members = []

        if not food:
            food = []

        template_party = super(TemplatePartyService, self).create(name=name, created_by=creator)

        ms = TemplateMemberService()
        ms.create(profile=creator, party=template_party, is_owner=True)
        for member in members:
            ms.create(profile=member, party=template_party)

        os = TemplateOrderService()
        for item in food:
            os.create(party=template_party,
                      food=item.name,
                      price=item.price,
                      quantity=1)

        return template_party

    @transaction.atomic
    def create_from_existing(self, party: Party) -> TemplateParty:
        template_name = self.get_template_name(party)
        template_party = super(TemplatePartyService, self).create(name=template_name, created_by=party.created_by)

        template_food = {}
        os = TemplateOrderService()
        for item in party.orderedfood_set.all():
            order_item = os.create(party=template_party,
                                   name=item.name,
                                   price=item.price,
                                   quantity=item.quantity)
            template_food[order_item.name] = order_item

        tms = TemplateMemberService()
        members = PartyService().get_party_members(party)
        for member in members:
            template_member = tms.create(profile=member.profile, party=template_party, is_owner=member.is_owner)
            for excluded_food in member.excluded_food.all():
                food = template_food[excluded_food.name]
                template_member.excluded_food.add(food)

        party.template = template_party
        party.save()

        return template_party

    def is_active(self, template: model):
        return True if template.state == self.model.ACTIVE else False

    def has_active_parties(self, template: TemplateParty):
        return template.parties.filter(state=Party.ACTIVE).exists()

    def get_template_members(self, template: model):
        return template.template_memberships.all()

    def get_template_ordered_food(self, template: model):
        return template.template_ordered_food.all()

    def add_member_to_template(self, template: model, info: str):
        profile = ProfileService().get(username=info)

        if not profile:
            raise Profile.DoesNotExist()

        if TemplateMemberService().is_party_member(profile, template):
            raise MemberAlreadyInParty(
                "User {0} (id={1}) is already in {2} (id={3})"
                    .format(profile.username, profile.id, template.name, template.id)
            )

        TemplateMemberService().grant_membership(template, profile)

    def remove_member_from_template(self, member: Membership):
        TemplateMemberService().revoke_membership(member)

    def order_food(self, template: model, food: Food, quantity: int):
        TemplateOrderService().create_or_update_order_item(template, food, quantity)

    def remove_from_order(self, order_item: OrderedFood):
        TemplateOrderService().delete(order_item)

    def set_state(self, template: model, state):
        allowed_states = (TemplateParty.ACTIVE, TemplateParty.INACTIVE)
        if state not in allowed_states:
            raise NoSuchTemplatePartyState()

        state_for_periodic_task = True if state == TemplateParty.ACTIVE else False
        ScheduleService().set_periodic_task_enabled(template, state_for_periodic_task)

        template.state = state
        template.save()

    def set_frequency(self, template: model, pattern: str):
        if not template.schedule:
            schedule = ScheduleService().create(pattern=pattern)
            template.schedule = schedule
            template.save()
        else:
            schedule = template.schedule
            ScheduleService().update(schedule, pattern)

    def get_template_name(self, party: Party):
        return '{0} {1}'.format(self.TEMPLATE_PREFIX, party.name)