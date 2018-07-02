from django.views.generic import TemplateView

from party_calculator.forms import CreatePartyForm, CreatePartyFromExistingForm, PartyMemberFormSet
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