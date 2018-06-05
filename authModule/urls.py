from django.conf.urls import url

from authModule.views import LoginView, SignInView, LogoutView, VerificationView

urlpatterns = [
  url(r'^login$', LoginView.as_view(),
      name='login'),

  url(r'^logout$', LogoutView.as_view(),
      name='logout'),

  url(r'^signIn$', SignInView.as_view(),
      name='sign-in'),

  url(r'^activate/(?P<verification_code>[0-9a-f-]+$)', VerificationView.as_view(),
      name='verification'),
]
