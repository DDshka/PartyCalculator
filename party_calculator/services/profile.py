from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404

from authModule.models import Profile, Code


class ProfileService:
  def get_by_id(self, profile_id: int) -> Profile:
    return Profile.objects.get(id=profile_id)

  def get_profile_parties(self, profile: Profile):
    return profile.memberships.all()

  def get_profile_administrated_parties(self, profile: Profile):
    return profile.membership_set.filter(is_owner=True)

  def activate_profile(self, uuid) -> bool:
    try:
      code: Code = Code.objects.get(code=uuid)
    except Code.DoesNotExist:
      return False

    profile: Profile = code.profile

    if profile.is_active:
      return False

    profile.is_active = True
    profile.save()

    return True
