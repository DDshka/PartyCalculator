from django.contrib.auth import authenticate, login

from authModule.models import Profile


def auth_user(request, username, password):
  user: Profile = authenticate(request, username=username, password=password)
  if user is not None and user.is_active:
    login(request, user)
  else:
    return None

  return user
