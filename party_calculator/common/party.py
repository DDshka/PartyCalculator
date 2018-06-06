from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

from party_calculator.services.member import MemberService


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
    if not MemberService().is_party_member(self.request.user.id, party_id):
      raise PermissionDenied("You are not a member of this party")
    return True


class PartyAdminPermission(UserPassesTestMixin):
  login_url = reverse_lazy('login')

  @logged_in
  def test_func(self):
    party_id = self.kwargs.get('party_id')
    return self.check_adminship(party_id)

  def check_adminship(self, party_id):
    if not MemberService().is_party_admin(self.request.user.id, party_id):
      raise PermissionDenied("You are neither admin or owner of this party")
    return True