from authModule.models import Profile


def get_profile_by_request(request) -> Profile:
  # TODO: Handle anonymous, actually anonymous can do nothing.
  return Profile.objects.get(id=request.user.id)


def get_profile_parties(profile: Profile):
  return profile.membership_set.all()


def get_profile_administrated_parties(profile: Profile):
  profile.membership_set.filter(is_owner=True)