from django.contrib.auth import authenticate, login

from party_calculator_auth.models import Profile


def auth_user(request, username, password):
    user: Profile = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
    else:
        return None

    return user


def auth_user_by_profile(request, profile: Profile) -> None:
    login(request, profile)