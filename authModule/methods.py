from django.contrib.auth import authenticate, login

from authModule.models import Profile


def auth_user(request, username, password) -> Profile:
  user = authenticate(request, username=username, password=password)
  if user is not None:
    login(request, user)

  return user
