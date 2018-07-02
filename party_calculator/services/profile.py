from django.core.exceptions import ValidationError

from party_calculator.common.service import Service
from party_calculator_auth.models import Profile, Code


class ProfileService(Service):
    model = Profile

    def get(self, **kwargs) -> Profile:
        try:
            result = super(ProfileService, self).get(**kwargs)
        except Profile.DoesNotExist:
            result = None

        return result

    def get_profile_parties(self, profile: Profile):
        return profile.member_of.all()

    def get_profile_administrated_parties(self, profile: Profile):
        return profile.membership_set.filter(is_owner=True)

    def activate_profile(self, uuid) -> bool:
        try:
            code: Code = Code.objects.get(code=uuid)
        except (ValidationError, Code.DoesNotExist):
            raise

        profile: Profile = code.profile

        if profile.is_active:
            return False

        profile.is_active = True
        profile.save()

        return True
