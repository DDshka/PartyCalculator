from django.conf.urls import url

from party_calculator_auth.views import LoginView, SignInView, LogoutView, VerificationView

urlpatterns = [
    url(r'^login$', LoginView.as_view(),
        name=LoginView.name),

    url(r'^logout$', LogoutView.as_view(),
        name=LogoutView.name),

    url(r'^signIn$', SignInView.as_view(),
        name=SignInView.name),

    url(r'^activate/(?P<verification_code>[0-9a-f-]+$)', VerificationView.as_view(),
        name=VerificationView.name),
]
