from party_calculator.exceptions import OAuthException
from party_calculator_auth.models import Profile


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    username = details['username']
    if not username:
        raise OAuthException(
            "Profile instance for user can`t be created. Not enough data"
        )

    profile = Profile.objects.create(username=username)
    profile.set_password('test')
    profile.save()

    return {
        'is_new': True,
        'user': profile
    }