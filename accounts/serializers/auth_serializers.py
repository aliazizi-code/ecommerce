from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from accounts.models import User
from accounts.otp import verify_otp_auth


class PhoneNumberField(serializers.CharField):
    default_validators = [
        RegexValidator(
            regex=r'^\+98[0-9]{10}$',
            message="Phone number must be entered in the format: '+9891234567890'. Exactly 12 digits allowed."
        )
    ]


class RequestOTPSerializer(serializers.Serializer):
    number = PhoneNumberField(max_length=13)


class VerifyOTPRequestSerializer(serializers.Serializer):
    number = PhoneNumberField(max_length=13)
    otp = serializers.IntegerField(required=True)

    def validate_otp(self, value):
        number = self.initial_data.get('number')
        user = get_object_or_404(User, number=number)

        if not verify_otp_auth(user.id, value):
            raise serializers.ValidationError("Invalid OTP provided. Please try again.")
        return value


class BaseLoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        super().validate(attrs)
        password = attrs['password']
        user = self.get_user(attrs)

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")
        
        attrs['user'] = user
        return attrs

    def get_user(self, attrs):
        raise NotImplementedError("Subclasses must implement get_user method")


class EmailLoginSerializer(BaseLoginSerializer):
    email = serializers.EmailField(required=True)

    def get_user(self, attrs):
        email = attrs['email']
        return get_object_or_404(User, email=email)


class NumberLoginSerializer(BaseLoginSerializer):
    number = PhoneNumberField(max_length=13)

    def get_user(self, attrs):
        number = attrs['number']
        return get_object_or_404(User, number=number)
