from django import forms

from party_calculator.models import Party


class CreatePartyForm(forms.ModelForm):
  class Meta:
    model = Party
    fields = ('name', 'members')

  user = None

  def __init__(self, user=None, *args, **kwargs):
    self.user = user
    super(CreatePartyForm, self).__init__(*args, **kwargs)


  def save(self, commit=True) -> Party:
    party: Party = super(CreatePartyForm, self).save(False)
    party.created_by = self.user

    return party