import json
import urllib

from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse_lazy, reverse

from authModule.models import Profile, Code


class LoginForm(forms.ModelForm):
  class Meta:
    model = Profile
    fields = ('username', 'password',)

  request = None

  def __init__(self, *args, **kwargs):
    if args:
      request = args[0]
      self.request = request
      super(LoginForm, self).__init__(request.POST, **kwargs)
    else:
      super(LoginForm, self).__init__(*args, **kwargs)

  def clean(self):
    super(LoginForm, self)

    ''' Begin reCAPTCHA validation '''
    recaptcha_response = self.request.POST.get('g-recaptcha-response')
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

    from .methods import auth_user
    username = self.cleaned_data.get('username')
    password = self.cleaned_data.get('password')
    logged = auth_user(self.request, username, password)

    if not logged:
      raise ValidationError('Wrong authentication. Provided data may be wrong or such user simply does not exist')


class SignInForm(forms.ModelForm):
  class Meta:
    model = Profile
    fields = ('username', 'password', 'email',)

  def save(self, commit=True):
    user = super(SignInForm, self).save(commit=False)
    user.set_password(self.cleaned_data['password'])
    user.is_active = False

    user.verification = Code.objects.create()

    from PartyCalculator.settings import HOST, WEBSITE_URL
    verification_url = reverse('verification', kwargs={'verification_code': user.verification.code })
    send_mail("Party calculator: Activation code",
              "Proceed this link to make your profile active and start becoming drunk\n"
              "{0}{1}".format(WEBSITE_URL, verification_url),
              "admin@{0}".format(HOST),
              [user.email])

    user.save()

    return user