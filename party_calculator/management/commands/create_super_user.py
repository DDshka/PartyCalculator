"""
Management utility to create superusers.
"""
from django.contrib.auth.management.commands.createsuperuser \
    import Command as CreateSuperUserCommand

from party_calculator_auth.models import Profile


class Command(CreateSuperUserCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = Profile
        self.username_field = self.UserModel._meta.get_field(self.UserModel.USERNAME_FIELD)