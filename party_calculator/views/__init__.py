from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.base import View

from party_calculator.adyen_api import make_bin_verification
from party_calculator.forms import CreatePartyForm, CreatePartyFromExistingForm, PartyMemberFormSet
from party_calculator.services.card import AdyenCardService
from party_calculator.services.profile import ProfileService


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

            context[CreatePartyForm.form_name] = CreatePartyForm(user=self.request.user)
            context[CreatePartyFromExistingForm.form_name] = CreatePartyFromExistingForm(user=self.request.user)

            context['formset'] = PartyMemberFormSet()

        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    name = 'profile'

    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        user = self.request.user
        profile = ProfileService().get(id=user.id)

        context['profile'] = profile
        context['cards'] = AdyenCardService().get_all_cards(profile)

        return context


class CardAdd(View):
    name = 'card-add'

    def post(self, request):
        encrypted_card_data = self.request.POST.get('adyen-encrypted-data')
        make_bin_verification(request, encrypted_card_data)

        return redirect(reverse(ProfileView.name))


class CardUpdate(TemplateView):
    name = 'card-update'

    template_name = 'update_card_info.html'

    def get_context_data(self, recurring_detail_reference, **kwargs):
        context = super(CardUpdate, self).get_context_data(**kwargs)

        context['recurring_detail_reference'] = recurring_detail_reference

        return context

    def post(self, request, recurring_detail_reference, **kwargs):
        card = {
            "expiryMonth": request.POST.get('expiryMonth'),
            "expiryYear": request.POST.get('expiryYear')
        }

        AdyenCardService().update_card(request, card, recurring_detail_reference)

        return redirect(reverse(ProfileView.name))


class CardDelete(View):
    name = 'card-delete'

    def get(self, request, recurring_detail_reference, **kwargs):
        profile = ProfileService().get(id=request.user.id)

        AdyenCardService().delete_card(profile, recurring_detail_reference)

        return redirect(reverse(ProfileView.name))