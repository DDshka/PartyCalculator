from authModule.models import Profile, Code


class ProfileService:
  def get_by_id(self, profile_id: int) -> Profile:
    return Profile.objects.get(id=profile_id)

  def get_by_email(self, email: str) -> Profile:
    try:
      result = Profile.objects.get(email=email)
    except Profile.DoesNotExist:
      result = None

    return result

  def get_by_username(self, username: str) -> Profile:
    try:
      result = Profile.objects.get(username=username)
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
