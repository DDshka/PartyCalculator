from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.base import View

from party_calculator.common import get_form_errors_as_str, get_formset_errors_as_str
from party_calculator.common.party import PartyMemberPermission, PartyAdminPermission
from party_calculator.exceptions import MemberAlreadyInPartyException
from party_calculator.forms import AddMemberToPartyForm, AddCustomFoodToPartyForm, \
    SponsorPartyForm, CreatePartyForm, \
    PartyMemberFormSet, CreatePartyFromExistingForm
from party_calculator.models import Food, Party
from party_calculator.services.calculator import calculate
from party_calculator.services.food import FoodService
from party_calculator.services.member import MemberService
from party_calculator.services.order import OrderService
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService
from party_calculator.views import HomeView
from party_calculator_auth.models import Profile


class PartyView(PartyMemberPermission, TemplateView):
    name = 'party'

    template_name = 'party.html'

    def get_context_data(self, party_id: int, **kwargs):
        context = super().get_context_data(**kwargs)
        party_service = PartyService()

        user = self.request.user
        party = party_service.get(id=party_id)
        members = party_service.get_party_members(party)
        current_member = MemberService().get(profile_id=user.id,
                                             party_id=party_id)
        ordered_food = party_service.get_party_ordered_food(party)

        calculate(ordered_food, members)

        context['party'] = party
        context['is_active'] = party_service.is_active(party)
        context['has_template'] = party_service.has_template(party)
        context['members'] = members
        context['current_member'] = current_member
        context['ordered_food'] = ordered_food

        context['food'] = Food.objects.all()

        context[AddMemberToPartyForm.form_name] = AddMemberToPartyForm(party=party)
        context[AddCustomFoodToPartyForm.form_name] = AddCustomFoodToPartyForm(party=party)
        context[SponsorPartyForm.form_name] = SponsorPartyForm(member=current_member)

        return context


class PartyCreateView(View):
    name = 'party-create'

    def post(self, request):
        create_party_form = CreatePartyForm(request.POST, user=request.user)
        members_form = PartyMemberFormSet(request.POST, user=request.user)

        if not create_party_form.is_valid():
            errors = get_form_errors_as_str(create_party_form)
            messages.error(request, errors)
            return redirect(reverse(HomeView.name))
        elif not members_form.is_valid():
            errors = get_formset_errors_as_str(members_form)
            messages.error(request, errors)
            return redirect(reverse(HomeView.name))
        else:
            name = create_party_form.cleaned_data.get('name')
            creator = ProfileService().get(id=request.user.id)
            members = []
            for form in members_form:
                profile = form.cleaned_data.get('profile')
                if profile:
                    members.append(profile)

            party = PartyService().create(name=name, creator=creator, members=members)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party.id}))


class PartyCreateFromExisting(View):
    name = 'party-create-from-existing'

    def post(self, request):
        form = CreatePartyFromExistingForm(request.POST, user=request.user)
        if not form.is_valid():
            errors = get_form_errors_as_str(form)
            messages.error(request, errors)
            return redirect(reverse(HomeView.name))

        party = form.save()
        return redirect(reverse(PartyView.name, kwargs={'party_id': party.id}))


class PartyDelete(View):
    name = 'party-delete'

    def post(self, request, party_id: int):
        party = PartyService().get(id=party_id)
        PartyService().delete(party)

        return redirect(reverse(HomeView.name))


class PartyAddFood(PartyAdminPermission, View):
    name = 'party-add-food'

    def post(self, request, party_id: int):
        food_id = int(request.POST.get('food'))
        quantity = abs(int(request.POST.get('quantity')))

        party = PartyService().get(id=party_id)
        food = FoodService().get(id=food_id)
        PartyService().order_food(party, food, quantity)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))


class PartyAddCustomFood(PartyAdminPermission, View):
    name = 'party-add-custom-food'

    def post(self, request, party_id: int, **kwargs):
        party = PartyService().get(id=party_id)
        form = AddCustomFoodToPartyForm(request.POST, party=party)

        if not form.is_valid():
            errors = get_form_errors_as_str(form)
            messages.error(request, errors)
        else:
            form.save()

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))


class PartyRemoveFood(PartyAdminPermission, View):
    name = 'party-remove-food'

    def post(self, request, party_id: int, **kwargs):
        order_item_id = int(request.POST.get('order_item'))

        order_item = OrderService().get(id=order_item_id)
        PartyService().remove_from_order(order_item)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))


class PartyExcludeFood(PartyMemberPermission, View):
    name = 'exclude-food'

    def post(self, request, party_id: int, **kwargs):
        order_item_id = int(request.POST.get('order_item'))
        user_id = request.user.id

        profile = ProfileService().get(id=user_id)
        order_item = OrderService().get(id=order_item_id)
        MemberService().member_exclude_food(profile, order_item)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))


class PartyIncludeFood(PartyMemberPermission, View):
    name = 'include-food'

    def post(self, request, party_id: int, **kwargs):
        order_item_id = int(request.POST.get('order_item'))
        user_id = request.user.id

        profile = ProfileService().get(id=user_id)
        order_item = OrderService().get(id=order_item_id)
        MemberService().member_include_food(profile, order_item)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))


class PartyInvite(PartyAdminPermission, View):
    name = 'party-invite-member'

    def post(self, request, party_id: int):
        ps = PartyService()
        party = ps.get(id=party_id)

        form = AddMemberToPartyForm(request.POST, party=party)
        if not form.is_valid():
            errors = get_form_errors_as_str(form)
            messages.error(request, errors)
        else:
            info = form.cleaned_data.get('info')
            message_level = messages.ERROR
            try:
                ps.invite_member(party, info)
                message = 'User successfully invited'
                message_level = messages.SUCCESS
            except Profile.DoesNotExist:
                message = 'Such user does not found'
            except MemberAlreadyInPartyException:
                message = 'This member is already in party'

            messages.add_message(request, message_level, message)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))


class PartyKickMember(PartyAdminPermission, View):
    name = 'party-kick-member'

    def post(self, request, party_id: int, **kwargs):
        member_id = request.POST.get('member')
        member = MemberService().get(id=member_id)
        PartyService().remove_member_from_party(member)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))


class PartySponsor(PartyMemberPermission, View):
    name = 'party-sponsor'

    def post(self, request, party_id: int, **kwargs):
        profile = ProfileService().get(id=request.user.id)
        party = PartyService().get(id=party_id)
        member = MemberService().get(party=party, profile=profile)

        form = SponsorPartyForm(request.POST, member=member)
        if not form.is_valid():
            errors = get_form_errors_as_str(form)
            messages.error(request, errors)
        else:
            amount = form.cleaned_data.get('amount')
            PartyService().sponsor_party(member, amount)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))


class PartyMakeInactive(PartyAdminPermission, View):
    name = 'party-set-inactive'

    def post(self, request, party_id: int, **kwargs):
        party = PartyService().get(id=party_id)
        PartyService().set_state(party, Party.INACTIVE)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))


class PartyGrantOwnership(PartyAdminPermission, View):
    name = 'party-grant-ownership'

    def post(self, request, party_id: int, **kwargs):
        member_id = request.POST.get('member')
        member = MemberService().get(id=member_id)
        MemberService().set_owner(member, True)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))


class PartyRevokeOwnership(View):
    name = 'party-revoke-ownership'

    def post(self, request, party_id: int, **kwargs):
        member_id = request.POST.get('member')
        member = MemberService().get(id=member_id)
        MemberService().set_owner(member, False)

        return redirect(reverse(PartyView.name, kwargs={'party_id': party_id}))
