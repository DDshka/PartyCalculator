from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from party_calculator.common.party import PartyMemberPermission, PartyAdminPermission
from party_calculator.forms import CreatePartyForm, AddToPartyForm
from party_calculator.models import Food

from party_calculator.services.calculator import calculate
from party_calculator.services.member import MemberService
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService


class HomeView(TemplateView):
  template_name = 'home.html'

  def get_context_data(self, **kwargs):
    context = {}
    if self.request.user.is_authenticated:
      profile = ProfileService().get_by_id(self.request.user.id)
      context['parties'] = ProfileService().get_profile_parties(profile)
      context['adm_parties'] = ProfileService().get_profile_administrated_parties(profile)
      context['form'] = CreatePartyForm()

    return context


class PartyView(PartyMemberPermission, TemplateView):
  template_name = 'party.html'

  def get_context_data(self, party_id: int):
    context = {}

    party = PartyService().get_by_id(party_id)
    members = PartyService().get_party_members(party)
    ordered_food = PartyService().get_party_ordered_food(party)

    calculate(ordered_food, members)

    context['party'] = party
    context['members'] = members
    context['ordered_food'] = ordered_food

    context['food'] = Food.objects.all()
    context['add_to_party_form'] = AddToPartyForm()

    return context


class CreatePartyView(View):
  def get(self, request):
    pass

  def post(self, request):
    form = CreatePartyForm(request.user, request.POST)
    if form.is_valid():
      party = form.save()
      return redirect(reverse('party', kwargs={'party_id': party.id}))
    else:
      # TODO: handle party creation form errors
      return redirect(reverse('home'))


class PartyAddFood(PartyAdminPermission, View):
  def get(self, request, party_id: int):
    food_id = int(request.GET.get('food'))
    quantity = int(request.GET.get('quantity'))

    PartyService().party_order_food(party_id, food_id, quantity)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyRemoveFood(PartyAdminPermission, View):
  def get(self, request, **kwargs):
    order_item_id = int(request.GET.get('order_item'))

    PartyService().remove_from_order(order_item_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyExcludeFood(PartyMemberPermission, View):
  def get(self, request, **kwargs):
    order_item_id = int(request.GET.get('order_item'))
    user_id = request.user.id

    MemberService().member_exclude_food(user_id, order_item_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyIncludeFood(PartyMemberPermission, View):
  def get(self, request, **kwargs):
    order_item_id = int(request.GET.get('order_item'))
    user_id = request.user.id

    MemberService().member_include_food(user_id, order_item_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyInvite(PartyAdminPermission, View):
  def get(self, request, party_id: int):
    info = request.GET.get('info')
    message = PartyService().invite_member(party_id, info)

    return HttpResponse(message)


class PartyKickMember(PartyAdminPermission, View):
  def get(self, request, **kwargs):
    member_id = request.GET.get('member')
    PartyService().remove_member_from_party(member_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))