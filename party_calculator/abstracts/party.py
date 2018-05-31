from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from party_calculator.services.party import is_party_member

class PartyMemberPermission(UserPassesTestMixin):
  login_url = reverse_lazy('login')

  def test_func(self):
    if not self.request.user.is_authenticated:
      return False

    # TODO: KOSTYL GODA. Nado pridumat normalnuu proverku
    party_id = self.kwargs.get('id') if self.kwargs.get('id') else self.request.GET.get('party')
    return self.check_membership(party_id)


  def check_membership(self, party_id):
    if not is_party_member(self.request, party_id):
      raise PermissionDenied("You are not a member of this party")
    return True

