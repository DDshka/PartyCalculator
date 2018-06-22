from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView

from party_calculator.common.party import PartyMemberPermission, PartyAdminPermission
from party_calculator.exceptions import MemberAlreadyInPartyException
from party_calculator.forms import CreatePartyForm, AddMemberToPartyForm, CreatePartyFromExistingForm, \
    CreateTemplateForm
from party_calculator.models import Food, TemplateParty, Party
from party_calculator.services.calculator import calculate
from party_calculator.services.food import FoodService
from party_calculator.services.member import MemberService
from party_calculator.services.order import OrderService
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService
from party_calculator.services.template_member import TemplateMemberService
from party_calculator.services.template_order import TemplateOrderService
from party_calculator.services.template_party import TemplatePartyService
from party_calculator_auth.models import Profile


class HomeView(TemplateView):
    name = 'home'

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = {}
        profile_service = ProfileService()

        if self.request.user.is_authenticated:
            profile = profile_service.get(id=self.request.user.id)
            context['parties'] = profile_service.get_profile_parties(profile)
            context['adm_parties'] = profile_service.get_profile_administrated_parties(profile)
            context['create_party_form'] = CreatePartyForm(user=self.request.user)
            context['create_party_from_existing_form'] = CreatePartyFromExistingForm(user=self.request.user)

        return context


class PartyView(PartyMemberPermission, TemplateView):
    name = 'party'

    template_name = 'party.html'

    def get_context_data(self, party_id: int, **kwargs):
        context = {}
        party_service = PartyService()

        user = self.request.user
        party = party_service.get(id=party_id)
        members = party_service.get_party_members(party)
        ordered_food = party_service.get_party_ordered_food(party)

        calculate(ordered_food, members)

        context['party'] = party
        context['is_active'] = party_service.is_active(party)
        context['has_template'] = party_service.has_template(party)
        context['members'] = members
        context['current_member'] = MemberService().get(profile_id=user.id,
                                                        party_id=party_id)
        context['ordered_food'] = ordered_food

        context['food'] = Food.objects.all()
        context['add_to_party_form'] = AddMemberToPartyForm()

        return context


class PartyCreateView(View):
    name = 'create-party'

    def post(self, request):
        form = CreatePartyForm(request.POST, user=request.user)
        if not form.is_valid():
            # TODO: handle party creation form errors
            return redirect(reverse('home'))

        party = form.save()
        return redirect(reverse('party', kwargs={'party_id': party.id}))


class PartyCreateFromExisting(View):
    name = 'create-party-from-existing'

    def post(self, request):
        form = CreatePartyFromExistingForm(request.POST, user=request.user)
        if not form.is_valid():
            return redirect(reverse('home'))

        party = form.save()
        return redirect(reverse('party', kwargs={'party_id': party.id}))


class PartyDelete(View):
    name = 'delete-party'

    def get(self, request, party_id: int):
        party = PartyService().get(id=party_id)
        PartyService().delete(party)


class PartyAddFood(PartyAdminPermission, View):
    name = 'add-food-to-party'

    def get(self, request, party_id: int):
        food_id = int(request.GET.get('food'))
        quantity = int(request.GET.get('quantity'))

        party = PartyService().get(id=party_id)
        food = FoodService().get(id=food_id)
        PartyService().order_food(party, food, quantity)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyRemoveFood(PartyAdminPermission, View):
    name = 'remove-food-from-party'

    def get(self, request, **kwargs):
        order_item_id = int(request.GET.get('order_item'))

        order_item = OrderService().get(id=order_item_id)
        PartyService().remove_from_order(order_item)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyExcludeFood(PartyMemberPermission, View):
    name = 'exclude-food'

    def get(self, request, **kwargs):
        order_item_id = int(request.GET.get('order_item'))
        user_id = request.user.id

        profile = ProfileService().get(id=user_id)
        order_item = OrderService().get(id=order_item_id)
        MemberService().member_exclude_food(profile, order_item)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyIncludeFood(PartyMemberPermission, View):
    name = 'include-food'

    def get(self, request, **kwargs):
        order_item_id = int(request.GET.get('order_item'))
        user_id = request.user.id

        profile = ProfileService().get(id=user_id)
        order_item = OrderService().get(id=order_item_id)
        MemberService().member_include_food(profile, order_item)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyInvite(PartyAdminPermission, View):
    name = 'invite-member'

    def get(self, request, party_id: int):
        info = request.GET.get('info')

        ps = PartyService()
        party = ps.get(id=party_id)

        message = 'User successfully invited'
        try:
            ps.invite_member(party, info)
        except Profile.DoesNotExist:
            message = 'Such user does not found'
        except MemberAlreadyInPartyException:
            message = 'This member is already in party'

        return HttpResponse(message)


class PartyKickMember(PartyAdminPermission, View):
    name = 'kick-member'

    def get(self, request, **kwargs):
        member_id = request.GET.get('member')
        member = MemberService().get(id=member_id)
        PartyService().remove_member_from_party(member)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartySponsor(PartyMemberPermission, View):
    name = 'sponsor-party'

    def get(self, request, **kwargs):
        amount = float(request.GET.get('amount'))
        member_id = request.GET.get('member')

        member = MemberService().get(id=member_id)
        PartyService().sponsor_party(member, amount)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyMakeInactive(PartyAdminPermission, View):
    name = 'party-set-inactive'

    def get(self, request, party_id: int):
        party = PartyService().get(id=party_id)
        PartyService().set_state(party, Party.INACTIVE)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# ---------------------------------


class TemplatesListView(ListView):
    name = 'templates'
    template_name = 'templates_list.html'
    context_object_name = 'templates'

    def get_queryset(self):
        return TemplatePartyService().filter(created_by=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TemplatesListView, self).get_context_data(object_list=object_list, **kwargs)
        context['create_template_form'] = CreateTemplateForm(user=self.request.user)

        return context


class TemplateCreate(View):
    name = 'create-template'

    def post(self, request):
        form = CreateTemplateForm(request.POST, user=request.user)
        if not form.is_valid():
            # TODO: handle template creation form errors
            return redirect(reverse('home'))

        template_party = form.save()
        return redirect(reverse('template', kwargs={'template_id': template_party.id}))


class TemplateCreateFromParty(View):
    name = 'create-template-from-party'

    def post(self, request, party_id: int):
        party = PartyService().get(id=party_id)
        template_party = TemplatePartyService().create_from_existing(party)
        return redirect(reverse('template', kwargs={'template_id': template_party.id}))


class TemplateDelete(View):
    name = 'delete-template'

    def get(self, request, template_id: int):
        party = TemplatePartyService().get(id=template_id)
        TemplatePartyService().delete(party)


class TemplatePartyView(TemplateView):
    name = 'template'
    template_name = 'party_template.html'

    def get_context_data(self, template_id, **kwargs):
        context = {}

        template_party = TemplatePartyService().get(id=template_id)
        template_members = TemplatePartyService().get_template_members(template_party)
        template_ordered_food = TemplatePartyService().get_template_ordered_food(template_party)

        context['template'] = template_party
        context['is_active'] = TemplatePartyService().is_active(template_party)
        context['members'] = template_members
        context['ordered_food'] = template_ordered_food

        context['food'] = Food.objects.all()
        context['add_to_party_form'] = AddMemberToPartyForm()

        return context


class TemplateAddMemberView(View):
    name = 'template-add-member'

    def get(self, request, template_id, **kwargs):
        info = request.GET.get('info')

        ps = TemplatePartyService()
        party = ps.get(id=template_id)

        try:
            ps.add_member_to_template(party, info)
        except Profile.DoesNotExist:
            message = 'Such user does not found'
            return HttpResponse(message)
        except MemberAlreadyInPartyException:
            message = 'This member is already in template'
            return HttpResponse(message)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class TemplateKickMember(View):
    name = 'template-kick-member'

    def get(self, request, **kwargs):
        member_id = request.GET.get('member')
        member = TemplateMemberService().get(id=member_id)
        TemplatePartyService().remove_member_from_template(member)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class TemplateAddFood(View):
    name = 'template-add-food'

    def get(self, request, template_id: int):
        food_id = int(request.GET.get('food'))
        quantity = int(request.GET.get('quantity'))

        party = TemplatePartyService().get(id=template_id)
        food = FoodService().get(id=food_id)
        TemplatePartyService().order_food(party, food, quantity)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class TemplateSetInactive(View):
    name = 'template-set-inactive'

    def get(self, request, template_id: int):
        party = TemplatePartyService().get(id=template_id)
        TemplatePartyService().set_state(party, TemplateParty.INACTIVE)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class TemplateSetActive(View):
    name = 'template-set-active'

    def get(self, request, template_id: int):
        party = TemplatePartyService().get(id=template_id)
        TemplatePartyService().set_state(party, TemplateParty.ACTIVE)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class TemplateGrantOwnership(View):
    name = 'template-grant-ownership'

    def get(self, request, **kwargs):
        member_id = request.GET.get('member')
        member = TemplateMemberService().get(id=member_id)
        TemplateMemberService().grant_ownership(member)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class TemplateRevokeOwnership(View):
    name = 'template-revoke-ownership'

    def get(self, request, **kwargs):
        member_id = request.GET.get('member')
        member = TemplateMemberService().get(id=member_id)
        TemplateMemberService().revoke_ownership(member)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class TemplateRemoveFood(View):
    name = 'template-remove-food'

    def get(self, request, **kwargs):
        order_item_id = int(request.GET.get('order_item'))

        order_item = TemplateOrderService().get(id=order_item_id)
        TemplatePartyService().remove_from_order(order_item)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class TemplateSetFrequency(View):
    name = 'template-set-frequency'

    def get(self, request, template_id:int, **kwargs):
        pattern: str = request.GET.get('pattern')

        template = TemplatePartyService().get(id=template_id)
        TemplatePartyService().set_frequency(template, pattern)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class OmegaLul(View):
    name = 'create-party-from-template'

    def post(self, request, **kwargs):
        template_id = request.POST.get('template')
        template = TemplatePartyService().get(id=template_id)

        PartyService().create_from_template(template)

        return HttpResponse('ZDAROVA')