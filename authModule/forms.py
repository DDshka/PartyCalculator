from django import forms

from authModule.models import Profile


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

    from .methods import auth_user
    username = self.cleaned_data.get('username')
    password = self.cleaned_data.get('password')
    logged = auth_user(self.request, username, password)

    if not logged:
      from django.core.exceptions import ValidationError
      raise ValidationError('Wrong authentication. Provided data may be wrong or such user simply does not exist')


class SignInForm(forms.ModelForm):
  class Meta:
    model = Profile
    fields = ('username', 'password', 'email',)

  def save(self, commit=True):
    user = super(SignInForm, self).save(commit=False)
    user.set_password(self.cleaned_data['password'])
    user.save()

    return user