import json
import urllib

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse

from PartyCalculator.settings import CAPTCHA_ENABLED
from party_calculator.tasks import send_mail
from party_calculator_auth.models import Profile, Code


class LoginForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('username', 'password',)

    form_name = 'login_form'

    def __init__(self, request=None, *args, **kwargs):
        self.request = request

        if request:
            super(LoginForm, self).__init__(data=request.POST, *args, **kwargs)
        else:
            super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].help_text = None
        self.fields['password'].widget = forms.PasswordInput()

    def clean(self):
        super(LoginForm, self)

        check_captcha(self.request)

        from party_calculator_auth.services.auth import auth_user
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        # TODO: raise exceptions (NoSuchUser, ProfileInactive) in auth_user and handle here
        logged = auth_user(self.request, username, password)

        if not logged:
            raise ValidationError('Wrong authentication. '
                                  'Provided data may be wrong or such user simply does not exist,'
                                  'or this profile has not been activated')


class SignInForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('username', 'password', 'email',)

    form_name = 'signin_form'

    def __init__(self, request=None, *args, **kwargs):
        self.request = request

        if request:
            super(SignInForm, self).__init__(data=request.POST, *args, **kwargs)
        else:
            super(SignInForm, self).__init__(*args, **kwargs)

        self.fields['username'].help_text = None
        self.fields['password'].widget = forms.PasswordInput()

    def clean(self):
        super(SignInForm, self)
        check_captcha(self.request)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Profile.objects.filter(username=username).exists():
            raise ValidationError("User with such name already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Profile.objects.filter(email=email).exists():
            raise ValidationError("User with such email address already exists")
        return email

    def save(self, commit=True):
        user = super(SignInForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = False

        user.verification = Code.objects.create()

        from PartyCalculator.production_settings import HOST, WEBSITE_URL
        from party_calculator_auth.views import VerificationView
        verification_url = reverse(VerificationView.name,
                                   kwargs={'verification_code': user.verification.code})
        send_mail.delay("Party calculator: Activation code",
                        "Proceed this link to make your profile active and start becoming drunk\n"
                        "{0}{1}".format(WEBSITE_URL, verification_url),
                        "admin@{0}".format(HOST),
                        [user.email])

        user.save()

        return user


def check_captcha(request):
    if CAPTCHA_ENABLED:
        ''' Begin reCAPTCHA validation '''
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        from PartyCalculator import settings
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        ''' End reCAPTCHA validation '''

        if not result['success']:
            raise ValidationError("Bad captcha. Try again")