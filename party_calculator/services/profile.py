from authModule.models import Profile, Code
from party_calculator.common.service import Service


class ProfileService(Service):

  model = Profile

  def get(self, **kwargs) -> model:
    try:
      result = super(ProfileService, self).get(**kwargs)
    except Profile.DoesNotExist:
      result = None

    return result

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
