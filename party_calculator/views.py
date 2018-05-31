from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView

from party_calculator.abstracts.party import PartyMemberPermission
from party_calculator.forms import CreatePartyForm
from party_calculator.models import Food

from party_calculator.services.calculator import calculate
from party_calculator.services.party import get_party_by_id, get_party_members, get_party_ordered_food, \
  party_order_food, member_exclude_food, member_include_food, party_remove_from_order
from party_calculator.services.profile import get_profile_by_request, get_profile_parties, \
  get_profile_administrated_parties


class HomeView(TemplateView):
  template_name = 'home.html'

  def get_context_data(self, **kwargs):
    context = {}
    if self.request.user.is_authenticated:
      profile = get_profile_by_request(self.request)
      context['parties'] = get_profile_parties(profile)
      context['adm_parties'] = get_profile_administrated_parties(profile)
      context['form'] = CreatePartyForm()

    return context


class PartyView(PartyMemberPermission, TemplateView):
  template_name = 'party.html'

  def get_context_data(self, id:int):
    context = {}

    party = get_party_by_id(id)
    members = get_party_members(party)
    ordered_food = get_party_ordered_food(party)

    calculate(ordered_food, members)

    context['party'] = party
    context['members'] = members
    context['ordered_food'] = ordered_food

    context['food'] = Food.objects.all()

    return context


class CreatePartyView(View):
  def get(self, request):
    pass

  def post(self, request):
    form = CreatePartyForm(request.user, request.POST)
    if form.is_valid():
      form.save(False)


class PartyAddFood(View):
  def get(self, request):
    food_id = int(request.GET.get('food'))
    party_id = int(request.GET.get('party'))
    quantity = int(request.GET.get('quantity'))

    # TODO: CHECK THROUGH DECORATOR!!11
    user = get_profile_by_request(request)
    party = get_party_by_id(party_id)
    if not user.membership_set.get(party=party):
      return HttpResponse("You can`t add food to a party which you are not membered in")

    party_order_food(party_id, food_id, quantity)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyExcludeFood(PartyMemberPermission, View):
  def get(self, request):
    order_item_id = int(request.GET.get('order_item'))

    member_exclude_food(request, order_item_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyIncludeFood(PartyMemberPermission, View):
  def get(self, request):
    order_item_id = int(request.GET.get('order_item'))

    member_include_food(request, order_item_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PartyRemoveFood(PartyMemberPermission, View):
  def get(self, request):
    party_id = int(request.GET.get('party'))
    order_item_id = int(request.GET.get('order_item'))

    party_remove_from_order(party_id, order_item_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

