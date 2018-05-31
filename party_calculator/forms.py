from django import forms

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


  def save(self, commit=True) -> Party:
    name = self.cleaned_data.get('name')
    members = self.cleaned_data.get('members')

    creator = Profile.objects.get(id=self.user.id)

    party: Party = Party.objects.create(name=name, created_by=creator)

    for member in members:
      membership: Membership = Membership.objects.create(profile=member, party=party)

      if member == creator:
        membership.is_owner = True

      membership.save()

    return party