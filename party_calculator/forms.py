from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets

from party_calculator.models import Party, Food, TemplateParty, OrderedFood
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService
from party_calculator.services.template_party import TemplatePartyService


class CreatePartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('name', 'members')

    user = None

    def __init__(self, *args, user=None, **kwargs):
        self.user = user

        super(CreatePartyForm, self).__init__(*args, **kwargs)

        self.fields['members'].required = False
        self.fields['members'].queryset = ProfileService().get_all(excluding={'id': self.user.id})

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Party.objects.filter(name=name).exists():
            raise ValidationError("There can`t be two parties with the same name")

        return name

    def save(self, commit=True) -> Party:
        name = self.cleaned_data.get('name')
        members = self.cleaned_data.get('members')

        creator = ProfileService().get(id=self.user.id)
        party = PartyService().create(name=name, creator=creator, members=members)

        return party


class CreatePartyFromExistingForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('name',)

    user = None

    name = forms.CharField(max_length=1024, label='Party name', widget=widgets.TextInput(
        attrs={'placeholder': 'Enter here your party name'}))
    existing_party_name = forms.CharField(max_length=1024,
                                          label='Existing party name',
                                          widget=widgets.TextInput(
                                                attrs={'placeholder': 'Enter here existing party name '}))

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super(CreatePartyFromExistingForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Party.objects.filter(name=name).exists():
            raise ValidationError("There can`t be two parties with the same name")

        return name

    def clean_existing_party_name(self):
        existing_party_name = self.cleaned_data.get('existing_party_name')
        if not Party.objects.filter(name=existing_party_name).exists():
            raise ValidationError("There no party with name {0}".format(existing_party_name))

        return existing_party_name

    def save(self, commit=True):
        name = self.cleaned_data.get('name')
        existing_party_name = self.cleaned_data.get('existing_party_name')

        ps = PartyService()
        existing_party = ps.get(name=existing_party_name)
        creator = ProfileService().get(id=self.user.id)
        members = ps.get_party_profiles(existing_party, excluding={'id': creator.id})

        return ps.create(name=name, creator=creator, members=members)


class AddMemberToPartyForm(forms.Form):
    info = forms.CharField(max_length=1024, label='Username', widget=widgets.TextInput(
        attrs={'placeholder': 'Enter here username'}))


class CreateTemplateForm(CreatePartyForm):
    food = forms.ModelMultipleChoiceField(queryset=Food.objects.all())

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if TemplatePartyService().filter(name=name).exists():
            raise ValidationError("Template with such name already exists")

        return name

    def save(self, commit=True) -> TemplateParty:
        name = self.cleaned_data.get('name')
        members = self.cleaned_data.get('members')
        food = self.cleaned_data.get('food')

        creator = ProfileService().get(id=self.user.id)
        return TemplatePartyService().create(name=name,
                                             creator=creator,
                                             members=members,
                                             food=food)


class AddFoodToPartyForm(forms.ModelForm):
    class Meta:
        model = OrderedFood
        fields = ('__all__')

    def save(self, commit=True):
        name = self.cleaned_data.get('name')
        price = self.cleaned_data.get('price')
        quantity = self.cleaned_data.get('name')
