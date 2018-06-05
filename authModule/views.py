from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from authModule.forms import LoginForm, SignInForm
from authModule.models import Profile
from party_calculator.services.profile import verify_profile


class LoginView(View):
  template_name = 'login.html'

  def get(self, request):
    if request.user.is_authenticated:
      return redirect(reverse_lazy('home'))

    return render(request, self.template_name, {'form': LoginForm()})


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

    return super(SignInView, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    if request.user.is_authenticated:
      return redirect(reverse_lazy('home'))

    return super(SignInView, self).post(request, *args, **kwargs)


class LogoutView(View):
  def get(self, request):
    logout(request)
    return redirect(reverse_lazy('home'))


class VerificationView(View):
  def get(self, request, verification_code):
    verified = verify_profile(verification_code)

    if verified:
      return HttpResponse("Your profile successfully activated.")
    else:
      return HttpResponse("It seems your profile has been already activated")

