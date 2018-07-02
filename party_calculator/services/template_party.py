from django.db import transaction

from party_calculator.common.service import Service
from party_calculator.exceptions import MemberAlreadyInPartyException, \
    NoSuchTemplatePartyStateException
from party_calculator.models import TemplateParty, Membership, OrderedFood, Food, Party, Schedule
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService
from party_calculator.services.schedule import ScheduleService
from party_calculator.services.template_member import TemplateMemberService
from party_calculator.services.template_order import TemplateOrderService
from party_calculator_auth.models import Profile


class TemplatePartyService(Service):
    model = TemplateParty

    TEMPLATE_PREFIX = 'Template'

    def __init__(self):
        self.party_service = PartyService()
        self.profile_service = ProfileService()
        self.schedule_service = ScheduleService()
        self.template_order_service = TemplateOrderService()
        self.template_member_service = TemplateMemberService()

    @transaction.atomic()
    def create(self, name, creator, members=None, food=None):
        if not members:
            members = []

        if not food:
            food = []

        template_party = super(TemplatePartyService, self).create(name=name,
                                                                  created_by=creator)

        self.template_member_service.create(profile=creator,
                                            party=template_party,
                                            is_owner=True)
        for member in members:
            self.template_member_service.create(profile=member, party=template_party)

        for item in food:
            self.template_order_service.create(party=template_party,
                                               name=item.name,
                                               price=item.price,
                                               quantity=1)

        return template_party

    @transaction.atomic
    def create_from_existing(self, party: Party) -> TemplateParty:
        template_name = self.get_template_name(party)
        template_party = super(TemplatePartyService, self).create(name=template_name,
                                                                  created_by=party.created_by)

        template_food = {}
        for item in party.orderedfood_set.all():
            order_item = self.template_order_service.create(party=template_party,
                                                            name=item.name,
                                                            price=item.price,
                                                            quantity=item.quantity)
            template_food[order_item.name] = order_item

        members = self.party_service.get_party_members(party)
        for member in members:
            template_member = self.template_member_service.create(profile=member.profile,
                                                                  party=template_party,
                                                                  is_owner=member.is_owner)
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
        profile = self.profile_service.get(username=info)

        if not profile:
            raise Profile.DoesNotExist

        if self.template_member_service.is_party_member(profile, template):
            raise MemberAlreadyInPartyException(
                "User {0} (id={1}) is already in {2} (id={3})"
                    .format(profile.username, profile.id, template.name, template.id)
            )

        self.template_member_service.grant_membership(template, profile)

    def remove_member_from_template(self, member: Membership):
        self.template_member_service.revoke_membership(member)

    def order_food(self, template: model, food: Food, quantity: int):
        self.template_order_service.create_or_update_order_item(template, food.name, food.price, quantity)

    def remove_from_order(self, order_item: OrderedFood):
        self.template_order_service.delete(order_item)

    def set_state(self, template: model, state):
        allowed_states = (TemplateParty.ACTIVE, TemplateParty.INACTIVE)
        if state not in allowed_states:
            raise NoSuchTemplatePartyStateException()

        state_for_periodic_task = True if state == TemplateParty.ACTIVE else False
        self.schedule_service.set_periodic_task_enabled(template, state_for_periodic_task)

        template.state = state
        template.save()

    def set_frequency(self, template: model, schedule: Schedule):
        schedule_values = (
            schedule.minute,
            schedule.hour,
            schedule.day_of_week,
            schedule.day_of_month,
            schedule.month_of_year
        )
        kwargs = dict(zip(self.schedule_service.CRONTAB_FIELDS, schedule_values))

        crontab_schedule, _ = self.schedule_service.get_or_create_dcbcs(**kwargs)

        template.schedule = schedule
        template.save()

    def get_template_name(self, party: Party):
        return '{0} {1}'.format(self.TEMPLATE_PREFIX, party.name)