from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from party_calculator.common.party import PartyMemberPermission, PartyAdminPermission
from party_calculator.forms import CreatePartyForm, AddToPartyForm
from party_calculator.models import Food

from party_calculator.services.calculator import calculate
from party_calculator.services.food import FoodService
from party_calculator.services.member import MemberService
from party_calculator.services.order import OrderService
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService


class HomeView(TemplateView):
  template_name = 'home.html'

  def get_context_data(self, **kwargs):
    context = {}
    if self.request.user.is_authenticated:
      profile = ProfileService().get(id=self.request.user.id)
      context['parties'] = ProfileService().get_profile_parties(profile)
      context['adm_parties'] = ProfileService().get_profile_administrated_parties(profile)
      context['form'] = CreatePartyForm()

    return context


class PartyView(PartyMemberPermission, TemplateView):
  template_name = 'party.html'

  def get_context_data(self, party_id: int):
    context = {}

    party = PartyService().get(id=party_id)
    members = PartyService().get_party_members(party)
    ordered_food = PartyService().get_party_ordered_food(party)

    calculate(ordered_food, members)

    context['party'] = party
    context['members'] = members
    context['current_member'] = MemberService().get(profile_id=self.request.user.id, party_id=party_id)
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

    party = PartyService().get(id=party_id)
    food = FoodService().get(id=food_id)
    PartyService().order_food(party, food, quantity)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyRemoveFood(PartyAdminPermission, View):
  def get(self, request, **kwargs):
    order_item_id = int(request.GET.get('order_item'))

    order_item = OrderService().get(id=order_item_id)
    PartyService().remove_from_order(order_item)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyExcludeFood(PartyMemberPermission, View):
  def get(self, request, **kwargs):
    order_item_id = int(request.GET.get('order_item'))
    user_id = request.user.id

    profile = ProfileService().get(id=user_id)
    order_item = OrderService().get(id=order_item_id)
    MemberService().member_exclude_food(profile, order_item)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyIncludeFood(PartyMemberPermission, View):
  def get(self, request, **kwargs):
    order_item_id = int(request.GET.get('order_item'))
    user_id = request.user.id

    profile = ProfileService().get(id=user_id)
    order_item = OrderService().get(id=order_item_id)
    MemberService().member_include_food(profile, order_item)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyInvite(PartyAdminPermission, View):
  def get(self, request, party_id: int):
    info = request.GET.get('info')

    ps = PartyService()
    party = ps.get(id=party_id)
    message = ps.invite_member(party, info)

    return HttpResponse(message)


class PartyKickMember(PartyAdminPermission, View):
  def get(self, request, **kwargs):
    member_id = request.GET.get('member')
    member = MemberService().get(id=member_id)
    PartyService().remove_member_from_party(member)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartySponsor(PartyMemberPermission, View):
  def get(self, request, **kwargs):
    amount = float(request.GET.get('amount'))
    member_id = request.GET.get('member')

    member = MemberService().get(id=member_id)
    MemberService().sponsor_party(member, amount)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))