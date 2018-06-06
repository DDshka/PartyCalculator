from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets

from authModule.models import Profile
from party_calculator.models import Party, Membership


class CreatePartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('name', 'members')

    user = None

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(CreatePartyForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Party.objects.filter(name=name).exists():
            raise ValidationError("There can`t be two parties with the same name")

        return name

    def save(self, commit=True) -> Party:
        name = self.cleaned_data.get('name')
        members = self.cleaned_data.get('members')

        creator = Profile.objects.get(id=self.user.id)

        party: Party = Party.objects.create(name=name, created_by=creator)
        Membership.objects.create(profile=creator, party=party, is_owner=True)

        for member in members:
            Membership.objects.create(profile=member, party=party)

        return party


class AddToPartyForm(forms.Form):
    userinfo = forms.CharField(max_length=1024, label='User', widget=widgets.TextInput(
        attrs={'placeholder': 'Enter here either username or his email'}))
