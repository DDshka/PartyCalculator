from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from authModule.models import Profile
from party_calculator.forms import CreatePartyForm
from party_calculator.models import Party


class HomeView(TemplateView):
  template_name = 'home.html'

  def get_context_data(self, **kwargs):
    context = {}
    if self.request.user.is_authenticated:
      user = Profile.objects.get(id=self.request.user.id)
      context['parties'] = user.membership_set.all()
      context['form'] = CreatePartyForm()

    return context


class CreatePartyView(View):
  def get(self, request):
    pass

  def post(self, request):
    form = CreatePartyForm(request.user, request.POST)
    if form.is_valid():
      form.save(False)