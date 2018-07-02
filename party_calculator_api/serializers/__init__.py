from rest_framework import serializers

from party_calculator_auth.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'username', 'age', 'gender', 'member_of')