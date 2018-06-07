from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

from party_calculator.services.member import MemberService
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService


def logged_in(func):
  def wrapper(*args, **kwargs):
    if not args[0].request.user.is_authenticated:
      return False
    else:
      return func(*args, **kwargs)

  return wrapper


def is_active(func):
  def wrapper(*args, **kwargs):
    party_id = kwargs.get('party_id')

    ps = PartyService()
    party = ps.get(id=party_id)
    if not ps.is_active(party):
      raise PermissionDenied("You cannot modify inactive party")
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
    profile = ProfileService().get(id=self.request.user.id)
    party = PartyService().get(id=party_id)

    if not MemberService().is_party_member(profile, party):
      raise PermissionDenied("You are not a member of this party")
    return True


class PartyAdminPermission(UserPassesTestMixin):
  login_url = reverse_lazy('login')

  @logged_in
  def test_func(self):
    party_id = self.kwargs.get('party_id')
    return self.check_adminship(party_id)

  def check_adminship(self, party_id):
    profile = ProfileService().get(id=self.request.user.id)
    party = PartyService().get(id=party_id)
    if not MemberService().is_party_admin(profile, party):
      raise PermissionDenied("You are neither admin or owner of this party")
    return True

