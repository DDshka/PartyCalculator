from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from social_django.models import UserSocialAuth

from PartyCalculator.settings import GOOGLE_RECAPTCHA_SITE_KEY
from authModule.forms import LoginForm, SignInForm
from authModule.models import Profile
from party_calculator.services.profile import verify_profile


class LoginView(View):
  template_name = 'login.html'

  def get(self, request):
    if request.user.is_authenticated:
      return redirect(reverse_lazy('home'))

    return render(request, self.template_name, {'form': LoginForm(), 'google_recaptcha_site_key': GOOGLE_RECAPTCHA_SITE_KEY})


  def post(self, request):
    if request.user.is_authenticated:
      return redirect(reverse_lazy('home'))

    form = LoginForm(request)
    if not form.is_valid():
      return render_to_response(self.template_name, {'form': form})

    if request.GET.get('next'):
      return HttpResponseRedirect(request.GET.get('next'))

    return redirect(reverse_lazy('home'))


class SignInView(CreateView):
  template_name = 'register.html'
  model = Profile
  form_class = SignInForm
  success_url = reverse_lazy('home')

  def get(self, request, *args, **kwargs):
    if request.user.is_authenticated:
      return redirect(reverse_lazy('home'))

    # TODO: PASS WITH CONTEXT GOOGLE_RECAPTCHA_SITE_KEY

    return super(SignInView, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    if request.user.is_authenticated:
      return redirect(reverse_lazy('home'))

    return super(SignInView, self).post(request, *args, **kwargs)


class LogoutView(View):
  def get(self, request):
    user = request.user
    try:
      google_login = user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
      google_login = None

    logout(request)

    # just example
    if google_login:
      import requests
      requests.post('https://accounts.google.com/o/oauth2/revoke',
                    params={'token': google_login.access_token},
                    headers={'content-type': 'application/x-www-form-urlencoded'})

    return redirect(reverse_lazy('home'))


class VerificationView(View):
  def get(self, request, verification_code):
    verified = verify_profile(verification_code)

    if verified:
      return HttpResponse("Your profile successfully activated.")
    else:
      return HttpResponse("It seems your profile has been already activated")



@login_required
def settings(request):
  user = request.user

  try:
    github_login = user.social_auth.get(provider='github')
  except UserSocialAuth.DoesNotExist:
    github_login = None

  try:
    google_login = user.social_auth.get(provider='google-oauth2')
  except UserSocialAuth.DoesNotExist:
    google_login = None

  can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

  return render(request, 'OAuth_settings.html', {
    'github_login': github_login,
    'google_login': google_login,
    'can_disconnect': can_disconnect
  })

@login_required
def password(request):
  if request.user.has_usable_password():
    PasswordForm = PasswordChangeForm
  else:
    PasswordForm = AdminPasswordChangeForm

  if request.method == 'POST':
    form = PasswordForm(request.user, request.POST)
    if form.is_valid():
      form.save()
      update_session_auth_hash(request, form.user)
      messages.success(request, 'Your password was successfully updated!')
      return redirect('password')
    else:
      messages.error(request, 'Please correct the error below.')
  else:
    form = PasswordForm(request.user)
  return render(request, 'password.html', {'form': form})
