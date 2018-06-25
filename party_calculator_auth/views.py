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

from PartyCalculator.settings import GOOGLE_RECAPTCHA_SITE_KEY, CAPTCHA_ENABLED
from party_calculator.services.profile import ProfileService
from party_calculator_auth.forms import LoginForm, SignInForm
from party_calculator_auth.models import Profile


class LoginView(View):
    name = 'login'
    template_name = 'login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('home'))

        return render(request, self.template_name, self.get_context_data())

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('home'))

        form = LoginForm(request)
        if not form.is_valid():
            kwargs = {
                LoginForm.form_name: form
            }
            return render(request, self.template_name, self.get_context_data(**kwargs))

        if request.GET.get('next'):
            return HttpResponseRedirect(request.GET.get('next'))

        return redirect(reverse_lazy('home'))

    def get_context_data(self, **kwargs):
        context = {}

        try:
            context[LoginForm.form_name] = kwargs[LoginForm.form_name]
        except KeyError:
            context[LoginForm.form_name] = LoginForm()

        context['captcha_enabled'] = CAPTCHA_ENABLED
        context['google_recaptcha_site_key'] = GOOGLE_RECAPTCHA_SITE_KEY

        return context


class SignInView(CreateView):
    name = 'sign-in'
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

        form = SignInForm(request)
        if not form.is_valid():
            kwargs = {
                SignInForm.form_name: form
            }
            return render_to_response(self.template_name, self.get_context_data(**kwargs))

        form.save()
        return redirect(reverse_lazy('home'))

    def get_context_data(self, **kwargs):
        context = {}

        try:
            context[SignInForm.form_name] = kwargs[SignInForm.form_name]
        except KeyError:
            context[SignInForm.form_name] = SignInForm()

        context['captcha_enabled'] = CAPTCHA_ENABLED
        context['google_recaptcha_site_key'] = GOOGLE_RECAPTCHA_SITE_KEY

        return context


class LogoutView(View):
    name = 'logout'

    def get(self, request):
        logout(request)

        return redirect(reverse_lazy('home'))


class VerificationView(View):
    name = 'verification'

    def get(self, request, verification_code):
        verified = ProfileService().activate_profile(verification_code)

        if not verified:
            return HttpResponse("It seems your profile has been already activated")

        return HttpResponse("Your profile has been successfully activated.")


# TODO: recode settings and password methods as classbased views
# ====================================================================================


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
