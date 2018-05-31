from django.conf.urls import url

from authModule.views import LoginView, SignInView, LogoutView

urlpatterns = [
  url(r'^login$', LoginView.as_view(),
      name='login'),

  url(r'^logout$', LogoutView.as_view(),
      name='logout'),

  url(r'^signIn$', SignInView.as_view(),
      name='sign-in'),
]
