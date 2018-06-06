from authModule.models import Profile, Code


# todo tis method returns multiple object types AuthUser and Profile
def get_profile_by_request(request) -> Profile:
    # TODO: Handle anonymous, actually anonymous can do nothing.
    try:
        return Profile.objects.get(id=request.user.id)
    except Profile.DoesNotExist:
        return request.user


def get_profile_parties(profile: Profile):
    return profile.memberships.all()


def get_profile_administrated_parties(profile: Profile):
    return profile.membership_set.filter(is_owner=True)


# todo method doesn't actually do what it should be
def verify_profile(uuid) -> bool:
    try:
        code: Code = Code.objects.get(code=uuid)
    except Code.DoesNotExist:
        return False

    profile: Profile = code.profile

    profile.is_active = True
    profile.save()

    return True
