from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from party_calculator.services.party import is_party_member, is_party_admin


def logged_in(func):
  def wrapper(*args, **kwargs):
    if not args[0].request.user.is_authenticated:
      return False
    else:
      return func(*args, **kwargs)

  return wrapper


class PartyMemberPermission(UserPassesTestMixin):
  login_url = reverse_lazy('login')

  @logged_in
  def test_func(self):
    party_id = self.kwargs.get('party_id')
    return self.check_membership(party_id)


  def check_membership(self, party_id):
    if not is_party_member(self.request, party_id):
      raise PermissionDenied("You are not a member of this party")
    return True


class PartyAdminPermission(UserPassesTestMixin):
  login_url = reverse_lazy('login')

  @logged_in
  def test_func(self):
    party_id = self.kwargs.get('party_id')
    return self.check_adminship(party_id)

  def check_adminship(self, party_id):
    if not is_party_admin(self.request, party_id):
      raise PermissionDenied("You are neither admin or owner of this party")
    return True