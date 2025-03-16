from rest_framework import serializers
from accounts.models import UserProfile, User

from utils import CacheManager
from accounts.otp import verify_otp_change_email, verify_otp_change_number
from accounts.serializers import RequestOTPSerializer, VerifyOTPRequestSerializer


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']


class ChangeEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address already exists.")
        return value


class ChangeEmailVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField(required=True)

    def validate_email(self, value):
        user = self.context['request'].user
        cached_email = CacheManager.get_value(user.id, "new_email")
        print(f"{cached_email}")

        # if not cached_email:
        #     raise serializers.ValidationError("No email found in the cache. Please request a new email verification.")

        # if cached_email != value:
        #     raise serializers.ValidationError("The provided email does not match the cached email.")
        
        return value

    def validate_otp(self, value):
        user = self.context['request'].user

        if not verify_otp_change_email(user.id, value):
            raise serializers.ValidationError("Invalid OTP provided. Please try again.")
        return value


class ChangeNumberRequestSerializer(RequestOTPSerializer):
    def validate_number(self, value):
        super().validate_number(value)
        user = self.context['request'].user

        if User.objects.filter(number=value).exists():
            raise serializers.ValidationError("This phone number is already in use.")

        if user.number == value:
            raise serializers.ValidationError("You must provide a different phone number.")
        return value
          
        
class ChangeNumberVerifySerializer(VerifyOTPRequestSerializer):
    def validate_number(self, value):
        user = self.context['request'].user
        cached_number = CacheManager.get_value(user.id, "new_number")

        if cached_number is None:
            raise serializers.ValidationError("No number found in the cache. Please request a new number verification.")
        
        if cached_number != value:
            raise serializers.ValidationError("The provided number does not match the cached number.")
        
        return value
    
    def validate_otp(self, value):
        user = self.context['request'].user

        if not verify_otp_change_number(user.id, value):
            raise serializers.ValidationError("Invalid OTP provided. Please try again.")
        return value
