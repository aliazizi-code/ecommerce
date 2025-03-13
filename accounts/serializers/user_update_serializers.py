from rest_framework import serializers
from accounts.models import UserProfile, User

from utils import CacheManager
from accounts.otp import verify_otp_change_email


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']


class ChangeEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address already exists.")
        return value


class ChangeEmailVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField(required=True)

    def validate_email(self, value):
        user = self.context['request'].user
        cached_email = CacheManager.get_value(user.id, "new_email")

        if cached_email is None:
            raise serializers.ValidationError("No email found in the cache. Please request a new email verification.")

        if cached_email != value:
            raise serializers.ValidationError("The provided email does not match the cached email.")
        
        return value

    def validate_otp(self, value):
        user_id = self.context['user_id']

        if not verify_otp_change_email(user_id, value):
            raise serializers.ValidationError("Invalid OTP provided. Please try again.")
